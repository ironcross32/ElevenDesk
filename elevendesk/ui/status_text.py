import weakref

import prism
import wx

from elevendesk import constants
from elevendesk import usage

# Plain speech engines would talk over a sighted user, so failures are only spoken through screen readers.
_SPEECH_ENGINE_BACKENDS = {
	prism.BackendId.SAPI,
	prism.BackendId.ONE_CORE,
	prism.BackendId.AV_SPEECH,
	prism.BackendId.SPEECH_DISPATCHER,
	prism.BackendId.ANDROID_TTS,
	prism.BackendId.WEB_SPEECH,
}

_prism_context = None
_instances = weakref.WeakSet()


def announce(message):
	# Speaks and brailles a message through whichever screen reader is running, if any.
	global _prism_context
	if not message:
		return
	try:
		if _prism_context is None:
			_prism_context = prism.Context()
		backend = _prism_context.acquire_best()
		if _prism_context.id_of(backend.name) in _SPEECH_ENGINE_BACKENDS:
			return
		backend.output(message)
	except (prism.PrismError, ValueError):
		pass


class StatusText(wx.StaticText):
	# Wraps long messages (such as API errors) onto several lines instead of clipping them.

	def __init__(self, parent, label, name):
		self._is_ready = label == constants.STATUS_READY
		if self._is_ready:
			label = usage.format_ready_status()
		super().__init__(parent, label=label, name=name, style=wx.ST_NO_AUTORESIZE)
		self._full_label = label
		self._wrapped_width = None
		self._label_generation = 0
		self.Bind(wx.EVT_SIZE, self._on_size)
		_instances.add(self)

	def SetLabel(self, label):
		# The ready status also carries a short usage summary once usage data has been fetched.
		self._is_ready = label == constants.STATUS_READY
		if self._is_ready:
			label = usage.format_ready_status()
		self._full_label = label
		self._wrapped_width = None
		self._label_generation += 1
		self._apply_label()

	def ShowPlayback(self, label):
		# Returns an on_finished callback for playback.play_audio that restores the ready status,
		# unless the status has changed since (for example, because newer audio started playing).
		self.SetLabel(label)
		generation = self._label_generation

		def restore_ready():
			if self and self._label_generation == generation:
				self.SetLabel(constants.STATUS_READY)

		return lambda: wx.CallAfter(restore_ready)

	def ReportFailure(self, message):
		# Failures are something the user must know about, so they are announced as well as shown.
		self.SetLabel(message)
		announce(message)

	def _apply_label(self):
		width = self.GetSize().width
		wx.StaticText.SetLabel(self, self._full_label)
		if width > 0:
			self.Wrap(width)
			self._wrapped_width = width
		self.InvalidateBestSize()
		self.GetParent().Layout()

	def _on_size(self, event):
		event.Skip()
		if event.GetSize().width != self._wrapped_width:
			wx.CallAfter(self._rewrap)

	def _rewrap(self):
		if self and self.GetSize().width != self._wrapped_width:
			self._apply_label()


def _refresh_ready_labels():
	for status_text in list(_instances):
		if status_text and status_text._is_ready:
			status_text.SetLabel(constants.STATUS_READY)


usage.add_listener(_refresh_ready_labels)
