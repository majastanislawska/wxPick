
import sys, time, math, os, os.path
import wx
import wx.propgrid
import src.gui.panel.topcam
import src.gui.notebook.gcode  # Add other modules as needed
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Config"
panel = None
pane = None
paneinfo=None
parent=None

class SizeProperty(wx.propgrid.PyProperty):
    """ Demonstrates a property with few children.
    """
    def __init__(self, label, name = wx.propgrid.PG_LABEL, value=wx.Size(0, 0)):
        wx.propgrid.PyProperty.__init__(self, label, name)

        value = self._ConvertValue(value)

        self.AddPrivateChild( wx.propgrid.IntProperty("X", value=value.x) )
        self.AddPrivateChild( wx.propgrid.IntProperty("Y", value=value.y) )

        self.m_value = value

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def RefreshChildren(self):
        size = self.m_value
        self.Item(0).SetValue( size.x )
        self.Item(1).SetValue( size.y )

    def _ConvertValue(self, value):
        """ Utility convert arbitrary value to a real wx.Size.
        """
        from operator import isSequenceType
        if isinstance(value, wx.Point):
            value = wx.Size(value.x, value.y)
        elif isSequenceType(value):
            value = wx.Size(*value)
        return value

    def ChildChanged(self, thisValue, childIndex, childValue):
        # FIXME: This does not work yet. ChildChanged needs be fixed "for"
        #        wxPython in wxWidgets SVN trunk, and that has to wait for
        #        2.9.1, as wxPython 2.9.0 uses WX_2_9_0_BRANCH.
        size = self._ConvertValue(self.m_value)
        if childIndex == 0:
            size.x = childValue
        elif childIndex == 1:
            size.y = childValue
        else:
            raise AssertionError

        return size

class SizeProperty(wx.propgrid.PyProperty):
    """ Demonstrates a property with few children.
    """
    def __init__(self, label, name = wx.propgrid.PG_LABEL_STRING, value=wx.Size(0, 0)):
        wx.propgrid.PyProperty.__init__(self, label, name)
        value = self._ConvertValue(value)
        self.AddPrivateChild( wx.propgrid.IntProperty("X", value=value.x) )
        self.AddPrivateChild( wx.propgrid.IntProperty("Y", value=value.y) )
        self.m_value = value

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def RefreshChildren(self):
        size = self.m_value
        self.Item(0).SetValue( size.x )
        self.Item(1).SetValue( size.y )

    def _ConvertValue(self, value):
        """ Utility convert arbitrary value to a real wx.Size.
        """
        from operator import isSequenceType
        if isinstance(value, wx.Point):
            value = wx.Size(value.x, value.y)
        elif isSequenceType(value):
            value = wx.Size(*value)
        return value

    def ChildChanged(self, thisValue, childIndex, childValue):
        # FIXME: This does not work yet. ChildChanged needs be fixed "for"
        #        wxPython in wxWidgets SVN trunk, and that has to wait for
        #        2.9.1, as wxPython 2.9.0 uses WX_2_9_0_BRANCH.
        size = self._ConvertValue(self.m_value)
        if childIndex == 0:
            size.x = childValue
        elif childIndex == 1:
            size.y = childValue
        else:
            raise AssertionError

        return size

class PyObjectPropertyValue:
    """\
    Value type of our sample PyObjectProperty. We keep a simple dash-delimited
    list of string given as argument to constructor.
    """
    def __init__(self, s=None):
        try:
            self.ls = [a.strip() for a in s.split('-')]
        except:
            self.ls = []

    def __repr__(self):
        return ' - '.join(self.ls)

