import wx
import wx.aui
import os
import re
import importlib
import logging
import src.gui #placeholder so plugins can load
logger = logging.getLogger(__name__)

notebook_plugins = []
panel_plugins = []
toolbar_plugins = []
graph_plugins = []

def load_plugins(app,package):
    pysearchre = re.compile('.py$', re.IGNORECASE)
    pluginfiles = filter(pysearchre.search,os.listdir(os.path.join(*package.split('.'))))
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    plugins = map(form_module, pluginfiles)
    # import parent module / namespace
    #importlib.import_module('src')
    modules = []
    for plugin in plugins:
        logger.info(f"Loading plugin {package}{plugin}")
        if not plugin.startswith('__'):
            module=importlib.import_module(plugin, package=package)
            module.app = app
            modules.append(module)
    return modules
class WxRichHandler(logging.Handler):
    def __init__(self, text_ctrl):
        super().__init__()
        self.text_ctrl = text_ctrl
        self.auto_scroll = True
        
    def emit(self, record):
        msg = self.format(record)
        color = self.get_color(record.levelno)
        wx.CallAfter(self._append_colored, msg, color)
    
    def get_color(self, levelno):
        colors = {
            logging.INFO: "black",
            logging.WARNING: "orange",
            logging.ERROR: "red", 
            logging.DEBUG: "gray"
        }
        return colors.get(levelno, "black")
    
    def _append_colored(self, msg, color):
        self.text_ctrl.SetDefaultStyle(wx.TextAttr(wx.Colour(color)))
        self.text_ctrl.AppendText(f"\n{msg}")
        if self.auto_scroll:
            self.text_ctrl.ScrollLines(1)
    
    def set_auto_scroll(self, enabled):
        self.auto_scroll = enabled

# def append_gcode_highlighted(text_ctrl, message):
#     def _safe_append():
#         text_ctrl.SetDefaultStyle(wx.TextAttr(wx.Colour("black")))
#         text_ctrl.AppendText(f"\n{message}")
#         # **THREAD-SAFE** HIGHLIGHTING
#         pos = text_ctrl.GetInsertionPoint() - len(message) - 1
#         for keyword, color in coloring_rules.items():
#             start = 0
#             while True:
#                 start = message.find(keyword, start)
#                 if start == -1: break
#                 end = start + len(keyword)
#                 text_ctrl.SetStyle(pos + start, pos + end, wx.TextAttr(wx.Colour(color)))
#                 start += 1
#         text_ctrl.ScrollLines(1)
#     wx.CallAfter(_safe_append)

# class FloatingFramme(wx.Frame):
#     def __init__(self, parent, title, size):
#         style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT |wx.FRAME_TOOL_WINDOW #| wx.STAY_ON_TOP  # Adjustable
#         super().__init__(parent, wx.ID_ANY, title, style=style, size=size)
#         self.SetMinSize(size)
#         self.aui_mgr=wx.aui.AuiManager(self)
#         self.aui_mgr.SetManagedWindow(self)
#         src.gui.panel.topcam.create(self)
#         self.Bind(wx.EVT_CLOSE, self.on_close)
#         self.Show()

#     def on_close(self, event):
#         self.Hide()  # Reuse on close
#         event.Skip()

