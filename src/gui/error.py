import wx

def gcode_error_callback(data):
    if not 'error' in data: return
    return message(data['message'],data['error'])

def message(message,title="Error"):
    return wx.MessageBox(message, title, wx.OK | wx.ICON_EXCLAMATION)
