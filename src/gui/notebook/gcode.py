import wx
import wx.stc
import src.engine
import src.app
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Console"
app:src.app.App = None
panel = None
pane = None
paneinfo=None
parent=None

gcode_display=None
gcmd_input=None
send_button=None
servos=[] 
pins=[]
pin_templates=[] 
macros=[]
fans=[]
leds=[]
manual_steppers=[] 
steppers=[]
pumps=[]
valves=[]
temperature_sensors=[]
accelerometers=[]
extruders=[]
heaters=[]
delayed_gcode=[]
tmcs=[]
auto_completion_entries={
    'FIRMWARE_RESTART': None, 'RESTART': None,'HELP': None, 'GET_POSITION': None,'STATUS': None, 
    'RESPOND': {'TYPE':['echo','echo_no_space','command','error'],'PREFIX': None, 'MSG':None}, 
    'ECHO': None, 
    'SET_GCODE_VARIABLE': {'MACRO': macros, 'VARIABLE': None, 'VALUE': None},
    'SET_GCODE_OFFSET': {'X': None, 'X_ADJUST': None, 'Y': None, 'Y_ADJUST': None, 'Z': None, 'Z_ADJUST': None, 'MOVE=1': None, 'MOVE_SPEED': None},
    'SAVE_GCODE_STATE': {'NAME': None},
    'RESTORE_GCODE_STATE': {'NAME': None, 'MOVE': None, 'MOVE_SPEED': None},
    'G0': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'E': None, 'F': None},
    'G1': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'E': None, 'F': None},
    'G2': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'E': None, 'F': None, 'I': None, 'J': None, 'K': None}, # (Clockwise Arc) 
    'G3': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'E': None, 'F': None, 'I': None, 'J': None, 'K': None}, # (Counterclockwise Arc)
    'G4': {'P': None}, #Dwell
    'G17': None,'G18': None,'G19': None, #Arc Plane Select:
    'G20': None,'G21': None, #Units (Inches vs Millimeters)
    'G28': {'X': None, 'Y': None, 'Z': None}, #home
    'G90': None,'G91': None, #Absolute vs Relative Positioning
    'G92': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'E': None}, #Set position
    'M18': None, 'M84': None, #Disable steppers
    'M73': {'S': None}, #Set build percentage
    'M82': None,'M83': None, #Extruder absolute mode vs relative mode
    'M104': {'T': None,'S': None}, 'M109': {'T': None,'S': None}, #Set extruder temperature
    'M105': None, #Get extruder temperature
    'M106': {'S': None},'M107': None, #fan on/off
    'M110': {'N': None}, #Set line number
    'M112': None, #Emergency stop
    'M114': None, #Get current position:
    'M115': None, #Get firmware version
    'M117': None,'M118': None,'M119': None,
    'M140': {'S': None},'M190': {'S': None}, #Set bed temperature and wait for bed temperature
    'M204': {'S': None, 'P': None, 'T': None}, #Set acceleration (default, print, travel)
    'M220': {'S': None},'M221': {'S': None}, #Set speed factor override percentage and flow factor override percentage
    'M400': None, #Finish all moves
    'SAVE_CONFIG': None,
    'UPDATE_DELAYED_GCODE': {'ID': delayed_gcode, 'DURATION': None},
    'SET_DISPLAY_GROUP': {'GROUP': None,'DISPLAY': None},
    'SET_PIN': {'PIN': pins,'VALUE': None, 'TEMPLATE': pin_templates, 'CYCLE_TIME': None}, 
    'SET_SERVO': {'SERVO': servos, 'ANGLE': None,'WIDTH': None,},
    'SET_FAN_SPEED':{'FAN':fans, 'SPEED': None, 'TEMPLATE': pin_templates,}, 
    'SET_LED ':{'LED': leds, 'RED': None, 'GREEN': None, 'BLUE': None, 'WHITE': None, 'INDEX': None, 'TRANSMIT=0': None, 'SYNC=1': None},
    'SET_LED_TEMPLATE ':{'LED': leds, 'TEMPLATE': pin_templates, 'INDEX': None},
    'SET_DISPLAY_TEXT ':{'MSG': None}, #M117 equivalent
    'MANUAL_STEPPER': {'STEPPER': manual_steppers, 'ENABLE': None, 'SET_POSITION': None, 'SPEED': None, 'ACCEL': None, 'MOVE': None, 'SYNC': None, 'STOP_ON_ENDSTOP': None}, 
    'STEPPER_BUZZ': {'STEPPER': steppers},
    'FORCE_MOVE': {'STEPPER': steppers, 'DISTANCE': None, 'VELOCITY': None, 'ACCEL': None},
    'SET_KINEMATIC_POSITION': {'X': None, 'Y': None, 'Z': None, 'A': None,'B': None, 'SET_HOMED':['X','Y','Z'], 'CLEAR_HOMED':['X','Y','Z']}, 
    'SET_VELOCITY_LIMIT': {'VELOCITY': None, 'ACCEL': None, 'MINIMUM_CRUISE_RATIO': None, 'SQUARE_CORNER_VELOCITY': None},
    'QUERY_ADC': {'NAME': None, 'PULLUP': None},
    'QUERY_ENDSTOPS': None,
    'MEASURE_AXES_NOISE': None,
    'TEST_RESONANCES': {'AXIS': ['X','Y','Z'], 'OUTPUT': ['resonances','raw_data'], 'NAME': None, 'FREQ_START': None, 'FREQ_END': None, 'ACCEL_PER_HZ': None, 'HZ_PER_SEC': None, 'CHIPS': None, 'POINT': None, 'INPUT_SHAPING': None},
    'SHAPER_CALIBRATE': {'AXIS': ['X','Y','Z'],'NAME': None, 'FREQ_START': None, 'FREQ_END': None, 'ACCEL_PER_HZ': None, 'HZ_PER_SEC': None, 'CHIPS': None, 'MAX_SMOOTHING': None, 'INPUT_SHAPING': None},
    'SET_PUMP_PRESSURE': {'PUMP': pumps, 'TARGET': None},
    'TURN_OFF_PUMPS': None, 'VAC': None, 
    'VALVE_GET': {'VALVE': valves},
    'VALVE_SET': {'VALVE': valves, 'VALUE': None},
    'PD_CAPS': {'MCU': None},'PD_GET': {'MCU': None},'PD_SET': {'MCU': None,'VOLTAGE': None,'MODE': ['FIXED', 'PPS', 'AVS']}, #power delivery extension
    'SET_LED_EFFECT': {'EFFECT': None}, 'STOP_LED_EFFECTS': None,#led effect extension
    #[adxl345]
    'ACCELEROMETER_MEASURE': {'CHIP': accelerometers, 'NAME':None},
    'ACCELEROMETER_QUERY': {'CHIP': accelerometers, 'RATE':None},
    'ACCELEROMETER_DEBUG_READ': {'CHIP': accelerometers, 'REG':None},
    'ACCELEROMETER_DEBUG_WRITE': {'CHIP': accelerometers, 'REG':None, 'VAL':None},
    #[angle] 'ANGLE_CALIBRATE': None,'ANGLE_CHIP_CALIBRATE': None,'ANGLE_DEBUG_READ': None,'ANGLE_DEBUG_WRITE': None,
    #[axis_twist_compensation] 'AXIS_TWIST_COMPENSATION_CALIBRATE': None,
    #[bed_mesh] 'BED_MESH_CALIBRATE': None,'BED_MESH_OUTPUT': None,'BED_MESH_MAP': None,'BED_MESH_CLEAR': None,'BED_MESH_PROFILE': None,'BED_MESH_OFFSET': None
    #[bed_screws] 'BED_SCREWS_ADJUST': None,
    #[bed_tilt] 'BED_TILT_CALIBRATE': None,
    #[bltouch] 'BLTOUCH_DEBUG': None,'BLTOUCH_STORE': None,
    #[delta_calibrate] 'DELTA_CALIBRATE': None,'DELTA_ANALYZE': None
    #[dual_carriage] 'SET_DUAL_CARRIAGE': None,'SAVE_DUAL_CARRIAGE_STATE': None,'RESTORE_DUAL_CARRIAGE_STATE': None,
    #[endstop_phase] 'ENDSTOP_PHASE_CALIBRATE': None,
    #[exclude_object] 'EXCLUDE_OBJECT': None,'EXCLUDE_OBJECT_DEFINE': None,'EXCLUDE_OBJECT_START': None,'EXCLUDE_OBJECT_END': None,
    #[extruder]
    'ACTIVATE_EXTRUDER': {'EXTRUDER': extruders},
    'SET_PRESSURE_ADVANCE':  {'EXTRUDER': extruders,'ADVANCE': None,'SMOOTH_TIME': None},
    'SET_EXTRUDER_ROTATION_DISTANCE': {'EXTRUDER': extruders,'DISTANCE': None},
    'SYNC_EXTRUDER_MOTION': {'EXTRUDER': extruders,'MOTION_QUEUE': None},
    #[filament_switch_sensor] 'QUERY_FILAMENT_SENSOR': None,'SET_FILAMENT_SENSOR': None
    #[firmware_retraction]
    # 'SET_RETRACTION', 'GET_RETRACTION',
    #[gcode_arcs]
    #[generic_cartesian] 'SET_STEPPER_CARRIAGES': None,
    #[hall_filament_width_sensor]'QUERY_FILAMENT_WIDTH': None,'RESET_FILAMENT_WIDTH_SENSOR': None,'DISABLE_FILAMENT_WIDTH_SENSOR': None,'ENABLE_FILAMENT_WIDTH_SENSOR': None,'QUERY_RAW_FILAMENT_WIDTH': None,'ENABLE_FILAMENT_WIDTH_LOG': None,'DISABLE_FILAMENT_WIDTH_LOG': None,
    #[heaters]
    'TURN_OFF_HEATERS': None,
    'TEMPERATURE_WAIT': {'SENSOR': heaters, 'MINIMUM': None, 'MAXIMUM': None},
    'SET_HEATER_TEMPERATURE': { 'SENSOR': heaters, 'TARGET': None},
    #[idle_timeout]
    'SET_IDLE_TIMEOUT': {'TIMEOUT': None},
    #[input_shaper]
    # 'SET_INPUT_SHAPER',
    #[load_cell] 'LOAD_CELL_DIAGNOSTIC': None,'LOAD_CELL_CALIBRATE': None,'LOAD_CELL_TARE': None,'LOAD_CELL_READ': None #load_cell='name'
    #[load_cell_probe] 'LOAD_CELL_TEST_TAP': None
    #[manual_probe] 
    # 'MANUAL_PROBE','Z_ENDSTOP_CALIBRATE','Z_OFFSET_APPLY_ENDSTOP',
    #[mcp4018] 'SET_DIGIPOT': None
    #[palette2]'PALETTE_CONNECT': None,'PALETTE_DISCONNECT': None,'PALETTE_CLEAR': None,'PALETTE_CUT': None,'PALETTE_SMART_LOAD': None,
    #[pause_resume]
    'PAUSE': None,'RESUME': {'VELOCITY': None},'CLEAR_PAUSE': None,'CANCEL_PRINT': None,
    #[pid_calibrate] 'PID_CALIBRATE': None,
    #[print_stats] 'SET_PRINT_STATS_INFO': None,
    #[probe] 'PROBE': None,'QUERY_PROBE': None,'PROBE_ACCURACY': None,'PROBE_CALIBRATE': None,'Z_OFFSET_APPLY_PROBE': None
    #[probe_eddy_current] 'PROBE_EDDY_CURRENT_CALIBRATE': None,'LDC_CALIBRATE_DRIVE_CURRENT': None,
    #[quad_gantry_level] 'QUAD_GANTRY_LEVEL': None
    #[save_variables]
    'SAVE_VARIABLE': {'VARIABLE': None, 'VALUE': None},
    #[screws_tilt_adjust]'SCREWS_TILT_CALCULATE': None,
    #[sdcard_loop] 'SDCARD_LOOP_BEGIN': None,'SDCARD_LOOP_END': None,'SDCARD_LOOP_DESIST': None,
    #[skew_correction] 'SET_SKEW': None,'GET_CURRENT_SKEW': None,'CALC_MEASURED_SKEW': None,'SKEW_PROFILE': None
    #[smart_effector] 'SET_SMART_EFFECTOR': None,'RESET_SMART_EFFECTOR': None
    #[stepper_enable]
    'SET_STEPPER_ENABLE': {'STEPPER': steppers, 'ENABLE':['0','1']},
    #[temperature_fan] 'SET_TEMPERATURE_FAN_TARGET': None,
    #[temperature_probe]'TEMPERATURE_PROBE_CALIBRATE': None,'TEMPERATURE_PROBE_NEXT': None,'TEMPERATURE_PROBE_COMPLETE': None,'ABORT': None,'TEMPERATURE_PROBE_ENABLE': None
    #[tmcXXXX]
    'DUMP_TMC': {'STEPPER': tmcs,'REGISTER': None},
    'INIT_TMC': {'STEPPER': tmcs},
    'SET_TMC_CURRENT': {'STEPPER': tmcs,'CURRENT': None, 'HOLD_CURRENT': None},
    'SET_TMC_FIELD': {'STEPPER': tmcs,'FIELD': None, 'VALUE': None, 'VELOCITY': None},
    #[tuning_tower] 'TUNING_TOWER': None,
    #[virtual_sdcard] 'SDCARD_PRINT_FILE': None,'SDCARD_RESET_FILE': None
    #[z_thermal_adjust] 'SET_Z_THERMAL_ADJUST': None
    #[z_tilt] 'Z_TILT_ADJUST': None,
}