class App(wx.Frame):
    def __init__(self, engine):
        super().__init__(None, title="wxPick", size=(800, 600))
        self.engine = engine
        global notebook_plugins,panel_plugins,toolbar_plugins,graph_plugins
        notebook_plugins = load_plugins(self,'src.gui.notebook')
        panel_plugins = load_plugins(self,'src.gui.panel')
        toolbar_plugins = load_plugins(self,'src.gui.toolbar')
        graph_plugins = load_plugins(self,'src.gui.graph')
        self.statusBar =self.CreateStatusBar(#number=5, 
            style= wx.STB_SIZEGRIP | wx.STB_SHOW_TIPS, #disable wx.STB_ELLIPSIZE_END
            id=0, name="StatusBar")
        self.statusBar_widths=[80,80,80,-1,-1]
        self.statusBar.SetFieldsCount(5,self.statusBar_widths)
        self.engine.subscribers.append(self.statusbar_update)
        for plugin in graph_plugins:
            # if hasattr(plugin, 'update'):
                self.engine.subscribers.append(plugin.update)
        self.aui_mgr = wx.aui.AuiManager(self)
        self.aui_mgr.SetManagedWindow(self)
        # self.frame2=FloatingFrame(self, "frame2", (300,300), (200,200), None)
        self.init_ui()
        self.create_menu()
        self.load_perspective()
        self.aui_mgr.Update()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()

    def init_ui(self):
        for plugin in panel_plugins:
            logger.info(f"calling {plugin}.create()")
            plugin.create(self)
        self.notebook = wx.aui.AuiNotebook(self)
        for plugin in notebook_plugins:
            # if hasattr(plugin, 'create'):
                plugin.create(self.notebook)
        self.gcode_handler = WxRichHandler(src.gui.notebook.gcode.gcode_display)
        self.log_handler = WxRichHandler(src.gui.notebook.log.log_display)
        self.engine.set_log_handler(self.log_handler)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_notebook_page_close)
        self.aui_mgr.AddPane(self.notebook, wx.aui.AuiPaneInfo().Name("Notebook").CenterPane())
        for plugin in toolbar_plugins:
            # if hasattr(plugin, 'create'):
                plugin.create(self)
        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)

    def create_menu(self):
        menubar = wx.MenuBar()
        tools_menu = wx.Menu()
        toolbar_plugins_menu = wx.Menu()
        for plugin in toolbar_plugins:
            # if hasattr(plugin, 'add_to_menu'):
                plugin.add_to_menu(toolbar_plugins_menu)
        tools_menu.Append(wx.ID_ANY, "Toolbars", toolbar_plugins_menu)
        panel_plugins_menu = wx.Menu()
        for plugin in panel_plugins:
            # if hasattr(plugin, 'add_to_menu'):
                plugin.add_to_menu(panel_plugins_menu)
        tools_menu.Append(wx.ID_ANY, "Panels", panel_plugins_menu)
        notebook_plugins_menu = wx.Menu()
        for plugin in notebook_plugins:
            # if hasattr(plugin, 'add_to_menu'):
                plugin.add_to_menu(notebook_plugins_menu)
        tools_menu.Append(wx.ID_ANY, "Notebooks", notebook_plugins_menu)
        # graph_plugins_menu = wx.Menu()
        # for plugin in graph_plugins:
        #     # if hasattr(plugin, 'add_to_menu'):
        #         plugin.add_to_menu(graph_plugins_menu)
        # tools_menu.AppendMenu(wx.ID_ANY, "Graphs", graph_plugins_menu)
        # tools_menu.AppendSeparator()
        # tools_menu.Append(999, "Reset Layout")
        # self.Bind(wx.EVT_MENU, self.on_reset_layout, id=999)
        self.Bind(wx.EVT_MENU, self.save_perspective, tools_menu.Append(wx.ID_ANY, 'Save persective', ''))
        menubar.Append(tools_menu, "&Tools")
        self.SetMenuBar(menubar)

    def on_notebook_page_close(self, event: wx.aui.AuiNotebookEvent):
        page_index = event.GetSelection() 
        name = self.notebook.GetPageText(page_index)
        for plugin in notebook_plugins:
            print(plugin.name, name)
            if plugin.name == name:
                self.GetMenuBar().Check(plugin.ID, False)
                break
        else: #propagate what we dont handle and exit
                logging.info("unhandled on_notebook_page_close %s"%name)
                event.Skip()
                return
        self.notebook.RemovePage(page_index)
        event.Veto()

    def on_pane_close(self, event: wx.aui.AuiManagerEvent):
        pane_info = event.GetPane()
        plugins= panel_plugins + toolbar_plugins
        for plugin in plugins:
            if plugin.name == pane_info.name:
                self.GetMenuBar().Check(plugin.ID, False)
                break
        else:
            logging.info("unhandled on_pane_close %s"%pane_info.name)
        event.Skip()

    def on_key(self, event):
        if event.KeyCode == wx.WXK_RETURN:
            self.log_handler.set_auto_scroll(True)
            self.gcode_handler.set_auto_scroll(True)
        event.Skip()

    def show_endstops(self, response):
        endstops = ["%s: %s"%(k.upper(),v) for k,v in response.items()]
        wx.MessageBox("\n".join(endstops), "Endstops Status", wx.OK | wx.ICON_INFORMATION)

    def statusbar_update(self,response):
        #{'eventtime': 293848.747924456, 'status': {'toolhead': {'position': [0.0, 470.0, -3.0, 0.0, 0.0, 0.0]}}}
        if ('webhooks' in response['status'] and
            'state' in response['status']['webhooks']):
            d = response['status']['webhooks']['state']
            icons = { "ready": "🟢", "paused": "⏸️", "error": "⛔", "shutdown": "🚫"}
            icon = icons.get(d, "●")
            field = f" {icon} {d} "
            self.statusBar.SetStatusText(field, 0)
            #self.statusBar.SetStatusTextColour(1, wx.Colour(color))
        if 'system_stats' in response['status']:
            if "sysload" in response['status']['system_stats']:
                self.statusBar.SetStatusText("load:%s"%response['status']['system_stats']['sysload'], 1)
            if "memavail" in response['status']['system_stats']:
                self.statusBar.SetStatusText("mem:%s"%response['status']['system_stats']['memavail'], 2)
        if "ch224q_pd toolhead" in response['status']:
            t=response['status']['ch224q_pd toolhead']
            pd=t.get('powergood', self.engine.status['ch224q_pd toolhead'].get('powergood', None))
            v=t.get('voltage', self.engine.status['ch224q_pd toolhead'].get('voltage', 'unknown'))
            icons = { True: "🟢", False: "🔴", None: "●" }
            self.statusBar.SetStatusText("PD:%s Volt:%s"%(icons[pd],v), 3)
        if ('toolhead' in response['status'] and
            'position' in response['status']['toolhead']):
            d=response['status']['toolhead']['position']
            if d is None: return
            pos_str = " ".join([f"{a}:{p:.3f}" for a, p in zip("XYZEAB", d)])
            self.statusBar.SetStatusText(pos_str, 4)
            #f = self.statusBar.GetFont ()
            width, _ = self.statusBar.GetTextExtent(pos_str)
            self.statusBar_widths[4]=width+10
            self.statusBar.SetStatusWidths(self.statusBar_widths)


    def load_perspective(self):
        try:
            with open('layout.ini', 'r') as f:
                self.aui_mgr.LoadPerspective(f.read())
                # if src.gui.toolbar_emergency.emergency_pane.IsShown():
                #     src.gui.toolbar_emergency.on_toggle(None)
                # else: None
                # ... other modules
        except:
            pass
    def save_perspective(self,event):
        with open('layout.ini', 'w') as f:
            f.write(self.aui_mgr.SavePerspective())

    def on_close(self, event):
        self.engine.stop()
        logger.removeHandler(self.log_handler)
        self.aui_mgr.UnInit()
        self.Destroy()

