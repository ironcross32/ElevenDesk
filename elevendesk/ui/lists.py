import wx


def get_selected_item(smart_list):
	# SmartList.get_selected_item reads index -1 when nothing is selected, returning the last row
	# (or raising IndexError on an empty list), so the selection is looked up by index instead.
	index = smart_list.get_selected_index()
	if index == wx.NOT_FOUND or index >= len(smart_list.models):
		return None
	return smart_list.models[index]
