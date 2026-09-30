import datetime
import threading
import time

import wx

from elevendesk import api
from elevendesk import constants


_subscription = None
_listeners = []


def get_subscription():
	return _subscription


def add_listener(callback):
	# Callbacks run on the GUI thread whenever new usage data arrives.
	_listeners.append(callback)


def set_subscription(subscription):
	global _subscription
	_subscription = subscription
	for listener in list(_listeners):
		listener()


def refresh():
	# Fetches usage in the background; safe to call from any thread.
	threading.Thread(target=_refresh_worker, daemon=constants.THREAD_DAEMON).start()


def _refresh_worker():
	try:
		subscription = api.get_subscription()
	except api.ElevenDeskAPIError:
		# The usage summary is supplementary, so a failed refresh keeps the last known values.
		return
	wx.CallAfter(set_subscription, subscription)


def _percent_left(subscription):
	limit = subscription[constants.KEY_CHARACTER_LIMIT]
	if not limit:
		return None
	remaining = max(limit - subscription[constants.KEY_CHARACTER_COUNT], 0)
	return int(remaining * constants.PERCENT_DIVISOR // limit)


def _format_time_until(unix_time):
	if not unix_time:
		return constants.EMPTY_TEXT
	seconds = unix_time - time.time()
	if seconds <= 0:
		return constants.EMPTY_TEXT
	days = int(seconds // constants.SECONDS_PER_DAY)
	if days:
		return (constants.USAGE_DAY_TEMPLATE if days == 1 else constants.USAGE_DAYS_TEMPLATE).format(days)
	hours = int(seconds // constants.SECONDS_PER_HOUR)
	if hours:
		return (constants.USAGE_HOUR_TEMPLATE if hours == 1 else constants.USAGE_HOURS_TEMPLATE).format(hours)
	return constants.USAGE_LESS_THAN_HOUR


def _format_date(unix_time):
	date_time = datetime.datetime.fromtimestamp(unix_time)
	return constants.USAGE_DATE_TEMPLATE.format(
		date_time.strftime(constants.HISTORY_DATE_PREFIX_FORMAT),
		date_time.day,
		date_time.year,
		date_time.strftime(constants.USAGE_TIME_FORMAT).lstrip(constants.USAGE_TIME_LEADING_ZERO),
	)


def _humanize(value):
	text = str(value).replace(constants.LABEL_WORD_SEPARATOR, constants.SPACE)
	return text[:1].upper() + text[1:]


def _format_period(period):
	return constants.USAGE_PERIOD_NAMES.get(period, _humanize(period))


def format_summary():
	# Such as "42% left, resets in 5 days"; empty until usage has been fetched.
	if _subscription is None:
		return constants.EMPTY_TEXT
	percent = _percent_left(_subscription)
	if percent is None:
		return constants.EMPTY_TEXT
	summary = constants.USAGE_PERCENT_LEFT_TEMPLATE.format(percent)
	time_until = _format_time_until(_subscription[constants.KEY_NEXT_RESET_UNIX])
	if time_until:
		summary = constants.USAGE_SUMMARY_TEMPLATE.format(summary, time_until)
	return summary


def format_ready_status():
	summary = format_summary()
	if not summary:
		return constants.STATUS_READY
	return constants.STATUS_READY_WITH_USAGE_TEMPLATE.format(constants.STATUS_READY, summary)


def format_details(subscription):
	lines = []

	def add(label, value):
		lines.append(constants.USAGE_LINE_TEMPLATE.format(label, value))

	if subscription[constants.KEY_TIER]:
		add(constants.USAGE_LABEL_PLAN, _humanize(subscription[constants.KEY_TIER]))
	if subscription[constants.KEY_SUBSCRIPTION_STATUS]:
		add(constants.USAGE_LABEL_STATUS, _humanize(subscription[constants.KEY_SUBSCRIPTION_STATUS]))
	count = subscription[constants.KEY_CHARACTER_COUNT]
	limit = subscription[constants.KEY_CHARACTER_LIMIT]
	add(constants.USAGE_LABEL_CHARACTERS_USED, constants.USAGE_OF_TEMPLATE.format(count, limit))
	percent = _percent_left(subscription)
	if percent is not None:
		add(
			constants.USAGE_LABEL_CHARACTERS_REMAINING,
			constants.USAGE_REMAINING_TEMPLATE.format(max(limit - count, 0), percent),
		)
	reset_unix = subscription[constants.KEY_NEXT_RESET_UNIX]
	if reset_unix:
		reset_text = _format_date(reset_unix)
		time_until = _format_time_until(reset_unix)
		if time_until:
			reset_text = constants.USAGE_RESET_TEMPLATE.format(reset_text, time_until)
		add(constants.USAGE_LABEL_NEXT_RESET, reset_text)
	if subscription[constants.KEY_CHARACTER_REFRESH_PERIOD]:
		add(constants.USAGE_LABEL_REFRESH_PERIOD, _format_period(subscription[constants.KEY_CHARACTER_REFRESH_PERIOD]))
	if subscription[constants.KEY_BILLING_PERIOD]:
		add(constants.USAGE_LABEL_BILLING_PERIOD, _format_period(subscription[constants.KEY_BILLING_PERIOD]))
	add(
		constants.USAGE_LABEL_VOICE_SLOTS,
		constants.USAGE_OF_TEMPLATE.format(subscription[constants.KEY_VOICE_SLOTS_USED], subscription[constants.KEY_VOICE_LIMIT]),
	)
	add(
		constants.USAGE_LABEL_PROFESSIONAL_VOICE_SLOTS,
		constants.USAGE_OF_TEMPLATE.format(
			subscription[constants.KEY_PROFESSIONAL_VOICE_SLOTS_USED],
			subscription[constants.KEY_PROFESSIONAL_VOICE_LIMIT],
		),
	)
	add_edits_used = subscription[constants.KEY_VOICE_ADD_EDITS_USED]
	max_add_edits = subscription[constants.KEY_MAX_VOICE_ADD_EDITS]
	if max_add_edits is None:
		add(constants.USAGE_LABEL_VOICE_ADD_EDITS, constants.USAGE_COUNT_TEMPLATE.format(add_edits_used))
	else:
		add(constants.USAGE_LABEL_VOICE_ADD_EDITS, constants.USAGE_OF_TEMPLATE.format(add_edits_used, max_add_edits))
	for label, key in (
		(constants.USAGE_LABEL_INSTANT_CLONING, constants.KEY_CAN_USE_INSTANT_CLONING),
		(constants.USAGE_LABEL_PROFESSIONAL_CLONING, constants.KEY_CAN_USE_PROFESSIONAL_CLONING),
	):
		add(label, constants.USAGE_AVAILABLE if subscription[key] else constants.USAGE_NOT_AVAILABLE)
	overage_amount = subscription[constants.KEY_OVERAGE_AMOUNT]
	if _is_nonzero_amount(overage_amount):
		add(
			constants.USAGE_LABEL_OVERAGE,
			constants.USAGE_MONEY_TEMPLATE.format(overage_amount, subscription[constants.KEY_OVERAGE_CURRENCY].upper()).strip(),
		)
	invoice_cents = subscription[constants.KEY_NEXT_INVOICE_CENTS]
	invoice_unix = subscription[constants.KEY_NEXT_INVOICE_UNIX]
	if invoice_cents is not None and invoice_unix:
		amount = constants.USAGE_MONEY_TEMPLATE.format(
			constants.USAGE_CENTS_TEMPLATE.format(invoice_cents / constants.CENTS_PER_UNIT),
			subscription[constants.KEY_CURRENCY].upper(),
		).strip()
		add(constants.USAGE_LABEL_NEXT_INVOICE, constants.USAGE_INVOICE_TEMPLATE.format(amount, _format_date(invoice_unix)))
	return constants.NEWLINE.join(lines)


def _is_nonzero_amount(amount):
	if amount is None:
		return False
	try:
		return float(amount) != 0
	except (TypeError, ValueError):
		return bool(amount)
