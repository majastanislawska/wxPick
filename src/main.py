import wx
try:
    import Cocoa
except ImportError: pass
import threading
import json
import logging
import src.engine
import src.app
import src.art

logger = logging.getLogger(__name__)
socket_path = "/tmp/pick_socket"
engine = src.engine.Engine(socket_path)

def console_input():
    while True:
        method = input("Enter method (e.g., info): ").strip()
        if method=="": continue
        params_input = input("Enter params as JSON (e.g., {}): ").strip()
        try:
            params = json.loads(params_input) if params_input else {}
            logger.info("Command from console: %s with params %s"%(
                    method,params))
            engine.queue.put(("command", 
                    {"method": method, "params": params}, None))
        except json.JSONDecodeError:
            logger.error("Invalid JSON for params, try again.")
        except EOFError:
            break

def main():
    wxPick = wx.App()
    wx.ArtProvider.Push(src.art.myArtProvider())
    frame = src.app.App(engine)
    frame.Show()
    try:
        Cocoa.NSApplication.sharedApplication()
        Cocoa.NSApp().activateIgnoringOtherApps_(True)
    except NameError: pass
    engine.start()
    tcpserver_thread=threading.Thread(
        target=src.engine.start_tcp_server, 
        args=(("localhost", 8888),), #tuple
        daemon=True)
    tcpserver_thread.start()
    console_thread = threading.Thread(
        target=console_input, daemon=True)
    console_thread.start()
    wxPick.MainLoop()