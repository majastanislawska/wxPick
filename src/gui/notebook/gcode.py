import wx
import src.engine
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Gcode"
panel = None
pane = None
paneinfo=None
parent=None

gcode_display=None
gcmd_input=None
send_button=None
auto_completion_entries=[]

coloring_rules = { #just stub
    "G0": "green",
    "G1": "green",
    "M114": "blue",
    "ERROR": "red",
    "Error": "red",
    "ok": "green", 
    "//": "purple",
    "Disconnect": "red"
}

# class MyClassCompleter(wx.TextCompleter):
#     def __init__(self):
#         wx.TextCompleter.__init__(self)
#         self._iLastReturned = wx.NOT_FOUND
#         self._sPrefix = ''
#         logger.info("MyCompleter init")

#     def Start(self, prefix):
#         self._sPrefix = prefix.lower()
#         self._iLastReturned = wx.NOT_FOUND
#         logger.info("Completer.Start: %s"%(self._sPrefix))
#         for item in auto_completion_entries:
#             if item.lower().startswith(self._sPrefix):
#                 return True
#         # Nothing found
#         return False
#     def GetNext(self):
#         for i in range(self._iLastReturned+1, len(auto_completion_entries)):
#             if auto_completion_entries[i].lower().startswith(self._sPrefix):
#                 self._iLastReturned = i
#                 return auto_completion_entries[i]
#          # No more corresponding item
#         return ''

# class MyTextCompleter(wx.TextCompleterSimple):
#     def __init__(self):
#         wx.TextCompleterSimple.__init__(self)
#     def GetCompletions(self, prefix):
#         res=[]
#         text = prefix.lower()
#         for entry in auto_completion_entries:
#             if entry.strip().lower().startswith(text):
#                 res.append(entry)
#         logger.debug("GetCompletions: %s %s"%(text,res))
#         return res
    
def create(notebook):
    global name,panel, pane, paneinfo, parent
    global gcode_display,gcmd_input,send_button
    parent=notebook
    panel = wx.Panel(notebook, 
        wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 
        wx.TAB_TRAVERSAL )
    sizer = wx.BoxSizer( wx.VERTICAL )
    gcode_display = wx.TextCtrl(panel, 
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
    gcode_display.SetFont(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    sizer.Add(wx.StaticText(panel, label="GCode Output:"), 0, wx.ALL, 5)
    sizer.Add(gcode_display, 1, wx.EXPAND | wx.ALL, 5)
    gcmd_sizer = wx.BoxSizer(wx.HORIZONTAL)
    gcmd_sizer.Add(wx.StaticText(panel, label="Command:"), flag=wx.ALIGN_CENTER_VERTICAL)
    gcmd_input = wx.TextCtrl(panel, value=wx.EmptyString, style=wx.TE_PROCESS_ENTER)
    # gcmd_input.SetToolTip("On MacOS press F5 for autocompletion")
    # gcmd_input.AutoComplete(MyTextCompleter())
    #gcmd_input.AutoComplete(MyClassCompleter())
    gcmd_sizer.Add(gcmd_input, 1, wx.EXPAND | wx.ALL, 1)
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

# for autocomplete
# def get_gcodes(data):
#     logger.debug("get_gcodes: %s"%data)
#     if not 'status' in data: return
#     if not 'gcode' in data['status']: return
#     if not 'commands' in data['status']['gcode']: return
#     for gcode in sorted(data['status']['gcode']['commands'].keys()):
#         logger.debug("get_gcodes: %s"%gcode)
#         auto_completion_entries.append(gcode)

def _append(message):
    gcode_display.SetDefaultStyle(wx.TextAttr(wx.Colour("black")))
    gcode_display.AppendText(f"\n{message}")
    pos = gcode_display.GetInsertionPoint() - len(message) - 1
    for keyword, color in coloring_rules.items():
        start = 0
        while True:
            start = message.find(keyword, start)
            if start == -1: break
            end = start + len(keyword)+1
            gcode_display.SetStyle(pos + start, pos + end, wx.TextAttr(wx.Colour(color)))
            start += 1
    gcode_display.ScrollLines(1)

def on_gcode_sub(data):
    logger.debug("on_gcode_sub: %s"%data)
    message = data['response'] if 'response' in data else str(data)
    wx.CallAfter(_append,message)

def send_gcode(event):
    command = gcmd_input.GetValue().strip()
    if command:
        logger.info("Sending GCode: %s" % command)
        src.engine.engine.queue.put(("command", 
                {"method": "gcode/script", "params": {"script": command}}, None))
        gcmd_input.Clear()
        event.Skip()
        wx.CallAfter(_append,command)

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