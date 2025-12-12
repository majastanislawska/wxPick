import wx
import logging
logger = logging.getLogger(__name__)

class TextCtrlCompleter(wx.EvtHandler):
    def __init__(self, tc: wx.TextCtrl, items=None, match_func=None, max_items=10):
        super().__init__()
        self.tc = tc
        self.items = items or []
        self.max_items = max_items
        # match_func(prefix, item) -> bool ; default: startswith (case-insensitive)
        self.match_func = match_func or (lambda p, i: i.lower().startswith(p.lower()))
        self.listbox = None
        self.CreatePopup()
        self.tc.Bind(wx.EVT_TEXT, self.OnText)
        self.tc.Bind(wx.EVT_CHAR, self.OnChar)
        self.tc.Bind(wx.EVT_KEY_DOWN, self.OnChar)
        # self.tc.Bind(wx.EVT_
        self.tc.Bind(wx.EVT_KILL_FOCUS, lambda e: self.HidePopup())

    def SetItems(self, items):
        self.items = list(items)

    def AddItem(self, item):
        self.items.append(item)

    def OnText(self, event):
        self.UpdatePopup()
        event.Skip()

    def OnChar(self, event):
        key = event.GetKeyCode()
        if not self.popup.IsShown():  event.Skip(); return
        match key:
            case wx.WXK_DOWN:         self.Navigate(key)
            case wx.WXK_UP:           self.Navigate(key)
            case wx.WXK_RETURN:       self.AcceptSelection()
            case wx.WXK_NUMPAD_ENTER: self.AcceptSelection()
            case wx.WXK_TAB:          self.AcceptSelection()
            case wx.WXK_ESCAPE:       self.HidePopup()
            case _ :                  event.Skip()

    def GetCurrentPrefix(self):
        # default: complete the word at insertion point (after last whitespace)
        pos = self.tc.GetInsertionPoint()
        text = self.tc.GetValue()[:pos]
        sep = max(text.rfind(' '), text.rfind('\t'), text.rfind('\n'), -1)
        prefix = text[sep+1:]
        return prefix, pos, sep+1

    def UpdatePopup(self):
        prefix, pos, start_index = self.GetCurrentPrefix()
        if not prefix: self.HidePopup(); return
        matches = [it for it in self.items if self.match_func(prefix, it)]
        if not matches: self.HidePopup(); return
        matches = matches[: self.max_items]
        self.listbox.Clear()
        for m in matches:
            self.listbox.Append(m)
        self.listbox.SetSelection(0)
        self.ShowPopup()

    def CreatePopup(self):
        style = wx.SIMPLE_BORDER
        self.popup = wx.PopupTransientWindow(self.tc, style)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listbox = wx.ListBox(self.popup, style=wx.LB_SINGLE)
        sizer.Add(self.listbox, 1, wx.EXPAND, 0)
        self.popup.SetSizer(sizer)
        self.popup.Layout()
        # self.popup.Bind(wx.EVT_LEFT_DOWN, lambda e: None)
        # self.listbox.Bind(wx.EVT_LEFT_DOWN, lambda e: self.AcceptSelection())
        self.listbox.Bind(wx.EVT_LEFT_DCLICK, lambda e: self.AcceptSelection())
        self.listbox.Bind(wx.EVT_LISTBOX, lambda e: self.AcceptSelection())
        self.listbox.Bind(wx.EVT_CHAR_HOOK, self.OnListboxChar)
        self.listbox.SetFocus()

    def ShowPopup(self):
        tc_size = self.tc.GetSize()
        screen_pt = self.tc.ClientToScreen((0, tc_size.y))
        width = max(self.tc.GetSize().GetWidth(), 200)
        height = min(200, 20 + self.listbox.GetCount() * 20)
        self.popup.SetSize(wx.Rect(screen_pt.x, screen_pt.y, width, height))
        self.popup.Show(True)
        self.listbox.SetFocus()

    def HidePopup(self):
        if self.popup and self.popup.IsShown():
            self.popup.Dismiss()

    def Navigate(self, key):
        logging.info("Navigate called")
        sel = self.listbox.GetSelection()
        if sel == wx.NOT_FOUND: return
        count = self.listbox.GetCount()
        if key == wx.WXK_DOWN: sel = min(count-1, sel+1)
        else:                  sel = max(0, sel-1)
        self.listbox.SetSelection(sel)

    def AcceptSelection(self):
        logging.info("AcceptSelection called")
        sel = self.listbox.GetSelection()
        if sel == wx.NOT_FOUND:
            self.HidePopup()
            return
        value = self.listbox.GetString(sel)
        # replace the current prefix with value
        prefix, pos, start_index = self.GetCurrentPrefix()
        full = self.tc.GetValue()
        new_text = full[:start_index] + value + full[pos:]
        self.tc.SetValue(new_text)
        # move caret after inserted word
        self.tc.SetInsertionPoint(start_index + len(value))
        self.HidePopup()

    def OnListboxChar(self, event):
        key = event.GetKeyCode()
        match key:
            case wx.WXK_RETURN:       self.AcceptSelection()
            case wx.WXK_NUMPAD_ENTER: self.AcceptSelection()
            case wx.WXK_TAB:          self.AcceptSelection()
            case wx.WXK_ESCAPE:       self.HidePopup()
            case wx.WXK_DOWN:         self.Navigate(key) 
            case wx.WXK_UP:           self.Navigate(key)
            case _ : event.Skip()

