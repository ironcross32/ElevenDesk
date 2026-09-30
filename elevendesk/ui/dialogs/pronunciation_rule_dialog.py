import wx

from elevendesk import constants
from elevendesk.ui import choices


class PronunciationRuleDialog(wx.Dialog):
	# Collects one pronunciation rule. With ask_for_dictionary it also collects the name and
	# description of a new dictionary, because the API cannot create a dictionary without a rule.

	def __init__(self, parent, ask_for_dictionary=False):
		title = constants.TITLE_NEW_DICTIONARY if ask_for_dictionary else constants.TITLE_ADD_RULE
		wx.Dialog.__init__(self, parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.ask_for_dictionary = ask_for_dictionary
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._update_rule_type()
		self.first_input.SetFocus()

	def _create_controls(self):
		self.name_label = wx.StaticText(self, label=constants.LABEL_DICTIONARY_NAME)
		self.name_input = wx.TextCtrl(self, name=constants.LABEL_DICTIONARY_NAME)
		self.description_label = wx.StaticText(self, label=constants.LABEL_DICTIONARY_DESCRIPTION)
		self.description_input = wx.TextCtrl(self, name=constants.LABEL_DICTIONARY_DESCRIPTION)
		self.text_label = wx.StaticText(self, label=constants.LABEL_RULE_TEXT)
		self.text_input = wx.TextCtrl(self, name=constants.LABEL_RULE_TEXT)
		self.rule_type_label = wx.StaticText(self, label=constants.LABEL_RULE_TYPE)
		self.rule_type_combo = choices.create_choice(
			self,
			choices=[label for label, value in constants.RULE_TYPES],
			name=constants.LABEL_RULE_TYPE,
		)
		self.rule_type_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.replacement_label = wx.StaticText(self, label=constants.LABEL_ALIAS)
		self.replacement_input = wx.TextCtrl(self, name=constants.LABEL_ALIAS)
		self.alphabet_label = wx.StaticText(self, label=constants.LABEL_ALPHABET)
		self.alphabet_combo = choices.create_choice(
			self,
			choices=[label for label, value in constants.PHONEME_ALPHABETS],
			name=constants.LABEL_ALPHABET,
		)
		self.alphabet_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.case_sensitive_checkbox = wx.CheckBox(self, label=constants.LABEL_CASE_SENSITIVE)
		self.case_sensitive_checkbox.SetValue(True)
		self.word_boundaries_checkbox = wx.CheckBox(self, label=constants.LABEL_WORD_BOUNDARIES)
		self.word_boundaries_checkbox.SetValue(True)
		self.help_text = wx.StaticText(self, label=constants.LABEL_RULE_HELP)
		self.ok_label = wx.StaticText(self, label=constants.LABEL_OK)
		self.ok_button = wx.Button(self, wx.ID_OK, constants.LABEL_OK, name=constants.LABEL_OK)
		self.ok_button.SetDefault()
		self.cancel_label = wx.StaticText(self, label=constants.LABEL_CANCEL)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, constants.LABEL_CANCEL, name=constants.LABEL_CANCEL)
		if not self.ask_for_dictionary:
			for control in (self.name_label, self.name_input, self.description_label, self.description_input):
				control.Hide()
		self.first_input = self.name_input if self.ask_for_dictionary else self.text_input

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		labelled_controls = [
			(self.text_label, self.text_input),
			(self.rule_type_label, self.rule_type_combo),
			(self.replacement_label, self.replacement_input),
			(self.alphabet_label, self.alphabet_combo),
		]
		if self.ask_for_dictionary:
			labelled_controls[:0] = [
				(self.name_label, self.name_input),
				(self.description_label, self.description_input),
			]
		for label, control in labelled_controls:
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.LEFT | wx.RIGHT, constants.SECTION_GAP)
			main_sizer.Add(control, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.ALL, constants.SECTION_GAP)
		for checkbox in (self.case_sensitive_checkbox, self.word_boundaries_checkbox):
			main_sizer.Add(checkbox, constants.SIZER_PROPORTION_NONE, wx.ALL, constants.SECTION_GAP)
		main_sizer.Add(self.help_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.ALL, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.AddStretchSpacer()
		for label, button in (
			(self.ok_label, self.ok_button),
			(self.cancel_label, self.cancel_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.ALL, constants.SECTION_GAP)
		self.SetSizer(main_sizer)
		self.SetSize(constants.SMALL_DIALOG_SIZE)
		self.help_text.Wrap(self.GetClientSize().width - constants.SECTION_GAP * 2)
		main_sizer.Fit(self)

	def _bind_events(self):
		choices.bind_selection(self.rule_type_combo, self._on_rule_type)
		self.ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

	def _selected_value(self, combo, options):
		index = combo.GetSelection()
		if index == wx.NOT_FOUND:
			index = constants.FIRST_ITEM_INDEX
		return options[index][1]

	def _is_phoneme(self):
		return self._selected_value(self.rule_type_combo, constants.RULE_TYPES) == constants.RULE_TYPE_PHONEME

	def _on_rule_type(self, event):
		self._update_rule_type()

	def _update_rule_type(self):
		# The replacement field means different things per rule type, so its label and name follow the type.
		is_phoneme = self._is_phoneme()
		label = constants.LABEL_PHONEMES if is_phoneme else constants.LABEL_ALIAS
		self.replacement_label.SetLabel(label)
		self.replacement_input.SetName(label)
		self.alphabet_label.Enable(is_phoneme)
		self.alphabet_combo.Enable(is_phoneme)
		self.Layout()

	def _report_invalid(self, message, control):
		wx.MessageBox(message, constants.TITLE_ERROR, wx.OK | wx.ICON_ERROR, self)
		control.SetFocus()

	def _on_ok(self, event):
		if self.ask_for_dictionary and not self.name_input.GetValue().strip():
			self._report_invalid(constants.ERROR_DICTIONARY_NAME_REQUIRED, self.name_input)
			return
		if not self.text_input.GetValue().strip():
			self._report_invalid(constants.ERROR_RULE_TEXT_REQUIRED, self.text_input)
			return
		if not self.replacement_input.GetValue().strip():
			self._report_invalid(constants.ERROR_RULE_REPLACEMENT_REQUIRED, self.replacement_input)
			return
		self.EndModal(wx.ID_OK)

	def get_dictionary_name(self):
		return self.name_input.GetValue().strip()

	def get_dictionary_description(self):
		return self.description_input.GetValue().strip()

	def get_rule(self):
		return {
			constants.KEY_STRING_TO_REPLACE: self.text_input.GetValue().strip(),
			constants.KEY_RULE_TYPE: self._selected_value(self.rule_type_combo, constants.RULE_TYPES),
			constants.KEY_REPLACEMENT: self.replacement_input.GetValue().strip(),
			constants.KEY_ALPHABET: self._selected_value(self.alphabet_combo, constants.PHONEME_ALPHABETS),
			constants.KEY_CASE_SENSITIVE: self.case_sensitive_checkbox.GetValue(),
			constants.KEY_WORD_BOUNDARIES: self.word_boundaries_checkbox.GetValue(),
		}
