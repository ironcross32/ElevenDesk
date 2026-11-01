import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import config
from elevendesk import constants
from elevendesk import playback
from elevendesk import usage
from elevendesk.ui import choices
from elevendesk.ui import lists
from elevendesk.ui.status_text import StatusText, announce

_PLAY_KEYS = (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE)


class SoundEffectsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.last_output_format = constants.OUTPUT_MP3_44100_128
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()

	def _create_controls(self):
		self.prompt_label = wx.StaticText(self, label=constants.LABEL_SOUND_PROMPT)
		self.prompt_input = wx.TextCtrl(self, name=constants.LABEL_SOUND_PROMPT)
		self.duration_label = wx.StaticText(self, label=constants.LABEL_DURATION)
		self.duration_input = wx.SpinCtrlDouble(
			self,
			min=constants.DURATION_AUTO,
			max=constants.DURATION_MAXIMUM,
			initial=constants.DURATION_AUTO,
			inc=constants.DURATION_INCREMENT,
			name=constants.LABEL_DURATION,
		)
		self.duration_input.SetDigits(constants.SPIN_DIGITS)
		self.influence_label = wx.StaticText(self, label=constants.LABEL_PROMPT_INFLUENCE)
		self.influence_slider = wx.Slider(
			self,
			value=constants.SLIDER_DEFAULT_PROMPT_INFLUENCE,
			minValue=constants.SLIDER_MINIMUM,
			maxValue=constants.SLIDER_MAXIMUM,
			name=constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(
				constants.LABEL_PROMPT_INFLUENCE,
				constants.SLIDER_DEFAULT_PROMPT_INFLUENCE,
			),
		)
		self.influence_value = wx.StaticText(
			self,
			label=constants.SLIDER_VALUE_TEMPLATE.format(
				constants.LABEL_PROMPT_INFLUENCE,
				constants.SLIDER_DEFAULT_PROMPT_INFLUENCE,
			),
		)
		self.loop_checkbox = wx.CheckBox(self, label=constants.LABEL_SEAMLESS_LOOP)
		self.output_format_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_FORMAT)
		self.output_format_combo = choices.create_choice(
			self,
			choices=list(constants.SFX_OUTPUT_FORMATS),
			name=constants.LABEL_OUTPUT_FORMAT,
		)
		format_index = self.output_format_combo.FindString(config.load_config()[constants.KEY_DEFAULT_OUTPUT_FORMAT])
		self.output_format_combo.SetSelection(constants.FIRST_ITEM_INDEX if format_index == wx.NOT_FOUND else format_index)
		self.count_label = wx.StaticText(self, label=constants.LABEL_VARIATION_COUNT)
		self.count_input = wx.SpinCtrl(
			self,
			min=constants.SFX_VARIATIONS_MINIMUM,
			max=constants.SFX_VARIATIONS_MAXIMUM,
			initial=constants.SFX_VARIATIONS_DEFAULT,
			name=constants.LABEL_VARIATION_COUNT,
		)
		self.generate_label = wx.StaticText(self, label=constants.LABEL_GENERATE)
		self.generate_button = wx.Button(
			self,
			label=constants.LABEL_GENERATE,
			name=constants.NAME_GENERATE_SOUND_EFFECT,
		)
		self.variation_label = wx.StaticText(self, label=constants.LABEL_VARIATIONS)
		self.variation_list = SmartList(parent=self, style=wx.LC_SINGLE_SEL, name=constants.LABEL_VARIATIONS)
		self.variation_list.set_columns([
			Column(constants.COLUMN_VARIATION, constants.COLUMN_WIDTH_NAME, constants.KEY_NAME),
		])
		self.variation_control = self.variation_list.control.control
		self.variation_control.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.RESULT_MIN_HEIGHT))
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(
			self,
			label=constants.LABEL_PLAY,
			name=constants.NAME_PLAY_GENERATED_SOUND_EFFECT,
		)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(
			self,
			label=constants.LABEL_SAVE,
			name=constants.NAME_SAVE_GENERATED_SOUND_EFFECT,
		)
		self.variation_control.Disable()
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = StatusText(self, constants.STATUS_READY, constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.prompt_label, self.prompt_input),
			(self.duration_label, self.duration_input),
			(self.influence_label, self.influence_slider),
			(None, self.influence_value),
			(None, self.loop_checkbox),
			(self.output_format_label, self.output_format_combo),
			(self.count_label, self.count_input),
			(self.generate_label, self.generate_button),
			(self.variation_label, self.variation_control),
		):
			if label is not None:
				main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.variation_control else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.play_label, self.play_button),
			(self.save_label, self.save_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		controls = (
			self.prompt_input,
			self.duration_input,
			self.influence_slider,
			self.loop_checkbox,
			self.output_format_combo,
			self.count_input,
			self.generate_button,
			self.variation_control,
			self.play_button,
			self.save_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def _bind_events(self):
		self.influence_slider.Bind(wx.EVT_SLIDER, self._on_influence_changed)
		self.generate_button.Bind(wx.EVT_BUTTON, self._on_generate)
		# The hook swallows Enter and Space before the list sees them, so activation only comes from a double-click.
		self.variation_control.Bind(wx.EVT_CHAR_HOOK, self._on_variation_key)
		lists.bind_item_activated(self.variation_list, self._on_play)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _on_influence_changed(self, event):
		value = self.influence_slider.GetValue()
		self.influence_value.SetLabel(constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_PROMPT_INFLUENCE, value))
		self.influence_slider.SetName(constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_PROMPT_INFLUENCE, value))

	def _on_variation_key(self, event):
		if event.GetKeyCode() in _PLAY_KEYS and not event.HasAnyModifiers():
			self._on_play(event)
			return
		event.Skip()

	def _duration_seconds(self):
		# Returns None for "model chooses", or raises ValueError when the duration is too short for the API.
		seconds = self.duration_input.GetValue()
		if seconds == constants.DURATION_AUTO:
			return None
		if seconds < constants.DURATION_MINIMUM:
			raise ValueError(constants.ERROR_DURATION_RANGE_TEMPLATE.format(
				constants.DURATION_MINIMUM,
				constants.DURATION_MAXIMUM,
			))
		return seconds

	def _on_generate(self, event):
		prompt = self.prompt_input.GetValue().strip()
		if not prompt:
			self.status_text.ReportFailure(constants.ERROR_PROMPT_REQUIRED)
			return
		try:
			duration = self._duration_seconds()
		except ValueError as error:
			self.status_text.ReportFailure(str(error))
			return
		count = self.count_input.GetValue()
		self.generate_button.Disable()
		self.status_text.SetLabel(constants.STATUS_GENERATING_VARIATIONS_TEMPLATE.format(count))
		threading.Thread(
			target=self._generate_worker,
			args=(
				count,
				prompt,
				duration,
				self.influence_slider.GetValue() / constants.PERCENT_DIVISOR,
				self.loop_checkbox.GetValue(),
				self.output_format_combo.GetStringSelection(),
			),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _generate_worker(self, count, prompt, duration, prompt_influence, loop, output_format):
		try:
			variations, error_message = api.generate_sound_effect_variations(
				count,
				prompt,
				duration,
				prompt_influence,
				loop,
				output_format,
			)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._generation_failed, str(error))
			return
		wx.CallAfter(self._generation_succeeded, variations, output_format, count, error_message)

	def _generation_succeeded(self, variations, output_format, count, error_message):
		usage.refresh()
		self.last_output_format = output_format
		self.variation_list.clear()
		self.variation_list.add_items([
			{
				constants.KEY_NAME: constants.VARIATION_ITEM_TEMPLATE.format(number),
				constants.KEY_AUDIO: audio_bytes,
			}
			for number, audio_bytes in enumerate(variations, constants.INDEX_STEP)
		])
		self.variation_list.set_selected_index(constants.FIRST_ITEM_INDEX)
		self.variation_control.Enable()
		self.generate_button.Enable()
		self.play_button.Enable()
		self.save_button.Enable()
		if error_message:
			self.status_text.ReportFailure(
				constants.STATUS_VARIATIONS_PARTIAL_TEMPLATE.format(len(variations), count, error_message)
			)
			return
		# Several sounds take a while, so the result is spoken in case focus has moved on.
		message = constants.STATUS_VARIATIONS_GENERATED_TEMPLATE.format(len(variations))
		self.status_text.SetLabel(message)
		announce(message)

	def _generation_failed(self, message):
		self.generate_button.Enable()
		self.status_text.ReportFailure(message)

	def _selected_audio(self):
		item = lists.get_selected_item(self.variation_list)
		return item[constants.KEY_AUDIO] if item else None

	def _on_play(self, event):
		audio_bytes = self._selected_audio()
		if audio_bytes:
			playback.play_audio(
				audio_bytes,
				self.last_output_format,
				on_finished=self.status_text.ShowPlayback(constants.STATUS_PLAYING),
			)
		else:
			self.status_text.ReportFailure(constants.ERROR_SELECTION_REQUIRED)

	def _on_save(self, event):
		self.GetTopLevelParent().save_audio_bytes(self._selected_audio(), self.last_output_format, self.status_text)

	def get_last_output(self):
		return self._selected_audio(), self.last_output_format
