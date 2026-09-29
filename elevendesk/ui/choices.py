import sys

import wx

from elevendesk import constants


def create_choice(parent, choices=None, name=None, **kwargs):
	if choices is None:
		choices = []
	if sys.platform == 'darwin':
		widget = wx.Choice(parent, choices=choices, **kwargs)
	else:
		kwargs['style'] = kwargs.get('style', 0) | wx.CB_READONLY
		widget = wx.ComboBox(parent, choices=choices, **kwargs)
	if name:
		widget.SetName(name)
	return widget


def set_model_choices(combo, models, selected_model_id):
	combo.Clear()
	for model in models:
		combo.Append(model[constants.KEY_NAME])
	select_model(combo, models, selected_model_id)


def select_model(combo, models, model_id):
	for index, model in enumerate(models):
		if model[constants.KEY_ID] == model_id:
			combo.SetSelection(index)
			return
	if models:
		combo.SetSelection(constants.FIRST_ITEM_INDEX)


def get_selected_model_id(combo, models):
	index = combo.GetSelection()
	if index == wx.NOT_FOUND:
		return constants.EMPTY_TEXT
	return models[index][constants.KEY_ID]