def create(notebook):
    global name,panel, pane, paneinfo, parent
    global gcode_display,gcmd_input,send_button
    parent=notebook
    panel = wx.Panel(notebook, 
        wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 
        wx.TAB_TRAVERSAL )
    sizer = wx.BoxSizer( wx.VERTICAL )
    gcode_display= wx.stc.StyledTextCtrl(panel)
    sizer.Add(wx.StaticText(panel, label="GCode Output:"), 0, wx.ALL, 5)
    _setup_gcode_styling(gcode_display)
    gcode_display.SetReadOnly(True)
    gcode_display.Bind(wx.stc.EVT_STC_STYLENEEDED, onStyleNeeded)
    sizer.Add(gcode_display, 1, wx.EXPAND | wx.ALL, 5)
    gcmd_sizer = wx.BoxSizer(wx.HORIZONTAL)
    gcmd_input = wx.stc.StyledTextCtrl(panel)
    _setup_gcode_styling(gcmd_input)
    gcmd_input.AutoCompSetIgnoreCase(True)
    gcmd_input.AutoCompSetAutoHide(True)
    gcmd_input.Bind(wx.stc.EVT_STC_CHARADDED, _on_char_added)
    gcmd_input.SetMinSize((-1, 60)) # Height for ~3-4 lines
    gcmd_sizer.Add(gcmd_input, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)
    send_button = wx.Button(panel, label="Send")
    gcmd_sizer.Add(send_button, 0, wx.ALL, 1)
    sizer.Add(gcmd_sizer, 0, wx.EXPAND | wx.ALL, 1)
    # sizer.Add(wx.StaticText(panel, label="On MacOS press F5 for autocompletion"), 0, wx.ALL, 5)
    panel.SetSizer(sizer)
    panel.Layout()
    notebook.AddPage(panel, u"Console", False)
    src.engine.engine.subscribe_gcode(on_gcode_sub)
    send_button.Bind(wx.EVT_BUTTON, send_gcode)
    gcmd_input.Bind( wx.EVT_TEXT_ENTER, send_gcode)
    src.engine.engine.register_on_connect("objects/query", {"objects": {'configfile': None}}, parse_config)

