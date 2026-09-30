import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import constants
from elevendesk import playback
from elevendesk import usage
from elevendesk.ui import choices
from elevendesk.ui import lists
from elevendesk.ui.status_text import StatusText


class VoiceLibraryDialog(wx.Dialog):
	def __init__(self, parent, tts_panel, sts_panel):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_VOICE_LIBRARY, size=constants.DIALOG_SIZE)
		self.tts_panel = tts_panel
		self.sts_panel = sts_panel
		self.voices = []
		self.community_page = constants.FIRST_ITEM_INDEX
		# Each load gets a new number so results from an older search that arrive late are ignored.
		self.load_request = constants.FIRST_ITEM_INDEX
		self.preview_cache = {}
		self.preview_thread = None
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()
		self._update_mode_controls()
		self._load_voices()

	def _create_controls(self):
		self.source_label = wx.StaticText(self, label=constants.LABEL_SHOW)
		self.source_combo = choices.create_choice(self, choices=list(constants.VOICE_SOURCES), name=constants.LABEL_SHOW)
		self.source_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.search_label = wx.StaticText(self, label=constants.LABEL_SEARCH)
		self.search_input = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, name=constants.LABEL_SEARCH)
		self.search_button = wx.Button(self, label=constants.LABEL_SEARCH, name=constants.LABEL_SEARCH)
		self.gender_label, self.gender_combo = self._create_filter(constants.LABEL_GENDER, constants.GENDER_FILTERS)
		self.age_label, self.age_combo = self._create_filter(constants.LABEL_AGE, constants.AGE_FILTERS)
		self.language_label, self.language_combo = self._create_filter(constants.LABEL_LANGUAGE, constants.LANGUAGE_FILTERS)
		self.sort_label, self.sort_combo = self._create_filter(constants.LABEL_SORT, constants.SORT_FILTERS)
		self.voice_list = SmartList(parent=self, name=constants.TITLE_VOICE_LIBRARY)
		self.voice_list.set_columns([
			Column(constants.COLUMN_NAME, constants.COLUMN_WIDTH_NAME, constants.KEY_NAME),
			Column(constants.COLUMN_CATEGORY, constants.COLUMN_WIDTH_CATEGORY, constants.KEY_CATEGORY),
			Column(constants.COLUMN_DETAILS, constants.COLUMN_WIDTH_DETAILS, constants.KEY_DETAILS),
			Column(constants.COLUMN_DESCRIPTION, constants.COLUMN_WIDTH_DESCRIPTION, constants.KEY_DESCRIPTION),
		])
		self.preview_button = wx.Button(self, label=constants.LABEL_PREVIEW, name=constants.NAME_PREVIEW_VOICE)
		self.stop_button = wx.Button(self, label=constants.LABEL_STOP, name=constants.NAME_STOP_PREVIEW)
		self.use_button = wx.Button(self, label=constants.LABEL_USE_VOICE, name=constants.LABEL_USE_VOICE)
		self.load_more_button = wx.Button(self, label=constants.LABEL_LOAD_MORE, name=constants.NAME_LOAD_MORE_VOICES)
		self.load_more_button.Disable()
		self.status_text = StatusText(self, constants.STATUS_LOADING, constants.LABEL_STATUS)

	def _create_filter(self, label, filter_options):
		filter_label = wx.StaticText(self, label=label)
		filter_combo = choices.create_choice(
			self,
			choices=[option_label for option_label, option_value in filter_options],
			name=label,
		)
		filter_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		return filter_label, filter_combo

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.source_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.source_combo, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.search_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		search_sizer = wx.BoxSizer(wx.HORIZONTAL)
		search_sizer.Add(self.search_input, constants.SIZER_PROPORTION_EXPAND, wx.RIGHT, constants.CONTROL_GAP)
		search_sizer.Add(self.search_button, constants.SIZER_PROPORTION_NONE)
		main_sizer.Add(search_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		self.filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for filter_label, filter_combo in (
			(self.gender_label, self.gender_combo),
			(self.age_label, self.age_combo),
			(self.language_label, self.language_combo),
			(self.sort_label, self.sort_combo),
		):
			self.filter_sizer.Add(filter_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			self.filter_sizer.Add(filter_combo, constants.SIZER_PROPORTION_EXPAND, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(self.filter_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.voice_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for button in (self.preview_button, self.stop_button, self.use_button, self.load_more_button):
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.CONTROL_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.main_sizer = main_sizer
		self.SetSizer(main_sizer)

	def _bind_events(self):
		choices.bind_selection(self.source_combo, self._on_source_changed)
		self.search_input.Bind(wx.EVT_TEXT, self._on_search_text)
		self.search_input.Bind(wx.EVT_TEXT_ENTER, self._on_search)
		self.search_button.Bind(wx.EVT_BUTTON, self._on_search)
		for filter_combo in (self.gender_combo, self.age_combo, self.language_combo, self.sort_combo):
			choices.bind_selection(filter_combo, self._on_search)
		lists.bind_item_activated(self.voice_list, self._on_preview)
		self.preview_button.Bind(wx.EVT_BUTTON, self._on_preview)
		self.stop_button.Bind(wx.EVT_BUTTON, self._on_stop)
		self.use_button.Bind(wx.EVT_BUTTON, self._on_use)
		self.load_more_button.Bind(wx.EVT_BUTTON, self._on_load_more)
		self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)

	def _on_key_hook(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		event.Skip()

	def _set_tab_order(self):
		controls = (
			self.source_combo,
			self.search_input,
			self.search_button,
			self.gender_combo,
			self.age_combo,
			self.language_combo,
			self.sort_combo,
			self.voice_list.control.control,
			self.preview_button,
			self.stop_button,
			self.use_button,
			self.load_more_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def _is_community(self):
		return self.source_combo.GetStringSelection() == constants.VOICE_SOURCE_COMMUNITY

	def _update_mode_controls(self):
		is_community = self._is_community()
		# Hidden rather than disabled, so screen reader users do not tab through filters that do nothing.
		self.main_sizer.Show(self.filter_sizer, is_community, recursive=True)
		self.search_button.Show(is_community)
		self.load_more_button.Show(is_community)
		if is_community:
			self.search_input.SetName(constants.NAME_SEARCH_COMMUNITY)
			self.use_button.SetLabel(constants.LABEL_ADD_TO_MY_VOICES)
			self.use_button.SetName(constants.LABEL_ADD_TO_MY_VOICES)
		else:
			self.search_input.SetName(constants.LABEL_SEARCH)
			self.use_button.SetLabel(constants.LABEL_USE_VOICE)
			self.use_button.SetName(constants.LABEL_USE_VOICE)
		self.Layout()

	def _get_filter_value(self, filter_combo, filter_options):
		selection = filter_combo.GetSelection()
		if selection == wx.NOT_FOUND:
			selection = constants.FIRST_ITEM_INDEX
		return filter_options[selection][constants.INDEX_STEP]

	def _on_source_changed(self, event):
		self._update_mode_controls()
		self._load_voices()

	def _on_search_text(self, event):
		# My Voices is filtered as you type; the community library is only searched on Enter, to avoid a request per keystroke.
		if not self._is_community():
			self._filter_voices()

	def _on_search(self, event):
		if self._is_community():
			self._load_voices()

	def _on_load_more(self, event):
		self.load_more_button.Disable()
		self._start_load(self.community_page + constants.INDEX_STEP)

	def _load_voices(self):
		self.voices = []
		self.voice_list.clear()
		self.load_more_button.Disable()
		self._start_load(constants.FIRST_ITEM_INDEX)

	def _start_load(self, page):
		self.load_request += constants.INDEX_STEP
		self.status_text.SetLabel(constants.STATUS_LOADING)
		if self._is_community():
			arguments = (
				self.search_input.GetValue().strip(),
				self._get_filter_value(self.gender_combo, constants.GENDER_FILTERS),
				self._get_filter_value(self.age_combo, constants.AGE_FILTERS),
				self._get_filter_value(self.language_combo, constants.LANGUAGE_FILTERS),
				self._get_filter_value(self.sort_combo, constants.SORT_FILTERS),
				page,
			)
			target = self._load_community_worker
		else:
			arguments = ()
			target = self._load_my_voices_worker
		threading.Thread(
			target=target,
			args=(self.load_request,) + arguments,
			daemon=constants.THREAD_DAEMON,
		).start()

	def _load_my_voices_worker(self, load_request):
		try:
			voices = api.get_voices()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._load_failed, load_request, str(error))
			return
		wx.CallAfter(self._set_my_voices, load_request, voices)

	def _load_community_worker(self, load_request, search, gender, age, language, sort, page):
		try:
			voices, has_more = api.get_shared_voices(search, gender, age, language, sort, page)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._load_failed, load_request, str(error))
			return
		wx.CallAfter(self._add_community_voices, load_request, voices, has_more, page)

	def _is_current_load(self, load_request):
		return bool(self) and load_request == self.load_request

	def _load_failed(self, load_request, message):
		if self._is_current_load(load_request):
			self.load_more_button.Enable(self._is_community() and bool(self.voices))
			self.status_text.ReportFailure(message)

	def _set_my_voices(self, load_request, voices):
		if not self._is_current_load(load_request):
			return
		self.voices = voices
		self._filter_voices()

	def _add_community_voices(self, load_request, voices, has_more, page):
		if not self._is_current_load(load_request):
			return
		self.community_page = page
		self.voices.extend(voices)
		self.voice_list.add_items(voices)
		self.load_more_button.Enable(has_more)
		template = constants.STATUS_MORE_VOICES_TEMPLATE if has_more else constants.STATUS_VOICES_LOADED_TEMPLATE
		self.status_text.SetLabel(template.format(len(self.voices)))

	def _filter_voices(self):
		search_text = self.search_input.GetValue().lower()
		visible = []
		for voice in self.voices:
			searchable_text = constants.SPACE.join((
				voice[constants.KEY_NAME],
				voice[constants.KEY_CATEGORY],
				voice[constants.KEY_DETAILS],
				voice[constants.KEY_DESCRIPTION],
			)).lower()
			if search_text in searchable_text:
				visible.append(voice)
		self.voice_list.clear()
		self.voice_list.add_items(visible)
		self.status_text.SetLabel(constants.STATUS_VOICES_LOADED_TEMPLATE.format(len(visible)))

	def _get_selected_voice(self):
		voice = lists.get_selected_item(self.voice_list)
		if voice is None:
			self.status_text.ReportFailure(constants.ERROR_SELECTION_REQUIRED)
		return voice

	def _on_preview(self, event):
		voice = self._get_selected_voice()
		if voice is None:
			return
		preview_url = voice[constants.KEY_PREVIEW_URL]
		if not preview_url:
			self.status_text.ReportFailure(constants.ERROR_NO_PREVIEW)
			return
		if preview_url in self.preview_cache:
			self._play_preview(voice, self.preview_cache[preview_url])
			return
		self.status_text.SetLabel(constants.STATUS_LOADING_PREVIEW)
		threading.Thread(target=self._preview_worker, args=(voice,), daemon=constants.THREAD_DAEMON).start()

	def _preview_worker(self, voice):
		try:
			audio_bytes = api.get_voice_preview(voice[constants.KEY_PREVIEW_URL])
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._preview_failed, str(error))
			return
		wx.CallAfter(self._preview_loaded, voice, audio_bytes)

	def _preview_loaded(self, voice, audio_bytes):
		if not self:
			return
		self.preview_cache[voice[constants.KEY_PREVIEW_URL]] = audio_bytes
		self._play_preview(voice, audio_bytes)

	def _preview_failed(self, message):
		if self:
			self.status_text.ReportFailure(message)

	def _play_preview(self, voice, audio_bytes):
		on_finished = self.status_text.ShowPlayback(
			constants.STATUS_PLAYING_PREVIEW_TEMPLATE.format(voice[constants.KEY_NAME])
		)
		self.preview_thread = playback.play_audio(audio_bytes, constants.PREVIEW_OUTPUT_FORMAT, on_finished)

	def _on_stop(self, event):
		playback.stop_audio()
		self.status_text.SetLabel(constants.STATUS_PREVIEW_STOPPED)

	def _on_destroy(self, event):
		event.Skip()
		# Only stop a preview that is still playing, so closing the dialog does not cut off generated speech.
		if event.GetEventObject() is self and self.preview_thread is not None and self.preview_thread.is_alive():
			playback.stop_audio()

	def _on_use(self, event):
		voice = self._get_selected_voice()
		if voice is None:
			return
		if not self._is_community():
			self._use_voice(voice[constants.KEY_VOICE_ID])
			return
		self.use_button.Disable()
		self.status_text.SetLabel(constants.STATUS_ADDING_VOICE_TEMPLATE.format(voice[constants.KEY_NAME]))
		threading.Thread(target=self._add_voice_worker, args=(voice,), daemon=constants.THREAD_DAEMON).start()

	def _add_voice_worker(self, voice):
		try:
			voice_id = api.add_shared_voice(
				voice[constants.KEY_PUBLIC_OWNER_ID],
				voice[constants.KEY_VOICE_ID],
				voice[constants.KEY_NAME],
			)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._add_voice_failed, str(error))
			return
		usage.refresh()
		wx.CallAfter(self._use_voice, voice_id)

	def _add_voice_failed(self, message):
		if self:
			self.use_button.Enable()
			self.status_text.ReportFailure(message)

	def _use_voice(self, voice_id):
		self.tts_panel.refresh_voices(voice_id)
		self.sts_panel.refresh_voices()
		if self:
			self.Close()
