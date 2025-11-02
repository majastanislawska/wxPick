import wx
import logging
import src.engine
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Objecs"
panel = None
pane = None
paneinfo=None
parent=None

objects_tree = None
list_button = None
query_button = None
root_item = None

def create(notebook):
    global name,panel, pane, paneinfo, parent
    global objects_tree, list_button, query_button, root_item
    parent=notebook
    panel = wx.Panel(notebook, wx.ID_ANY, wx.DefaultPosition,wx.DefaultSize, wx.TAB_TRAVERSAL)
    sizer = wx.BoxSizer(wx.VERTICAL)
    btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
    list_button = wx.Button(panel, label="List Objects")
    query_button = wx.Button(panel, label="Query Selected")
    btn_sizer.Add(list_button, 0, wx.ALL, 5)
    btn_sizer.Add(query_button, 0, wx.ALL, 5)
    sizer.Add(btn_sizer, 0, wx.ALL, 5)
    objects_tree = wx.TreeCtrl(panel, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
    root_item = objects_tree.AddRoot("Click 'List Objects' to start")
    sizer.Add(objects_tree, 1, wx.EXPAND | wx.ALL, 5)
    panel.SetSizer(sizer)
    panel.Layout()
    notebook.AddPage(panel, name, False)

    list_button.Bind(wx.EVT_BUTTON, on_list_objects)
    query_button.Bind(wx.EVT_BUTTON, on_query_selected)
    #objects_tree.Bind(wx.EVT_TREE_SEL_CHANGED, on_object_selected)
    return panel

def on_list_objects(event):
    src.engine.engine.send_command("objects/list", {}, store_object_list)

def store_object_list(response):
    global root_item
    objects_tree.DeleteChildren(root_item)
    if "objects" in response:
        object_names = [name for name in response["objects"]]
        objects_tree.SetItemText(root_item, f"Klipper Objects ({len(object_names)})")
        
        for name in sorted(object_names):
            item = objects_tree.AppendItem(root_item, f"{name} (click to query)")
            objects_tree.SetItemTextColour(item, wx.Colour("gray"))
            objects_tree.SetPyData(item, name)
        objects_tree.Expand(root_item)
    else:
        objects_tree.SetItemText(root_item, f"ERROR list: {response}")

def on_query_selected(event):
    selected = objects_tree.GetSelection()
    if selected.IsOk():
        obj_name = objects_tree.GetItemData(selected)
        params = {"objects": {obj_name: None}}
        src.engine.engine.send_command("objects/query", params, populate_by_name)

def populate_by_name(response):
    if "status" in response:
        status = response['status']
        for obj_name, obj_data in status.items():
            item = find_tree_item_by_name(obj_name)
            if item.IsOk():
                objects_tree.DeleteChildren(item)
                for key, value in sorted(obj_data.items()):
                    build_tree_recursive(item, key, value)
                objects_tree.SetItemText(item, obj_name)
                objects_tree.SetItemTextColour(item, wx.Colour("blue"))
                objects_tree.Expand(item)

def find_tree_item_by_name(name):
    item, cookie = objects_tree.GetFirstChild(root_item)
    while item.IsOk():
        stored_name = objects_tree.GetItemData(item)
        if stored_name == name:
            return item
        item, cookie = objects_tree.GetNextChild(root_item, cookie)
    return wx.TreeItemId()

def build_tree_recursive(parent_node, name, data):
    if isinstance(data, dict):
        key_node = objects_tree.AppendItem(parent_node, name)
        objects_tree.SetItemTextColour(key_node, wx.Colour("blue"))
        for sub_key, sub_value in sorted(data.items()):
            build_tree_recursive(key_node, sub_key, sub_value)
    elif isinstance(data, list):
        list_node = objects_tree.AppendItem(parent_node, f"{name} [{len(data)} items]")
        objects_tree.SetItemTextColour(list_node, wx.Colour("purple"))
        for i, item in enumerate(data):
            simple_item = str(item)
            child_node = objects_tree.AppendItem(list_node, f"[{i}]: {simple_item}")
            # try:
            #     if isinstance(item, (int, float)):
            #         objects_tree.SetItemTextColour(child_node, wx.Colour("green"))
            #     elif item is True:
            #         objects_tree.SetItemTextColour(child_node, wx.Colour("green"))
            #     elif item is False:
            #         objects_tree.SetItemTextColour(child_node, wx.Colour("red"))
            #     else:
            #         objects_tree.SetItemTextColour(child_node, wx.Colour("black"))
            # except:
            #     objects_tree.SetItemTextColour(child_node, wx.Colour("black"))
    else:
        if isinstance(data, str) and ('\n' in data or len(data) > 50):
            # **LONG/MULTILINE: Show preview + length**
            preview = data.replace('\n', '\\n')[:100].rstrip() + "..." if len(data) > 100 else data.replace('\n', '\\n')
            attr_text = f"{name}: '{preview}' [{len(data)} chars]"
        else:
            attr_text = f"{name}: {repr(data)}"
        node = objects_tree.AppendItem(parent_node, attr_text)
        # COLOR BY TYPE
        # if isinstance(data, (int, float)):
        #     objects_tree.SetItemTextColour(node, wx.Colour("green"))
        # elif data is True:
        #     objects_tree.SetItemTextColour(node, wx.Colour("green"))
        # elif data is False:
        #     objects_tree.SetItemTextColour(node, wx.Colour("red"))
        # else:
        #     objects_tree.SetItemTextColour(node, wx.Colour("black"))

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Objects Notebook")
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