class PyObjectProperty(wx.propgrid.PyProperty):
    """\
    Another simple example. This time our value is a PyObject.

    NOTE: We can't return an arbitrary python object in DoGetValue. It cannot
          be a simple type such as int, bool, double, or string, nor an array
          or wxObject based. Dictionary, None, or any user-specified Python
          class is allowed.
    """
    def __init__(self, label, name = wx.propgrid.PG_LABEL_STRING, value=None):
        wx.propgrid.PyProperty.__init__(self, label, name)
        self.SetValue(value)

    def GetClassName(self):
        return self.__class__.__name__

    def GetEditor(self):
        return "TextCtrl"

    def ValueToString(self, value, flags):
        return repr(value)

    def StringToValue(self, s, flags):
        """ If failed, return False or (False, None). If success, return tuple
            (True, newValue).
        """
        v = PyObjectPropertyValue(s)
        return (True, v)

class SampleMultiButtonEditor(wx.propgrid.PyTextCtrlEditor):
    def __init__(self):
        wx.propgrid.PyTextCtrlEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wx.propgrid.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddButton("...")
        buttons.AddButton("A")
        # Add a bitmap button
        buttons.AddBitmapButton(wx.ArtProvider.GetBitmap(wx.ART_FOLDER))
        
        # Create the 'primary' editor control (textctrl in this case)
        wnd = self.CallSuperMethod("CreateControls",
                                   propGrid,
                                   property,
                                   pos,
                                   buttons.GetPrimarySize())

        # Finally, move buttons-subwindow to correct position and make sure
        # returned wx.propgridWindowList contains our custom button list.
        buttons.Finalize(propGrid, pos);

        # We must maintain a reference to any editor objects we created
        # ourselves. Otherwise they might be freed prematurely. Also,
        # we need it in OnEvent() below, because in Python we cannot "cast"
        # result of wxPropertyGrid.GetEditorControlSecondary() into
        # PGMultiButton instance.
        self.buttons = buttons

        return (wnd, buttons)

    def OnEvent(self, propGrid, prop, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()

            if evtId == buttons.GetButtonId(0):
                # Do something when the first button is pressed
                wx.LogDebug("First button pressed");
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(1):
                # Do something when the second button is pressed
                wx.MessageBox("Second button pressed");
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(2):
                # Do something when the third button is pressed
                wx.MessageBox("Third button pressed");
                return False  # Return false since value did not change

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)
    
class SingleChoiceDialogAdapter(wx.propgrid.PyEditorDialogAdapter):
    """ This demonstrates use of wx.propgrid.PyEditorDialogAdapter.
    """
    def __init__(self, choices):
        wx.propgrid.PyEditorDialogAdapter.__init__(self)
        self.choices = choices
    def DoShowDialog(self, propGrid, property):
        s = wx.GetSingleChoice("Message", "Caption", self.choices)
        if s:
            self.SetValue(s)
            return True

        return False
class SingleChoiceProperty(wx.propgrid.PyStringProperty):
    def __init__(self, label, name=wx.propgrid.PG_LABEL_STRING, value=''):
        wx.propgrid.PyStringProperty.__init__(self, label, name, value)

        # Prepare choices
        dialog_choices = []
        dialog_choices.append("Cat");
        dialog_choices.append("Dog");
        dialog_choices.append("Gibbon");
        dialog_choices.append("Otter");

        self.dialog_choices = dialog_choices

    def GetEditor(self):
        # Set editor to have button
        return "TextCtrlAndButton"

    def GetEditorDialog(self):
        # Set what happens on button click
        return SingleChoiceDialogAdapter(self.dialog_choices)

