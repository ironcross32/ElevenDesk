import wx
from wx import dataview


def get_selected_item(smart_list):
	# SmartList.get_selected_item reads index -1 when nothing is selected, returning the last row
	# (or raising IndexError on an empty list), so the selection is looked up by index instead.
	index = smart_list.get_selected_index()
	if index == wx.NOT_FOUND or index >= len(smart_list.models):
		return None
	return smart_list.models[index]


def delete_item(smart_list, item):
	# Deleting any row clears a macOS DataView's selection (a Windows ListCtrl only loses it when the
	# selected row goes), so the row now at the deleted position is selected to keep keyboard users in place.
	index = smart_list.find_index_of_item(item)
	smart_list.delete_item(item)
	if smart_list.get_selected_index() == wx.NOT_FOUND and smart_list.models:
		smart_list.set_selected_index(min(index, len(smart_list.models) - 1))


# On macOS SmartList is a DataViewCtrl rather than a ListCtrl, which never sends EVT_LIST_* events
# (and SmartList's own Bind maps activation to the wrong event), so the DataView equivalents are bound there.

def _uses_dataview(smart_list):
	return smart_list.control.use_dataview


def bind_selection_changed(smart_list, handler):
	if _uses_dataview(smart_list):
		smart_list.control.control.Bind(dataview.EVT_DATAVIEW_SELECTION_CHANGED, handler)
	else:
		smart_list.control.control.Bind(wx.EVT_LIST_ITEM_SELECTED, handler)


def bind_item_activated(smart_list, handler):
	if _uses_dataview(smart_list):
		smart_list.control.control.Bind(dataview.EVT_DATAVIEW_ITEM_ACTIVATED, handler)
	else:
		smart_list.control.control.Bind(wx.EVT_LIST_ITEM_ACTIVATED, handler)


def bind_key_down(smart_list, handler):
	if _uses_dataview(smart_list):
		smart_list.control.control.Bind(wx.EVT_KEY_DOWN, handler)
	else:
		smart_list.control.control.Bind(wx.EVT_LIST_KEY_DOWN, handler)


def is_delete_key(event):
	# The key labelled Delete on a Mac keyboard is backspace; forward delete is Fn+Delete.
	key_code = event.GetKeyCode()
	return key_code == wx.WXK_DELETE or (wx.Platform == "__WXMAC__" and key_code == wx.WXK_BACK)