def parse_config(response):
    global servos, pins, pin_templates, macros, fans, leds, manual_steppers, steppers, pumps, valves, temperature_sensors, accelerometers, extruders, heaters, delayed_gcode, tmcs
    if not "status" in response:
        logger.error("Config scan failed: %s"%(response,))
        return
    for i in [servos, pins, pin_templates, macros, fans, leds, manual_steppers, steppers, pumps, valves, temperature_sensors, accelerometers, extruders, heaters, delayed_gcode, tmcs]:
        i.clear()
    config = response['status']['configfile']['config']
    for item in config.keys():
        if item.startswith("servo"):  servos.append(item[6:])
        elif item.startswith("output_pin"): pins.append(item[11:])
        elif item.startswith("display_template"): pin_templates.append(item[17:])
        elif item.startswith("gcode_macro"): macros.append(item[12:])
        elif item.startswith("fan_generic"): fans.append(item[12:])
        elif item.startswith("neopixel"): leds.append(item[9:])
        elif item.startswith("led"): leds.append(item[4:])
        elif item.startswith("manual_stepper"): manual_steppers.append(item[15:])
        elif item.startswith("stepper"): steppers.append(item)
        elif item.startswith("pressure_pump"): pumps.append(item[14:])
        elif item.startswith("pressure_valve"): valves.append(item[15:])
        elif item.startswith("temperature_sensor"): temperature_sensors.append(item[19:])
        elif item.startswith("adxl345"): accelerometers.append(item[8:])
        elif item.startswith("icm20948"):accelerometers.append(item[11:])
        elif item.startswith("lis2dw"):  accelerometers.append(item[8:])
        elif item.startswith("lis3dh"):  accelerometers.append(item[8:])
        elif item.startswith("bmi160"):  accelerometers.append(item[7:])
        elif item.startswith("mpu9250"): accelerometers.append(item[8:])
        elif item.startswith("extruder"): extruders.append(item[9:])
        elif item.startswith("heater"): heaters.append(item[7:])
        elif item.startswith("delayed_gcode"): delayed_gcode.append(item[13:])
        elif item.startswith("tmc2209"): tmcs.append(item[8:])
        elif item.startswith("tmc2208"): tmcs.append(item[8:])
        elif item.startswith('pca9685'): continue
        elif item.startswith('ch224q_pd'): continue
        elif item.startswith('display'): continue
        elif item.startswith('board_pins'): continue
        elif item in ['printer','idle_timeout', 'save_variables', 'pneumatics','force_move',
            'respond','resonance_tester']: continue
        else:
            logger.info("Config scan: %s %s"%(item, config[item]))
    for macro in macros:
        if macro.upper() not in auto_completion_entries.keys():
            auto_completion_entries[macro.upper()] = None

