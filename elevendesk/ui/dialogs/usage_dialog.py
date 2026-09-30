import threading

import wx

from elevendesk import api
from elevendesk import constants
from elevendesk import usage
from elevendesk.ui.status_text import StatusText


class UsageDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_USAGE, size=constants.SMALL_DIALOG_SIZE)
		self.details_label = wx.StaticText(self, label=constants.TITLE_USAGE)
		self.details_output = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			name=constants.TITLE_USAGE,
		)
		self.status_text = StatusText(self, constants.STATUS_LOADING, constants.LABEL_STATUS)
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.details_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.details_output, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)
		# Show the last known usage straight away while fresh data loads.
		subscription = usage.get_subscription()
		if subscription is not None:
			self.details_output.ChangeValue(usage.format_details(subscription))
		self.details_output.SetFocus()
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _on_key_hook(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		event.Skip()

	def _load_worker(self):
		try:
			subscription = api.get_subscription()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._load_failed, str(error))
			return
		wx.CallAfter(self._set_subscription, subscription)

	def _load_failed(self, message):
		if self:
			self.status_text.ReportFailure(message)

	def _set_subscription(self, subscription):
		usage.set_subscription(subscription)
		if not self:
			return
		details = usage.format_details(subscription)
		# Replacing identical text would move a screen reader's reading position back to the start.
		if details != self.details_output.GetValue():
			self.details_output.ChangeValue(details)
		self.status_text.SetLabel(constants.STATUS_READY)
