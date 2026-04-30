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
auto_completion_entries=[]

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
    # fetch all gcode commands for autocomplete
    #src.engine.engine.queue.put(("command", {"method": "gcode/help", "params": {}}, get_gcodes))
    #src.engine.engine.queue.put( ("command", {"method": "objects/query", "params": {"objects": {"gcode": None}}}, get_gcodes))

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

# for autocomplete
# def get_gcodes(data):
#     logger.debug("get_gcodes: %s"%data)
#     if not 'status' in data: return
#     if not 'gcode' in data['status']: return
#     if not 'commands' in data['status']['gcode']: return
#     for gcode in sorted(data['status']['gcode']['commands'].keys()):
#         logger.debug("get_gcodes: %s"%gcode)
#         auto_completion_entries.append(gcode)

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
