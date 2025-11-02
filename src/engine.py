import wx
import threading
import socket
import socketserver
import json
import queue
import os
import logging
import time

logger = logging.getLogger(__name__)

engine=None #placeholder

class GCodeRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        logger.info("TCP client connected: %s"%(self.client_address,))
        while engine.running.is_set():
            try:
                data = self.rfile.readline().strip().decode()
                #if not data:continue  # Ignore empty lines
                logger.info("TCP server received: %s"%data)
                # put commad as receive message so gcode window can show it
                engine.queue.put(("response", {"sub":"gcode","params":{"TCP":self.client_address,"command":data}}, None))
                def callback(response):
                    try:
                        if "output" in response:
                            output = "\n".join(response["output"]) + "\n"
                        else:
                            output = json.dumps(response) + "\n"
                        self.wfile.write(output.encode())
                        self.wfile.flush()
                    except socket.error as e:
                        logger.error("TCP server send error: %s"%e)
                engine.queue.put(("command", {"method": "gcode/session", "params": {"command": data}}, callback))
            except socket.error as e:
                logger.error("TCP server read error: %s"%e)
                break
        logger.info("TCP client disconnected: %s"%(self.client_address,))

def start_tcp_server(server_address):
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer(server_address, 
                        GCodeRequestHandler)
    logger.info("Starting TCP server on %s"%(server_address,))
    server.serve_forever()

class Engine:
    def __init__(self, socket_path="/tmp/pick_socket"):
        global engine
        engine=self
        self.socket_path = socket_path
        self.socket = None
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = threading.Event()
        self.connected = threading.Event()
        self.pending_requests = {}
        self.subscribed_objects={
             "webhooks": None 
            ,"toolhead": ["position"]
            ,"system_stats": ["sysload","memavail"]
            ,"temperature_sensor mcu_temp": ['temperature']
            ,"temperature_sensor toolhead_temp": ['temperature']
            }
        self.subscribers=[]
        self.gcode_sub_callback=None
        self.connected.clear()
        self.running.set()
        self.request_id = 0  # Sequential request ID
        self.server = None
        self.log_handler = None  # Set by App

    def set_log_handler(self, handler):
        self.log_handler = handler
        logger.addHandler(handler)

    def connect(self):
        retry_delay = 10  # seconds
        while True:
            try:
                logger.info("Attempting to connect to Unix socket at %s"%(self.socket_path))
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.socket_path)
                logger.info("Connected to Unix socket")
                self.queue.put(("socket_open", None, None))
                break
            except socket.error as e:
                logger.error("Failed to connect: %s"%e)
                time.sleep(retry_delay)

    def send_command(self, method, params, callback=None):
        with self.lock:
            self.request_id += 1
            request_id = self.request_id
        request = {"id": request_id, "method": method}
        if params: request["params"] = params
        try:
            data = json.dumps(request).encode()
            with self.lock:
                self.socket.sendall(data + b'\x03')
            self.pending_requests[request_id] = request
            if callback:
                self.pending_requests[request_id]["callback"] = callback
            logger.info("send_command: %s" % data)
        except socket.error as e:
            logger.error("Failed to send command: %s."%e)
            self.connected.clear()
            self.socket.close()
            self.queue.put(("socket_closed", None, None))

    def subscribe_gcode(self,callback):
        self.gcode_sub_callback=callback
        if self.connected.is_set(): self.queue.put(("command", {"method": "gcode/subscribe_output", "params": {"response_template":{"sub": "gcode"}}},self.gcode_sub_callback))

    def subscribe_objects(self):
        self.queue.put(( "command",
            {"method": "objects/subscribe", 
            "params": {"response_template": {"sub": "objects"}, 
                       "objects": self.subscribed_objects}},
            self.process_object_subs))
    def process_object_subs(self,payload):
        for callback in self.subscribers:
            #logger.info("process_object_subs %s %s"%(callback,payload))
            callback(payload)

    def socket_reader(self):
        buffer = b""
        logger.warning("Attempting to connect...")
        self.connect()
        self.connected.set()
        while self.running.is_set():
            try:
                data = self.socket.recv(4096)
                if not data:
                    logger.warning("Socket closed...")
                    self.connected.clear()
                    self.socket.close()
                    self.queue.put(("socket_closed", None, None))
                    break
                buffer += data
                while b'\x03' in buffer:
                    message, buffer = buffer.split(b'\x03', 1)
                    try:
                        payload = json.loads(message.decode())
                        self.queue.put(("response", payload, None))
                        # logger.debug("Received raw message: %s"%payload)
                    except UnicodeDecodeError as e:
                        logger.error("Failed to decode message: %s %s"%(e,message))
            except socket.error as e:
                logger.error("Socket error: %s."%e)
                self.connected.clear()
                self.socket.close()
                self.queue.put(("socket_closed", None, None))
                break

    def command_processor(self):
        while self.running.is_set():
            try: msg_type, data, callback = self.queue.get(timeout=30.0)
            except queue.Empty: continue
            if msg_type == "socket_closed":
                logger.info("socket_close event: Starting Reader")
                threading.Thread(target=self.socket_reader, daemon=True).start()
                with self.lock:
                    # Clear pending requests on disconnect
                    self.pending_requests.clear()  
            elif msg_type == "socket_open":
                logger.info("Recreating subscriptions.")
                self.subscribe_gcode(self.gcode_sub_callback)
                self.subscribe_objects()
            elif msg_type == "command":
                if self.connected.is_set(): self.send_command(data["method"], data.get("params", {}), callback)
                else: logger.info("not connected, discarding %s"%((msg_type, data, callback),))
            elif msg_type == "response":
                request_id = data.get("id")
                if request_id is not None:# Handle regular response with id
                    with self.lock:
                        if request_id in self.pending_requests:
                            request = self.pending_requests.pop(request_id)
                            response = data.get("result", data.get("error","No result or error"))
                            logger.info("Received response for %s: %s"%(request['method'],response))
                            if request.get("callback"):
                                wx.CallAfter(request["callback"], response)
                else:# Handle subscription message (no id, has subscription)
                    # logger.debug("Sub raw %s"%(data))
                    sub=data.get("sub","unset")
                    payload=data.get("params", {})
                    match sub:
                        case "gcode": self.gcode_sub_callback(payload)
                        case "objects": wx.CallAfter(self.process_object_subs,payload)
                        case _ : logger.warning("bogus sub; %s: %s"%(sub,payload))
            # except Exception as e:
            #     logger.error("Error in command processor: %s"%e)

    def start(self):
        self.queue.put(("socket_closed", None, None)) #put event to start connecting
        threading.Thread(target=self.command_processor, daemon=True).start()
        logger.info("Engine started")

    def stop(self):
        self.running.clear()
        if self.socket:
            try:
                self.socket.close()
            except socket.error as e:
                logger.error("Error closing Unix socket: %s"%e)
        if self.server:
            try:
                self.server.server_close()
                logger.info("TCP server closed")
            except Exception as e:
                logger.error("Error closing TCP server: %s"%e)
        logger.info("Engine stopped")

# engine=Engine()

# def start(socket_path):
#     global engine
#     engine=Engine(socket_path)