# Define style IDs
STYLE_DEFAULT = 0
STYLE_OK= 1   # OK
STYLE_ERROR = 2   #Error
STYLE_GCODECOMMENT = 3   # (Comment) or ; Comment
STYLE_KLIPPERCOMMENT = 4   # // Comment
STYLE_COMMAND = 5   # G, M
STYLE_REMOTE_COMMAND = 6  # Commands sent from other sources (e.g. TCP) than the input field

def _setup_gcode_styling(ctrl:wx.stc.StyledTextCtrl):
    ctrl.SetLexer(wx.stc.STC_LEX_CONTAINER)
    font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
    ctrl.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, font)
    ctrl.SetWrapMode(wx.stc.STC_WRAP_WORD)            # Enable line wrap
    ctrl.SetEndAtLastLine(True)                    # Don't scroll past last line
    ctrl.SetUseHorizontalScrollBar(False)          # Disable Horizontal
    ctrl.SetUseVerticalScrollBar(True)             # Enable Vertical
    ctrl.SetMarginWidth(1, 0)
    # ctrl.SetMarginWidth(0, 35) # Line numbers
    ctrl.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
    ctrl.StyleSetForeground(STYLE_OK, wx.Colour(0, 255, 0))   # Green
    ctrl.StyleSetForeground(STYLE_COMMAND, wx.Colour(0, 0, 255))   # Blue
    ctrl.StyleSetForeground(STYLE_REMOTE_COMMAND, wx.Colour(0, 0, 0))
    ctrl.MarkerDefine(STYLE_REMOTE_COMMAND, wx.stc.STC_MARK_BACKGROUND, background=wx.Colour(200,200,255)) # Light Blue
    ctrl.StyleSetForeground(STYLE_GCODECOMMENT, wx.Colour(0, 128, 0))   # Green
    ctrl.StyleSetForeground(STYLE_ERROR, wx.Colour(0, 0, 0))   # black
    # ctrl.IndicatorSetStyle(STYLE_ERROR, wx.stc.STC_INDIC_ROUNDBOX)
    # ctrl.IndicatorSetForeground(STYLE_ERROR, wx.Colour(0, 120, 215, 100)) # Transparent
    ctrl.MarkerDefine(STYLE_ERROR, wx.stc.STC_MARK_BACKGROUND, background=wx.Colour(255, 200, 200))
    ctrl.StyleSetForeground(STYLE_GCODECOMMENT, wx.Colour(100, 100, 100)) # Grey
    ctrl.StyleSetItalic(STYLE_GCODECOMMENT, True)
    ctrl.StyleSetForeground(STYLE_KLIPPERCOMMENT, wx.Colour(85, 107, 47)) # Dark Olive Green
    ctrl.StyleSetItalic(STYLE_KLIPPERCOMMENT, True)