class TrivialPropertyEditor(wx.propgrid.PyEditor):
    """\
    This is a simple re-creation of TextCtrlWithButton. Note that it does
    not take advantage of wx.TextCtrl and wx.Button creation helper functions
    in wx.PropertyGrid.
    """
    def __init__(self):
        wx.propgrid.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, sz):
        """ Create the actual wxPython controls here for editing the
            property value.

            You must use propgrid.GetPanel() as parent for created controls.

            Return value is either single editor control or tuple of two
            editor controls, of which first is the primary one and second
            is usually a button.
        """
        try:
            x, y = pos
            w, h = sz
            h = 64 + 6

            # Make room for button
            bw = propgrid.GetRowHeight()
            w -= bw

            s = property.GetDisplayedString();

            tc = wx.TextCtrl(propgrid.GetPanel(), wx.propgrid.PG_SUBID1, s,
                             (x,y), (w,h),
                             wx.TE_PROCESS_ENTER)
            btn = wx.Button(propgrid.GetPanel(), wx.propgrid.PG_SUBID2, '...',
                            (x+w, y),
                            (bw, h), wx.WANTS_CHARS)
            return (tc, btn)
        except:
            import traceback
            print(traceback.print_exc())

    def UpdateControl(self, property, ctrl):
        ctrl.SetValue(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        """ Return True if modified editor value should be committed to
            the property. To just mark the property value modified, call
            propgrid.EditorsValueWasModified().
        """
        if not ctrl:
            return False

        evtType = event.GetEventType()

        if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
            if propgrid.IsEditorsValueModified():
                return True
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            #
            # Pass this event outside wxPropertyGrid so that,
            # if necessary, program can tell when user is editing
            # a textctrl.
            event.Skip()
            event.SetId(propgrid.GetId())

            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        tc = ctrl
        textVal = tc.GetValue()

        if property.UsesAutoUnspecified() and not textVal:
            return (True, None)

        res, value = property.StringToValue(textVal,
                                            wx.propgrid.PG_EDITABLE_VALUE)

        # Changing unspecified always causes event (returning
        # True here should be enough to trigger it).
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.Remove(0,len(ctrl.GetValue()))

    def SetControlStringValue(self, property, ctrl, text):
        ctrl.SetValue(text)

    def OnFocus(self, property, ctrl):
        ctrl.SetSelection(-1,-1)
        ctrl.SetFocus()

class LargeImagePickerCtrl(wx.Panel):
    """\
    Control created and used by LargeImageEditor.
    """
    def __init__(self):
        pre = wx.PrePanel()
        self.PostCreate(pre)

    def Create(self, parent, id_, pos, size, style = 0):
        wx.Panel.Create(self, parent, id_, pos, size,
                        style | wx.BORDER_SIMPLE)
        img_spc = size[1]
        self.tc = wx.TextCtrl(self, -1, "", (img_spc,0), (2048,size[1]),
                              wx.BORDER_NONE)
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.property = None
        self.bmp = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)

        whiteBrush = wx.Brush(wx.WHITE)
        dc.SetBackground(whiteBrush)
        dc.Clear()

        bmp = self.bmp
        if bmp:
            dc.DrawBitmap(bmp, 2, 2)
        else:
            dc.SetPen(wx.Pen(wx.BLACK))
            dc.SetBrush(whiteBrush)
            dc.DrawRectangle(2, 2, 64, 64)

    def RefreshThumbnail(self):
        """\
        We use here very simple image scaling code.
        """
        if not self.property:
            self.bmp = None
            return

        path = self.property.DoGetValue()

        if not os.path.isfile(path):
            self.bmp = None
            return

        image = wx.Image(path)
        image.Rescale(64, 64)
        self.bmp = wx.BitmapFromImage(image)

    def SetProperty(self, property):
        self.property = property
        self.tc.SetValue(property.GetDisplayedString())
        self.RefreshThumbnail()

    def SetValue(self, s):
        self.RefreshThumbnail()
        self.tc.SetValue(s)

    def GetLastPosition(self):
        return self.tc.GetLastPosition()

