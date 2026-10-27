import threading

import wx

from elevendesk import api
from elevendesk import config
from elevendesk import constants
from elevendesk import dialogue_script
from elevendesk import playback
from elevendesk import usage
from elevendesk.ui import choices
from elevendesk.ui.status_text import StatusText, announce

_RETURN_KEYS = (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER)
_UP_KEYS = (wx.WXK_UP, wx.WXK_NUMPAD_UP)
_DOWN_KEYS = (wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN)
_LEFT_RIGHT_KEYS = (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_NUMPAD_LEFT, wx.WXK_NUMPAD_RIGHT)


class DialoguePanel(wx.Panel):
	# Voices come from the Text to Speech panel, whose selected voice also speaks any text before the first tag.

	def __init__(self, parent, tts_panel):
		wx.Panel.__init__(self, parent)
		self.tts_panel = tts_panel
		self.models = []
		self.requested_model_id = constants.MODEL_ELEVEN_V3
		self.last_audio = None
		self.last_output_format = constants.DEFAULT_OUTPUT_FORMAT
		# Voices offered for the "@" tag being typed; None while no suggestion list is open.
		self.suggestions = None
		self.suggestion_index = constants.FIRST_ITEM_INDEX
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()
		self.apply_defaults()

	def _create_controls(self):
		self.script_label = wx.StaticText(self, label=constants.LABEL_SCRIPT)
		self.script_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, name=constants.LABEL_SCRIPT)
		self.script_input.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.TEXT_MIN_HEIGHT))
		self.model_label = wx.StaticText(self, label=constants.LABEL_MODEL)
		self.model_combo = choices.create_choice(self, name=constants.LABEL_MODEL)
		self.output_format_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_FORMAT)
		self.output_format_combo = choices.create_choice(self, choices=list(constants.OUTPUT_FORMATS), name=constants.LABEL_OUTPUT_FORMAT)
		self.stability_label = wx.StaticText(self, label=constants.LABEL_STABILITY)
		self.stability_slider = wx.Slider(
			self,
			value=constants.SLIDER_DEFAULT_STABILITY,
			minValue=constants.SLIDER_MINIMUM,
			maxValue=constants.SLIDER_MAXIMUM,
			name=constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_STABILITY, constants.SLIDER_DEFAULT_STABILITY),
		)
		self.stability_value = wx.StaticText(
			self,
			label=constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_STABILITY, constants.SLIDER_DEFAULT_STABILITY),
		)
		self.generate_label = wx.StaticText(self, label=constants.LABEL_GENERATE)
		self.generate_button = wx.Button(self, label=constants.LABEL_GENERATE, name=constants.NAME_GENERATE_DIALOGUE_SHORTCUT)
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(self, label=constants.LABEL_PLAY, name=constants.NAME_PLAY_GENERATED_DIALOGUE)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, label=constants.LABEL_SAVE, name=constants.NAME_SAVE_GENERATED_DIALOGUE)
		self.generate_button.Disable()
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = StatusText(self, constants.STATUS_READY, constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.script_label, self.script_input),
			(self.model_label, self.model_combo),
			(self.output_format_label, self.output_format_combo),
			(self.stability_label, self.stability_slider),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.script_input else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.stability_value, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.generate_label, self.generate_button),
			(self.play_label, self.play_button),
			(self.save_label, self.save_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _bind_events(self):
		choices.bind_selection(self.model_combo, self._on_model_selected)
		self.stability_slider.Bind(wx.EVT_SLIDER, self._on_stability)
		self.script_input.Bind(wx.EVT_TEXT, self._on_script_text)
		self.script_input.Bind(wx.EVT_KILL_FOCUS, self._on_script_focus_lost)
		for caret_event in (wx.EVT_KEY_UP, wx.EVT_LEFT_UP, wx.EVT_SET_FOCUS):
			self.script_input.Bind(caret_event, self._on_script_caret_moved)
		self.generate_button.Bind(wx.EVT_BUTTON, self._on_generate)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)

	def _set_tab_order(self):
		controls = (
			self.script_input,
			self.model_combo,
			self.output_format_combo,
			self.stability_slider,
			self.generate_button,
			self.play_button,
			self.save_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def apply_defaults(self):
		selection = self.output_format_combo.FindString(config.load_config()[constants.KEY_DEFAULT_OUTPUT_FORMAT])
		if selection == wx.NOT_FOUND:
			selection = constants.FIRST_ITEM_INDEX
		self.output_format_combo.SetSelection(selection)

	def set_models(self, models):
		self.models = models
		choices.set_model_choices(self.model_combo, self.models, self.requested_model_id)
		self.generate_button.Enable(bool(self.models))

	def show_models_placeholder(self, text):
		self.models = []
		choices.show_placeholder(self.model_combo, text)
		self.generate_button.Disable()

	def _on_model_selected(self, event):
		model_id = choices.get_selected_model_id(self.model_combo, self.models)
		if model_id:
			self.requested_model_id = model_id

	def _on_stability(self, event):
		value = self.stability_slider.GetValue()
		self.stability_value.SetLabel(constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_STABILITY, value))
		self.stability_slider.SetName(constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_STABILITY, value))

	# The script helpers work on GetValue() indexes. A plain multiline control on Windows counts each line break
	# as two positions, so indexes are converted before moving the caret or replacing text.

	def _get_script(self):
		text = self.script_input.GetValue()
		caret = len(self.script_input.GetRange(0, self.script_input.GetInsertionPoint()))
		return text, caret

	def _position_from_index(self, text, index):
		if self.script_input.GetLastPosition() == len(text):
			return index
		return index + text.count(constants.NEWLINE, 0, index)

	def _replace_script_text(self, text, start, end, replacement):
		self.script_input.Replace(
			self._position_from_index(text, start),
			self._position_from_index(text, end),
			replacement,
		)
		new_text = self.script_input.GetValue()
		self.script_input.SetInsertionPoint(self._position_from_index(new_text, start + len(replacement)))
		self.update_script_position()

	def _default_voice(self):
		return self.tts_panel.get_selected_voice()

	# The caret's line and column go on the window's status bar, where a screen reader's read status bar command
	# finds them. Line numbers match the ones in script errors.

	def update_script_position(self):
		text, caret = self._get_script()
		line_start, _ = dialogue_script.line_bounds(text, caret)
		self.GetTopLevelParent().SetStatusText(constants.STATUS_BAR_SCRIPT_POSITION_TEMPLATE.format(
			dialogue_script.line_index_at(text, caret) + constants.INDEX_STEP,
			text.count(constants.NEWLINE) + constants.INDEX_STEP,
			caret - line_start + constants.INDEX_STEP,
		))

	def _on_script_caret_moved(self, event):
		event.Skip()
		self.update_script_position()

	# Voice tag suggestions. They are spoken through the screen reader rather than shown in a popup,
	# so focus never leaves the script.

	def _on_script_text(self, event):
		event.Skip()
		self.update_script_position()
		text, caret = self._get_script()
		partial = dialogue_script.partial_tag_at(text, caret)
		if partial is None:
			self._close_suggestions()
			return
		voices = dialogue_script.matching_voices(partial, self.tts_panel.voices)
		if not voices:
			if self.suggestions != []:
				self.suggestions = []
				self._show_suggestion_status(constants.STATUS_NO_MATCHING_VOICES)
			return
		if self.suggestions == voices:
			return
		self.suggestions = voices
		self.suggestion_index = constants.FIRST_ITEM_INDEX
		self._announce_suggestion()

	def _announce_suggestion(self):
		voice = self.suggestions[self.suggestion_index]
		self._show_suggestion_status(constants.STATUS_SUGGESTION_TEMPLATE.format(
			voice[constants.KEY_NAME],
			self.suggestion_index + constants.INDEX_STEP,
			len(self.suggestions),
		))

	def _show_suggestion_status(self, message):
		self.status_text.SetLabel(message)
		announce(message)

	def _close_suggestions(self):
		if self.suggestions is None:
			return
		self.suggestions = None
		self.status_text.SetLabel(constants.STATUS_READY)

	def _move_suggestion(self, step):
		self.suggestion_index = (self.suggestion_index + step) % len(self.suggestions)
		self._announce_suggestion()

	def _accept_suggestion(self):
		# Returns False when there is nothing to accept, so the key can do its usual job instead.
		text, caret = self._get_script()
		if not self.suggestions or dialogue_script.partial_tag_at(text, caret) is None:
			self._close_suggestions()
			return False
		voice = self.suggestions[self.suggestion_index]
		start, end, replacement = dialogue_script.suggestion_edit(text, caret, voice, self.tts_panel.voices)
		self._close_suggestions()
		self._replace_script_text(text, start, end, replacement)
		announce(dialogue_script.tag_name_for_voice(voice, self.tts_panel.voices))
		return True

	def _on_script_focus_lost(self, event):
		event.Skip()
		self._close_suggestions()

	def _insert_next_speaker(self):
		text, caret = self._get_script()
		default_voice = self._default_voice()
		default_tag = None
		if default_voice:
			default_tag = dialogue_script.tag_name_for_voice(default_voice, self.tts_panel.voices)
		edit = dialogue_script.next_speaker_edit(text, caret, default_tag)
		if edit is None:
			return
		position, insertion = edit
		self._replace_script_text(text, position, position, insertion)
		speaker = insertion.strip()[len(constants.DIALOGUE_TAG_PREFIX):-len(constants.DIALOGUE_TAG_END)]
		if speaker:
			announce(speaker)

	def _on_key_hook(self, event):
		key_code = event.GetKeyCode()
		is_return = key_code in _RETURN_KEYS
		has_modifier = event.ControlDown() or event.AltDown() or event.ShiftDown()
		if event.ControlDown() and is_return:
			if self.generate_button.IsEnabled():
				self._start_generation()
			return
		if wx.Window.FindFocus() is not self.script_input:
			event.Skip()
			return
		if self.suggestions is not None and not has_modifier:
			if key_code == wx.WXK_TAB or is_return:
				if self._accept_suggestion():
					return
			elif key_code in _UP_KEYS and self.suggestions:
				self._move_suggestion(-constants.INDEX_STEP)
				return
			elif key_code in _DOWN_KEYS and self.suggestions:
				self._move_suggestion(constants.INDEX_STEP)
				return
			elif key_code == wx.WXK_ESCAPE:
				self._close_suggestions()
				return
			elif key_code in _LEFT_RIGHT_KEYS:
				self._close_suggestions()
		if is_return and event.ShiftDown() and not event.AltDown():
			self._insert_next_speaker()
			return
		event.Skip()

	def _on_generate(self, event):
		self._start_generation()

	def _start_generation(self):
		self._close_suggestions()
		if not self.tts_panel.voices:
			self.status_text.ReportFailure(constants.ERROR_DIALOGUE_VOICES_NOT_LOADED)
			return
		text = self.script_input.GetValue()
		try:
			inputs = dialogue_script.parse_script(text, self.tts_panel.voices, self._default_voice())
		except dialogue_script.ScriptError as error:
			error_index = dialogue_script.line_start_index(text, error.line_index) + error.column
			self.script_input.SetFocus()
			self.script_input.SetInsertionPoint(self._position_from_index(text, error_index))
			self.update_script_position()
			self.status_text.ReportFailure(str(error))
			return
		model_id = choices.get_selected_model_id(self.model_combo, self.models)
		output_format = self.output_format_combo.GetStringSelection()
		stability = self.stability_slider.GetValue() / constants.PERCENT_DIVISOR
		voice_count = len({dialogue_input[constants.API_KW_VOICE_ID] for dialogue_input in inputs})
		character_count = sum(len(dialogue_input[constants.API_KW_TEXT]) for dialogue_input in inputs)
		self.generate_button.Disable()
		self.status_text.SetLabel(constants.STATUS_GENERATING_DIALOGUE_TEMPLATE.format(len(inputs), voice_count, character_count))
		threading.Thread(
			target=self._generate_worker,
			args=(inputs, model_id, stability, output_format, config.load_tts_pronunciation_dictionary_ids()),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _generate_worker(self, inputs, model_id, stability, output_format, pronunciation_dictionary_ids):
		try:
			audio_bytes = api.text_to_dialogue(inputs, model_id, stability, output_format, pronunciation_dictionary_ids)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._generation_failed, str(error))
			return
		wx.CallAfter(self._generation_succeeded, audio_bytes, output_format)

	def _generation_succeeded(self, audio_bytes, output_format):
		usage.refresh()
		self.last_audio = audio_bytes
		self.last_output_format = output_format
		self.generate_button.Enable(bool(self.models))
		self.play_button.Enable()
		self.save_button.Enable()
		self._on_play(None)

	def _generation_failed(self, message):
		self.generate_button.Enable(bool(self.models))
		self.status_text.ReportFailure(message)

	def _on_play(self, event):
		if self.last_audio:
			playback.play_audio(
				self.last_audio,
				self.last_output_format,
				on_finished=self.status_text.ShowPlayback(constants.STATUS_PLAYING),
			)

	def _on_save(self, event):
		self.GetTopLevelParent().save_audio_bytes(self.last_audio, self.last_output_format, self.status_text)

	def get_last_output(self):
		return self.last_audio, self.last_output_format