def onStyleNeeded( event):
    end_pos = event.GetPosition()
    ctrl = event.GetEventObject()
    start_pos = ctrl.GetEndStyled()
    text = ctrl.GetTextRange(start_pos, end_pos)
    # logger.info("Styling needed from %d to %d %s"%(start_pos,end_pos,repr(text)))
    ctrl.StartStyling(start_pos)
    ctrl.SetStyling(end_pos - start_pos, STYLE_DEFAULT)

def get_completion_list(stc):
    pos = stc.GetCurrentPos()
    line = stc.GetCurLine()[0]  # current line text
    line_pos = stc.GetColumn(pos)  # position within the line
    tokens = line[:line_pos].split()   # only up to caret
    # logger.info("get_completion_list: tokens=%s"%tokens)
    if not tokens:
        return list(auto_completion_entries.keys())  # top level commands
    cmd = tokens[0].upper()
    # logger.info("get_completion_list: cmd=%s"%cmd)
    if cmd not in auto_completion_entries:
        return [x for x in auto_completion_entries.keys() if x.startswith(cmd.upper())]  # not full command suggest autocommpleteions for top-level commands
    schema = auto_completion_entries[cmd]
    if schema is None:
        return []  # no params for this command
    used_params = {}
    for t in tokens[1:]:
        if '=' in t:
            k, v = t.split('=', 1)
            used_params[k.upper()] = v
    # logger.info("get_completion_list: schema= %s used_params=%s"%(schema, used_params))
    # Find the last incomplete token
    last_token = tokens[-1] if tokens else ""
    # logger.info("get_completion_list: last_token=%s"%last_token)
    if last_token.endswith('='):# or '=' in last_token:
        # We're in a value position
        param = last_token.split('=')[0].upper()
        if param in schema:
            info = schema[param]
            return info() if callable(schema[param]) else info
    # Fallback: suggest any unused params
    return [p for p in schema if p not in used_params]


