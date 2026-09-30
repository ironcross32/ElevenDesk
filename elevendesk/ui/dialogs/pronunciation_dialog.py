import os
import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import config
from elevendesk import constants
from elevendesk.ui import lists
from elevendesk.ui.dialogs.pronunciation_rule_dialog import PronunciationRuleDialog
from elevendesk.ui.status_text import StatusText, announce

_RULE_TYPE_LABELS = {value: label for label, value in constants.RULE_TYPES}
_ALPHABET_LABELS = {value: label for label, value in constants.PHONEME_ALPHABETS}


class PronunciationDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_PRONUNCIATION, size=constants.DIALOG_SIZE)
		self.tts_dictionary_ids = config.load_tts_pronunciation_dictionary_ids()
		self.rules_request_id = 0
		# Shown alongside the rule count once the selected dictionary's rules have loaded.
		self.pending_status_message = None
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()
		self.dictionary_list.control.control.SetFocus()
		self._load_dictionaries()

	def _create_controls(self):
		self.dictionary_label = wx.StaticText(self, label=constants.LABEL_DICTIONARIES)
		self.dictionary_list = SmartList(parent=self, name=constants.LABEL_DICTIONARIES)
		self.dictionary_list.set_columns([
			Column(constants.COLUMN_NAME, constants.COLUMN_WIDTH_NAME, constants.KEY_NAME),
			Column(constants.COLUMN_RULES, constants.COLUMN_WIDTH_RULES, lambda item: str(item[constants.KEY_RULE_COUNT])),
			Column(constants.TAB_TTS, constants.COLUMN_WIDTH_TYPE, constants.KEY_USED_IN_TTS),
			Column(constants.COLUMN_DESCRIPTION, constants.COLUMN_WIDTH_DESCRIPTION, constants.KEY_DESCRIPTION),
		])
		self.use_in_tts_checkbox = wx.CheckBox(self, label=constants.LABEL_USE_IN_TTS)
		self.dictionary_buttons = []
		self.new_button = self._create_button(constants.LABEL_NEW_DICTIONARY, self.dictionary_buttons)
		self.import_button = self._create_button(constants.LABEL_IMPORT_DICTIONARY, self.dictionary_buttons)
		self.rename_button = self._create_button(constants.LABEL_RENAME, self.dictionary_buttons)
		self.archive_button = self._create_button(constants.LABEL_ARCHIVE, self.dictionary_buttons)
		self.download_button = self._create_button(constants.LABEL_DOWNLOAD_DICTIONARY, self.dictionary_buttons)
		self.rule_label = wx.StaticText(self, label=constants.LABEL_RULES)
		self.rule_list = SmartList(parent=self, name=constants.LABEL_RULES)
		self.rule_list.set_columns([
			Column(constants.COLUMN_TEXT, constants.COLUMN_WIDTH_TEXT, constants.KEY_STRING_TO_REPLACE),
			Column(constants.COLUMN_RULE_TYPE, constants.COLUMN_WIDTH_RULE_TYPE,
				lambda item: _RULE_TYPE_LABELS.get(item[constants.KEY_RULE_TYPE], item[constants.KEY_RULE_TYPE])),
			Column(constants.COLUMN_REPLACEMENT, constants.COLUMN_WIDTH_REPLACEMENT, constants.KEY_REPLACEMENT),
			Column(constants.COLUMN_ALPHABET, constants.COLUMN_WIDTH_ALPHABET,
				lambda item: _ALPHABET_LABELS.get(item[constants.KEY_ALPHABET], item[constants.KEY_ALPHABET])),
			Column(constants.COLUMN_OPTIONS, constants.COLUMN_WIDTH_OPTIONS, constants.KEY_OPTIONS),
		])
		self.rule_buttons = []
		self.add_rule_button = self._create_button(constants.LABEL_ADD_RULE, self.rule_buttons)
		self.remove_rule_button = self._create_button(constants.LABEL_REMOVE_RULE, self.rule_buttons)
		self.close_buttons = []
		self.close_button = self._create_button(constants.LABEL_CLOSE, self.close_buttons, wx.ID_CLOSE)
		self.status_text = StatusText(self, constants.STATUS_LOADING, constants.LABEL_STATUS)

	def _create_button(self, label, button_group, button_id=wx.ID_ANY):
		# Each button is preceded by a matching label, as in the other ElevenDesk dialogs.
		button_label = wx.StaticText(self, label=label)
		button = wx.Button(self, button_id, label, name=label)
		button_group.append((button_label, button))
		return button

	def _add_button_row(self, sizer, button_group):
		row_sizer = wx.WrapSizer(wx.HORIZONTAL)
		for label, button in button_group:
			row_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			row_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT | wx.BOTTOM, constants.SECTION_GAP)
		sizer.Add(row_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.dictionary_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.dictionary_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.use_in_tts_checkbox, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		self._add_button_row(main_sizer, self.dictionary_buttons)
		main_sizer.Add(self.rule_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.rule_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		self._add_button_row(main_sizer, self.rule_buttons)
		self._add_button_row(main_sizer, self.close_buttons)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _bind_events(self):
		lists.bind_selection_changed(self.dictionary_list, self._on_dictionary_selected)
		lists.bind_key_down(self.rule_list, self._on_rule_key)
		self.use_in_tts_checkbox.Bind(wx.EVT_CHECKBOX, self._on_use_in_tts)
		self.new_button.Bind(wx.EVT_BUTTON, self._on_new)
		self.import_button.Bind(wx.EVT_BUTTON, self._on_import)
		self.rename_button.Bind(wx.EVT_BUTTON, self._on_rename)
		self.archive_button.Bind(wx.EVT_BUTTON, self._on_archive)
		self.download_button.Bind(wx.EVT_BUTTON, self._on_download)
		self.add_rule_button.Bind(wx.EVT_BUTTON, self._on_add_rule)
		self.remove_rule_button.Bind(wx.EVT_BUTTON, self._on_remove_rule)
		self.close_button.Bind(wx.EVT_BUTTON, self._on_close_button)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)

	def _set_tab_order(self):
		controls = (
			self.dictionary_list.control.control,
			self.use_in_tts_checkbox,
			self.new_button,
			self.import_button,
			self.rename_button,
			self.archive_button,
			self.download_button,
			self.rule_list.control.control,
			self.add_rule_button,
			self.remove_rule_button,
			self.close_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def _on_close_button(self, event):
		self.Close()

	def _on_key_hook(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		event.Skip()

	def _run_request(self, worker, on_success, *arguments):
		# Runs an API call off the UI thread; failures are reported in (and announced from) the status line.
		self.status_text.SetLabel(constants.STATUS_WORKING)

		def run():
			try:
				result = worker(*arguments)
			except api.ElevenDeskAPIError as error:
				wx.CallAfter(self._request_failed, str(error))
				return
			wx.CallAfter(self._request_succeeded, on_success, result)

		threading.Thread(target=run, daemon=constants.THREAD_DAEMON).start()

	def _request_succeeded(self, on_success, result):
		if self:
			on_success(result)

	def _request_failed(self, message):
		if self:
			self.status_text.ReportFailure(message)

	def _load_dictionaries(self, select_id=None, status_message=None):
		self._run_request(
			api.get_pronunciation_dictionaries,
			lambda dictionaries: self._set_dictionaries(dictionaries, select_id, status_message),
		)

	def _set_dictionaries(self, dictionaries, select_id, status_message):
		# Dictionaries archived or deleted elsewhere would make every speech request fail, so they are forgotten.
		existing_ids = {dictionary[constants.KEY_ID] for dictionary in dictionaries}
		kept_ids = [dictionary_id for dictionary_id in self.tts_dictionary_ids if dictionary_id in existing_ids]
		if kept_ids != self.tts_dictionary_ids:
			self._save_tts_dictionary_ids(kept_ids)
		if select_id is None:
			selected = lists.get_selected_item(self.dictionary_list)
			select_id = selected[constants.KEY_ID] if selected else None
		for dictionary in dictionaries:
			dictionary[constants.KEY_USED_IN_TTS] = self._tts_marker(dictionary[constants.KEY_ID])
		self.dictionary_list.clear()
		self.rule_list.clear()
		self.dictionary_list.add_items(dictionaries)
		if not dictionaries:
			self.use_in_tts_checkbox.SetValue(False)
			message = status_message or constants.STATUS_NO_PRONUNCIATION_DICTIONARIES
			self.status_text.SetLabel(message)
			# An empty list gives a screen reader nothing to say, so the empty state is announced.
			announce(message)
			return
		select_index = constants.FIRST_ITEM_INDEX
		for index, dictionary in enumerate(dictionaries):
			if dictionary[constants.KEY_ID] == select_id:
				select_index = index
		self.pending_status_message = status_message or constants.STATUS_DICTIONARIES_LOADED_TEMPLATE.format(len(dictionaries))
		self.dictionary_list.set_selected_index(select_index)

	def _tts_marker(self, dictionary_id):
		return constants.DICTIONARY_IN_TTS if dictionary_id in self.tts_dictionary_ids else constants.EMPTY_TEXT

	def _selected_dictionary(self):
		dictionary = lists.get_selected_item(self.dictionary_list)
		if dictionary is None:
			self.status_text.ReportFailure(constants.ERROR_DICTIONARY_SELECTION_REQUIRED)
		return dictionary

	def _on_dictionary_selected(self, event):
		event.Skip()
		dictionary = lists.get_selected_item(self.dictionary_list)
		if dictionary is None:
			return
		self.use_in_tts_checkbox.SetValue(dictionary[constants.KEY_ID] in self.tts_dictionary_ids)
		self._load_rules(dictionary)

	def _load_rules(self, dictionary, status_message=None):
		self.rules_request_id += 1
		request_id = self.rules_request_id
		self.rule_list.clear()
		self.status_text.SetLabel(constants.STATUS_LOADING_RULES)

		def run():
			try:
				rules = api.get_pronunciation_rules(dictionary[constants.KEY_ID])
			except api.ElevenDeskAPIError as error:
				wx.CallAfter(self._rules_failed, request_id, str(error))
				return
			wx.CallAfter(self._set_rules, request_id, dictionary, rules, status_message)

		threading.Thread(target=run, daemon=constants.THREAD_DAEMON).start()

	def _rules_failed(self, request_id, message):
		if self and request_id == self.rules_request_id:
			self.status_text.ReportFailure(message)

	def _set_rules(self, request_id, dictionary, rules, status_message):
		# Selecting another dictionary while rules load starts a newer request, so older results are dropped.
		if not self or request_id != self.rules_request_id:
			return
		self.rule_list.clear()
		self.rule_list.add_items(rules)
		if rules:
			self.rule_list.set_selected_index(constants.FIRST_ITEM_INDEX)
		message = status_message or self.pending_status_message
		self.pending_status_message = None
		rules_message = constants.STATUS_RULES_LOADED_TEMPLATE.format(dictionary[constants.KEY_NAME], len(rules))
		self.status_text.SetLabel(message + constants.SPACE + rules_message if message else rules_message)

	def _save_tts_dictionary_ids(self, dictionary_ids):
		try:
			config.save_tts_pronunciation_dictionary_ids(dictionary_ids)
		except OSError as error:
			self.status_text.ReportFailure(str(error))
			return False
		self.tts_dictionary_ids = list(dictionary_ids)
		return True

	def _on_use_in_tts(self, event):
		dictionary = self._selected_dictionary()
		use_dictionary = self.use_in_tts_checkbox.GetValue()
		if dictionary is None:
			self.use_in_tts_checkbox.SetValue(False)
			return
		dictionary_id = dictionary[constants.KEY_ID]
		dictionary_ids = [existing_id for existing_id in self.tts_dictionary_ids if existing_id != dictionary_id]
		if use_dictionary:
			# The API accepts only a few pronunciation dictionaries per speech request.
			if len(dictionary_ids) >= constants.TTS_MAX_PRONUNCIATION_DICTIONARIES:
				self.use_in_tts_checkbox.SetValue(False)
				self.status_text.ReportFailure(
					constants.ERROR_TTS_DICTIONARY_LIMIT_TEMPLATE.format(constants.TTS_MAX_PRONUNCIATION_DICTIONARIES)
				)
				return
			dictionary_ids.append(dictionary_id)
		if not self._save_tts_dictionary_ids(dictionary_ids):
			self.use_in_tts_checkbox.SetValue(not use_dictionary)
			return
		updated = dict(dictionary)
		updated[constants.KEY_USED_IN_TTS] = self._tts_marker(dictionary_id)
		self.dictionary_list.update_item(updated, dictionary)
		template = constants.STATUS_TTS_DICTIONARY_ON_TEMPLATE if use_dictionary else constants.STATUS_TTS_DICTIONARY_OFF_TEMPLATE
		self.status_text.SetLabel(template.format(dictionary[constants.KEY_NAME]))

	def _on_new(self, event):
		with PronunciationRuleDialog(self, ask_for_dictionary=True) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			name = dialog.get_dictionary_name()
			description = dialog.get_dictionary_description()
			rule = dialog.get_rule()
		self._run_request(
			api.create_pronunciation_dictionary,
			self._dictionary_created,
			name,
			description,
			rule,
		)

	def _dictionary_created(self, dictionary):
		self._load_dictionaries(
			select_id=dictionary[constants.KEY_ID],
			status_message=constants.STATUS_DICTIONARY_CREATED_TEMPLATE.format(dictionary[constants.KEY_NAME]),
		)

	def _on_import(self, event):
		with wx.FileDialog(
			self,
			message=constants.TITLE_IMPORT_DICTIONARY,
			wildcard=constants.PLS_FILE_WILDCARD,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			file_path = dialog.GetPath()
		default_name = os.path.splitext(os.path.basename(file_path))[constants.FIRST_ITEM_INDEX]
		name = self._ask_for_name(constants.TITLE_NEW_DICTIONARY, default_name)
		if name:
			self._run_request(
				api.import_pronunciation_dictionary,
				self._dictionary_created,
				name,
				constants.EMPTY_TEXT,
				file_path,
			)

	def _ask_for_name(self, title, default_name):
		with wx.TextEntryDialog(self, constants.LABEL_DICTIONARY_NAME, title, default_name) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return None
			name = dialog.GetValue().strip()
		if not name:
			self.status_text.ReportFailure(constants.ERROR_DICTIONARY_NAME_REQUIRED)
		return name

	def _on_rename(self, event):
		dictionary = self._selected_dictionary()
		if dictionary is None:
			return
		name = self._ask_for_name(constants.TITLE_RENAME_DICTIONARY, dictionary[constants.KEY_NAME])
		if not name or name == dictionary[constants.KEY_NAME]:
			return
		self._run_request(
			api.rename_pronunciation_dictionary,
			lambda result: self._load_dictionaries(
				select_id=dictionary[constants.KEY_ID],
				status_message=constants.STATUS_DICTIONARY_RENAMED_TEMPLATE.format(name),
			),
			dictionary[constants.KEY_ID],
			name,
		)

	def _on_archive(self, event):
		dictionary = self._selected_dictionary()
		if dictionary is None:
			return
		answer = wx.MessageBox(
			constants.CONFIRM_ARCHIVE_DICTIONARY_TEMPLATE.format(dictionary[constants.KEY_NAME]),
			constants.TITLE_ARCHIVE_DICTIONARY,
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
			self,
		)
		if answer != wx.YES:
			return
		self._run_request(
			api.archive_pronunciation_dictionary,
			lambda result: self._load_dictionaries(
				status_message=constants.STATUS_DICTIONARY_ARCHIVED_TEMPLATE.format(dictionary[constants.KEY_NAME]),
			),
			dictionary[constants.KEY_ID],
		)

	def _on_download(self, event):
		dictionary = self._selected_dictionary()
		if dictionary is None:
			return
		with wx.FileDialog(
			self,
			message=constants.TITLE_SAVE_DICTIONARY,
			defaultDir=config.load_config()[constants.KEY_OUTPUT_DIRECTORY],
			defaultFile=dictionary[constants.KEY_NAME] + constants.EXTENSION_PLS,
			wildcard=constants.PLS_FILE_WILDCARD,
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			file_path = dialog.GetPath()
		self._run_request(
			api.download_pronunciation_dictionary,
			lambda dictionary_bytes: self._write_dictionary_file(file_path, dictionary_bytes),
			dictionary[constants.KEY_ID],
			dictionary[constants.KEY_VERSION_ID],
		)

	def _write_dictionary_file(self, file_path, dictionary_bytes):
		try:
			with open(file_path, constants.FILE_MODE_BINARY_WRITE) as dictionary_file:
				dictionary_file.write(dictionary_bytes)
		except OSError as error:
			self.status_text.ReportFailure(str(error))
			return
		self.status_text.SetLabel(constants.STATUS_DICTIONARY_DOWNLOADED + file_path)

	def _on_add_rule(self, event):
		dictionary = self._selected_dictionary()
		if dictionary is None:
			return
		with PronunciationRuleDialog(self) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			rule = dialog.get_rule()
		self._run_request(
			api.add_pronunciation_rule,
			lambda result: self._load_dictionaries(
				select_id=dictionary[constants.KEY_ID],
				status_message=constants.STATUS_RULE_ADDED_TEMPLATE.format(rule[constants.KEY_STRING_TO_REPLACE]),
			),
			dictionary[constants.KEY_ID],
			rule,
		)

	def _on_rule_key(self, event):
		if lists.is_delete_key(event):
			self._on_remove_rule(event)
			return
		event.Skip()

	def _on_remove_rule(self, event):
		dictionary = self._selected_dictionary()
		if dictionary is None:
			return
		rule = lists.get_selected_item(self.rule_list)
		if rule is None:
			self.status_text.ReportFailure(constants.ERROR_RULE_SELECTION_REQUIRED)
			return
		text = rule[constants.KEY_STRING_TO_REPLACE]
		answer = wx.MessageBox(
			constants.CONFIRM_REMOVE_RULE_TEMPLATE.format(text),
			constants.TITLE_REMOVE_RULE,
			wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
			self,
		)
		if answer != wx.YES:
			return
		self._run_request(
			api.remove_pronunciation_rule,
			lambda result: self._load_dictionaries(
				select_id=dictionary[constants.KEY_ID],
				status_message=constants.STATUS_RULE_REMOVED_TEMPLATE.format(text),
			),
			dictionary[constants.KEY_ID],
			text,
		)