class LargeImageEditor(wx.propgrid.PyEditor):
    """\
    Double-height text-editor with image in front.
    """
    def __init__(self):
        wx.propgrid.PyEditor.__init__(self)

    def CreateControls(self, propgrid, property, pos, sz):
        try:
            x, y = pos
            w, h = sz
            h = 64 + 6

            # Make room for button
            bw = propgrid.GetRowHeight()
            w -= bw

            lipc = LargeImagePickerCtrl()
            if sys.platform.startswith('win'):
                lipc.Hide()
            lipc.Create(propgrid.GetPanel(), wx.propgrid.PG_SUBID1, (x,y), (w,h))
            lipc.SetProperty(property)
            # Hmmm.. how to have two-stage creation without subclassing?
            #btn = wx.PreButton()
            #pre = wx.PreWindow()
            #self.PostCreate(pre)
            #if sys.platform == 'win32':
            #    btn.Hide()
            #btn.Create(propgrid, wx.propgrid.PG_SUBID2, '...', (x2-bw,pos[1]),
            #           (bw,h), wx.WANTS_CHARS)
            btn = wx.Button(propgrid.GetPanel(), wx.propgrid.PG_SUBID2, '...',
                            (x+w, y),
                            (bw, h), wx.WANTS_CHARS)
            return (lipc, btn)
        except:
            import traceback
            print(traceback.print_exc())

    def UpdateControl(self, property, ctrl):
        ctrl.SetValue(property.GetDisplayedString())

    def DrawValue(self, dc, rect, property, text):
        if not property.IsValueUnspecified():
            dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        """ Return True if modified editor value should be committed to
            the property. To just mark the property value modified, call
            propgrid.EditorsValueWasModified().
        """
        if not ctrl:
            return False

        evtType = event.GetEventType()

        if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
            if propgrid.IsEditorsValueModified():
                return True
        elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
            #
            # Pass this event outside wxPropertyGrid so that,
            # if necessary, program can tell when user is editing
            # a textctrl.
            event.Skip()
            event.SetId(propgrid.GetId())

            propgrid.EditorsValueWasModified()
            return False

        return False

    def GetValueFromControl(self, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        tc = ctrl.tc
        textVal = tc.GetValue()

        if property.UsesAutoUnspecified() and not textVal:
            return (None, True)

        res, value = property.StringToValue(textVal,
                                            wx.propgrid.PG_EDITABLE_VALUE)

        # Changing unspecified always causes event (returning
        # True here should be enough to trigger it).
        if not res and value is None:
            res = True

        return (res, value)

    def SetValueToUnspecified(self, property, ctrl):
        ctrl.tc.Remove(0,len(ctrl.tc.GetValue()))

    def SetControlStringValue(self, property, ctrl, txt):
        ctrl.SetValue(txt)

    def OnFocus(self, property, ctrl):
        ctrl.tc.SetSelection(-1,-1)
        ctrl.tc.SetFocus()

    def CanContainCustomImage(self):
        return True

def create(notebook):
    global name,panel, pane, paneinfo, parent
    parent=notebook
    panel = wx.Panel(notebook, wx.ID_ANY)
    sizer = wx.BoxSizer(wx.VERTICAL)
    pg = wx.propgrid.PropertyGridManager(panel,
                        style=wx.propgrid.PG_SPLITTER_AUTO_CENTER |
                              wx.propgrid.PG_AUTO_SORT |
                              wx.propgrid.PG_TOOLBAR)
    
    if not getattr(sys, '_PropGridEditorsRegistered', False):
        pg.RegisterEditor(TrivialPropertyEditor)
        pg.RegisterEditor(SampleMultiButtonEditor)
        pg.RegisterEditor(LargeImageEditor)
        # ensure we only do it once
        sys._PropGridEditorsRegistered = True

    pg.AddPage( "Page 1 - Testing All" )
    pg.Append( wx.propgrid.PropertyCategory("1 - Basic Properties") )
    pg.Append( wx.propgrid.StringProperty("String",value="Some Text") )
    pg.Append( wx.propgrid.IntProperty("Int",value=100) )
    pg.Append( wx.propgrid.FloatProperty("Float",value=100.0) )
    pg.Append( wx.propgrid.BoolProperty("Bool",value=True) )
    pg.Append( wx.propgrid.BoolProperty("Bool_with_Checkbox",value=True) )
    pg.SetPropertyAttribute("Bool_with_Checkbox", "UseCheckbox", True)
    pg.Append( wx.propgrid.PropertyCategory("2 - More Properties") )
    pg.Append( wx.propgrid.LongStringProperty("LongString",
        value="This is a\\nmulti-line string\\nwith\\ttabs\\nmixed\\tin."))
    pg.Append( wx.propgrid.DirProperty("Dir",value="C:\\Windows") )
    pg.Append( wx.propgrid.FileProperty("File",value="C:\\Windows\\system.ini") )
    pg.Append( wx.propgrid.ArrayStringProperty("ArrayString",value=['A','B','C']) )
    pg.Append( wx.propgrid.EnumProperty("Enum","Enum",
                                    ['wxPython Rules',
                                    'wxPython Rocks',
                                    'wxPython Is The Best'],
                                    [10,11,12],
                                    0) )
    pg.Append( wx.propgrid.EditEnumProperty("EditEnum","EditEnumProperty",
                                        ['A','B','C'],
                                        [0,1,2],
                                        "Text Not in List") )
    pg.Append( wx.propgrid.PropertyCategory("3 - Advanced Properties") )
    #pg.Append( wx.propgrid.DateProperty("Date",value=wx.DateTime_Now()) )
    pg.Append( wx.propgrid.FontProperty("Font",value=panel.GetFont()) )
    pg.Append( wx.propgrid.ColourProperty("Colour",
                                    value=panel.GetBackgroundColour()) )
    pg.Append( wx.propgrid.SystemColourProperty("SystemColour") )
    pg.Append( wx.propgrid.ImageFileProperty("ImageFile") )
    pg.Append( wx.propgrid.MultiChoiceProperty("MultiChoice",
                choices=['wxWidgets','QT','GTK+']) )
    pg.Append( wx.propgrid.PropertyCategory("4 - Additional Properties") )
    # pg.Append( wx.propgrid.PointProperty("Point",value=panel.GetPosition()) )
    #pg.Append( SizeProperty("Size",value=panel.GetSize()) )
    # pg.Append( wx.propgrid.FontDataProperty("FontData") )
    pg.Append( wx.propgrid.IntProperty("IntWithSpin",value=256) )
    pg.SetPropertyEditor("IntWithSpin","SpinCtrl")
    pg.SetPropertyAttribute( "File", wx.propgrid.PG_FILE_SHOW_FULL_PATH, 0 )
    pg.SetPropertyAttribute( "File", wx.propgrid.PG_FILE_INITIAL_PATH,
                                 "C:\\Program Files\\Internet Explorer" )
    # pg.SetPropertyAttribute( "Date", wx.propgrid.PG_DATE_PICKER_STYLE,
    #                             wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
    pg.Append( wx.propgrid.PropertyCategory("5 - Custom Properties and Editors") )
    # pg.Append( IntProperty2("IntProperty2", value=1024) )

    pg.Append( PyObjectProperty("PyObjectProperty") )

    #pg.Append( DirsProperty("Dirs1",value=['C:/Lib','C:/Bin']) )
    #pg.Append( DirsProperty("Dirs2",value=['/lib','/bin']) )

    # Test another type of delimiter
    # pg.SetPropertyAttribute("Dirs2", "Delimiter", '"')

    # SampleMultiButtonEditor
    pg.Append( wx.propgrid.LongStringProperty("MultipleButtons") );
    pg.SetPropertyEditor("MultipleButtons", "SampleMultiButtonEditor");
    pg.Append( SingleChoiceProperty("SingleChoiceProperty") )

    # Custom editor samples
    prop = pg.Append( wx.propgrid.StringProperty("StringWithCustomEditor",
                                            value="test value") )
    pg.SetPropertyEditor(prop, "TrivialPropertyEditor")

    pg.Append( wx.propgrid.ImageFileProperty("ImageFileWithLargeEditor") )
    pg.SetPropertyEditor("ImageFileWithLargeEditor", "LargeImageEditor")

    # When page is added, it will become the target page for AutoFill
    # calls (and for other property insertion methods as well)
    pg.AddPage( "Page 2 - Results of AutoFill will appear here" )
    
    sizer.Add(pg, 1, wx.EXPAND)
    panel.SetSizer(sizer)
    notebook.AddPage(panel, "Config", False)  # False to not select by default
    sizer.Layout()
    return panel

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Config Notebook")
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