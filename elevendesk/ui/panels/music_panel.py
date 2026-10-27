import threading

import wx

from elevendesk import api
from elevendesk import constants
from elevendesk import music_plan
from elevendesk import playback
from elevendesk import usage
from elevendesk.ui import choices
from elevendesk.ui.status_text import StatusText, announce

_RETURN_KEYS = (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER)


class MusicPanel(wx.Panel):
	# With an empty plan the description is sent as a prompt; once the plan has text, the plan is sent instead.

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.last_audio = None
		self.last_output_format = constants.MUSIC_OUTPUT_FORMAT
		self.finetunes = []
		self.finetunes_requested = False
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()

	def _create_controls(self):
		self.prompt_label = wx.StaticText(self, label=constants.LABEL_MUSIC_PROMPT)
		self.prompt_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, name=constants.LABEL_MUSIC_PROMPT)
		self.prompt_input.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.RESULT_MIN_HEIGHT))
		self.model_label = wx.StaticText(self, label=constants.LABEL_MODEL)
		self.model_combo = choices.create_choice(
			self,
			choices=[label for label, _ in constants.MUSIC_MODELS],
			name=constants.LABEL_MODEL,
		)
		self.model_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.length_label = wx.StaticText(self, label=constants.LABEL_MUSIC_LENGTH)
		self.length_input = wx.SpinCtrl(
			self,
			min=constants.MUSIC_LENGTH_AUTO,
			max=constants.MUSIC_LENGTH_MAXIMUM,
			initial=constants.MUSIC_LENGTH_AUTO,
			name=constants.LABEL_MUSIC_LENGTH,
		)
		self.instrumental_checkbox = wx.CheckBox(self, label=constants.LABEL_INSTRUMENTAL)
		self.finetune_label = wx.StaticText(self, label=constants.LABEL_MUSIC_FINETUNE)
		self.finetune_combo = choices.create_choice(
			self,
			choices=[constants.LABEL_NO_FINETUNE],
			name=constants.LABEL_MUSIC_FINETUNE,
		)
		self.finetune_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.plan_label = wx.StaticText(self, label=constants.LABEL_MUSIC_PLAN)
		self.plan_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, name=constants.LABEL_MUSIC_PLAN)
		self.plan_input.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.TEXT_MIN_HEIGHT))
		self.create_plan_label = wx.StaticText(self, label=constants.LABEL_CREATE_PLAN)
		self.create_plan_button = wx.Button(self, label=constants.LABEL_CREATE_PLAN, name=constants.NAME_CREATE_MUSIC_PLAN)
		self.generate_label = wx.StaticText(self, label=constants.LABEL_GENERATE)
		self.generate_button = wx.Button(self, label=constants.LABEL_GENERATE, name=constants.NAME_GENERATE_MUSIC_SHORTCUT)
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(self, label=constants.LABEL_PLAY, name=constants.NAME_PLAY_GENERATED_MUSIC)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, label=constants.LABEL_SAVE, name=constants.NAME_SAVE_GENERATED_MUSIC)
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = StatusText(self, constants.STATUS_READY, constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.prompt_label, self.prompt_input),
			(self.model_label, self.model_combo),
			(self.length_label, self.length_input),
			(None, self.instrumental_checkbox),
			(self.finetune_label, self.finetune_combo),
			(self.plan_label, self.plan_input),
		):
			if label is not None:
				main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.plan_input else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.create_plan_label, self.create_plan_button),
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
		self.create_plan_button.Bind(wx.EVT_BUTTON, self._on_create_plan)
		self.generate_button.Bind(wx.EVT_BUTTON, self._on_generate)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)

	def _set_tab_order(self):
		controls = (
			self.prompt_input,
			self.model_combo,
			self.length_input,
			self.instrumental_checkbox,
			self.finetune_combo,
			self.plan_input,
			self.create_plan_button,
			self.generate_button,
			self.play_button,
			self.save_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def load_finetunes(self):
		# Fetched the first time the tab is shown, so startup makes no extra request.
		if self.finetunes_requested:
			return
		self.finetunes_requested = True
		threading.Thread(target=self._load_finetunes_worker, daemon=constants.THREAD_DAEMON).start()

	def _load_finetunes_worker(self):
		try:
			finetunes = api.get_music_finetunes()
		except api.ElevenDeskAPIError:
			# Finetunes are optional, so a failure just leaves "None" and allows a retry next time.
			self.finetunes_requested = False
			return
		wx.CallAfter(self._set_finetunes, finetunes)

	def _set_finetunes(self, finetunes):
		if not self:
			return
		self.finetunes = finetunes
		selection = self.finetune_combo.GetSelection()
		self.finetune_combo.Clear()
		self.finetune_combo.Append(constants.LABEL_NO_FINETUNE)
		for finetune in finetunes:
			self.finetune_combo.Append(finetune[constants.KEY_NAME])
		if selection == wx.NOT_FOUND or selection > len(finetunes):
			selection = constants.FIRST_ITEM_INDEX
		self.finetune_combo.SetSelection(selection)

	def _selected_model_id(self):
		index = choices.get_selected_index(self.model_combo, constants.MUSIC_MODELS)
		if index == wx.NOT_FOUND:
			index = constants.FIRST_ITEM_INDEX
		return constants.MUSIC_MODELS[index][constants.INDEX_STEP]

	def _selected_finetune_id(self):
		# Index 0 is "None", so finetunes start at index 1.
		index = self.finetune_combo.GetSelection() - constants.INDEX_STEP
		if constants.FIRST_ITEM_INDEX <= index < len(self.finetunes):
			return self.finetunes[index][constants.KEY_ID]
		return None

	def _plan_allowed(self):
		return self._selected_model_id() in constants.MUSIC_PLAN_MODELS

	def _on_model_selected(self, event):
		allowed = self._plan_allowed()
		self.plan_input.Enable(allowed)
		self.create_plan_button.Enable(allowed)
		self.plan_label.SetLabel(constants.LABEL_MUSIC_PLAN if allowed else constants.LABEL_MUSIC_PLAN_V2_ONLY)
		self.plan_input.SetName(self.plan_label.GetLabel())

	def _length_ms(self):
		# Returns None for "model chooses", or raises ValueError when the length is out of range.
		seconds = self.length_input.GetValue()
		if seconds == constants.MUSIC_LENGTH_AUTO:
			return None
		if seconds < constants.MUSIC_LENGTH_MINIMUM:
			raise ValueError(constants.ERROR_MUSIC_LENGTH_RANGE_TEMPLATE.format(
				constants.MUSIC_LENGTH_MINIMUM,
				constants.MUSIC_LENGTH_MAXIMUM,
			))
		return seconds * constants.MILLISECONDS_PER_SECOND

	def _set_busy(self, busy):
		self.generate_button.Enable(not busy)
		self.create_plan_button.Enable(not busy and self._plan_allowed())

	def _on_key_hook(self, event):
		if event.ControlDown() and event.GetKeyCode() in _RETURN_KEYS and self.generate_button.IsEnabled():
			self._on_generate(event)
			return
		event.Skip()

	def _on_create_plan(self, event):
		prompt = self.prompt_input.GetValue().strip()
		if not prompt:
			self.status_text.ReportFailure(constants.ERROR_MUSIC_PLAN_PROMPT_REQUIRED)
			return
		try:
			length_ms = self._length_ms()
		except ValueError as error:
			self.status_text.ReportFailure(str(error))
			return
		self._set_busy(True)
		self.status_text.SetLabel(constants.STATUS_CREATING_MUSIC_PLAN)
		threading.Thread(
			target=self._create_plan_worker,
			args=(prompt, self._selected_model_id(), length_ms),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _create_plan_worker(self, prompt, model_id, length_ms):
		try:
			chunks = api.create_music_plan(prompt, model_id, length_ms)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._request_failed, error)
			return
		wx.CallAfter(self._plan_created, chunks)

	def _plan_created(self, chunks):
		self._set_busy(False)
		self.plan_input.SetValue(music_plan.format_plan(chunks))
		message = constants.STATUS_MUSIC_PLAN_READY_TEMPLATE.format(*music_plan.format_summary(chunks))
		self.status_text.SetLabel(message)
		announce(message)

	def _on_generate(self, event):
		model_id = self._selected_model_id()
		plan_text = self.plan_input.GetValue().strip() if self._plan_allowed() else constants.EMPTY_TEXT
		prompt = self.prompt_input.GetValue().strip()
		keyword_arguments = {constants.API_KW_FINETUNE_ID: self._selected_finetune_id()}
		if plan_text:
			try:
				chunks = music_plan.parse(plan_text)
			except music_plan.MusicPlanError as error:
				self.status_text.ReportFailure(str(error))
				return
			keyword_arguments[constants.KEY_PLAN_CHUNKS] = chunks
			status = constants.STATUS_GENERATING_MUSIC_PLAN_TEMPLATE.format(*music_plan.format_summary(chunks))
		elif prompt:
			try:
				keyword_arguments[constants.KEY_LENGTH_MS] = self._length_ms()
			except ValueError as error:
				self.status_text.ReportFailure(str(error))
				return
			keyword_arguments[constants.API_KW_PROMPT] = prompt
			keyword_arguments[constants.KEY_INSTRUMENTAL] = self.instrumental_checkbox.GetValue()
			status = constants.STATUS_GENERATING_MUSIC
		else:
			self.status_text.ReportFailure(constants.ERROR_MUSIC_PROMPT_REQUIRED)
			return
		self._set_busy(True)
		self.status_text.SetLabel(status)
		threading.Thread(
			target=self._generate_worker,
			args=(model_id, keyword_arguments),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _generate_worker(self, model_id, keyword_arguments):
		try:
			audio_bytes = api.compose_music(model_id, **keyword_arguments)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._request_failed, error)
			return
		wx.CallAfter(self._generation_succeeded, audio_bytes)

	def _generation_succeeded(self, audio_bytes):
		usage.refresh()
		self.last_audio = audio_bytes
		self._set_busy(False)
		self.play_button.Enable()
		self.save_button.Enable()
		# Songs take a while, so the result is spoken in case focus has moved on.
		self.status_text.SetLabel(constants.STATUS_MUSIC_GENERATED)
		announce(constants.STATUS_MUSIC_GENERATED)

	def _request_failed(self, error):
		self._set_busy(False)
		# A suggestion replaces the rejected text, selected, so Generate retries it and typing replaces it.
		if isinstance(error, api.MusicRejectedError):
			if error.prompt_suggestion:
				self.prompt_input.SetValue(error.prompt_suggestion)
				self.prompt_input.SelectAll()
			elif error.plan_suggestion:
				self.plan_input.SetValue(music_plan.format_plan(error.plan_suggestion))
		self.status_text.ReportFailure(str(error))

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