def _on_char_added(event:wx.stc.StyledTextEvent):
    ctrl = event.GetEventObject()
    pos = ctrl.GetCurrentPos()
    start_pos = ctrl.WordStartPosition(pos, True)
    word = ctrl.GetTextRange(start_pos, pos)
    # key = event.GetKey()
    # if key == wx.WXK_TAB:# or (key == ord(' ') and event.ControlDown()):
    completions = get_completion_list(ctrl)
    if completions:
        ctrl.AutoCompShow(len(word), " ".join(completions))  # space-separated list
        return
    event.Skip()


def _append(text):
    # logger.info("Appending to GCode display: %s"%repr(text))
    gcode_display.SetReadOnly(False)
    # gcode_display.AppendText(f"\n{message}")
    start_line = gcode_display.GetLineCount() - 1
    gcode_display.AppendText(f"{text}\n")
    gcode_display.StartStyling(gcode_display.PositionFromLine(start_line))
    if text.startswith("ok"):
        gcode_display.SetStyling(len(text), STYLE_OK) 
    elif text.startswith("!!") or text.startswith("Error:"):
        gcode_display.SetStyling(len(text), STYLE_ERROR) 
        gcode_display.MarkerAdd(start_line, STYLE_ERROR) # Highlight the whole line red
    elif text.startswith("//"):
        gcode_display.SetStyling(len(text), STYLE_KLIPPERCOMMENT)  
    else:
         gcode_display.SetStyling(len(text), STYLE_DEFAULT)
    gcode_display.GotoPos(gcode_display.GetLength())
    gcode_display.SetReadOnly(True)

def append(text):
   for lines in text.splitlines():
       _append(lines)
def append_command(text, style):
    # logger.info("append_command: %s, %s"%(repr(text), style))
    gcode_display.SetReadOnly(False)
    start_pos = gcode_display.GetEndStyled()
    start_line = gcode_display.GetLineCount() - 1
    gcode_display.AppendText(f"{text}\n")
    gcode_display.StartStyling(start_pos)
    gcode_display.SetStyling(len(text), style) 
    gcode_display.MarkerAdd(start_line, style)

def on_gcode_sub(data):
    # logger.debug("on_gcode_sub: %s"%data)
    if 'response' in data: wx.CallAfter(append,data['response'])
    elif 'TCP' in data:    wx.CallAfter(append_command,data['command'],STYLE_REMOTE_COMMAND)
    else:                  wx.CallAfter(append,str(data))

def send_gcode(event):
    command = gcmd_input.GetValue().strip()
    if command:
        # logger.info("Sending GCode: %s" % command)
        src.engine.engine.queue.put(("command", 
                {"method": "gcode/script", "params": {"script": command}}, None))
        wx.CallAfter(append_command,command,STYLE_COMMAND)
    event.Skip()

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Gcode Notebook")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    is_checked = event.IsChecked()
    if is_checked: parent.AddPage(panel, name, select=True)
    else:
        page_index = parent.FindPage(panel)
        if page_index != wx.NOT_FOUND:
            parent.RemovePage(page_index)
