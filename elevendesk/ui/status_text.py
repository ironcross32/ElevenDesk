import prism
import wx

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
		super().__init__(parent, label=label, name=name, style=wx.ST_NO_AUTORESIZE)
		self._full_label = label
		self._wrapped_width = None
		self.Bind(wx.EVT_SIZE, self._on_size)

	def SetLabel(self, label):
		self._full_label = label
		self._wrapped_width = None
		self._apply_label()

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
