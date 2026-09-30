import datetime

from elevenlabs.client import ElevenLabs
from elevenlabs.core import ApiError
from elevenlabs.types import DialogueInput, PronunciationDictionaryVersionLocator, ToDialogueSettingsResponseModel, VoiceSettings
import httpx

from elevendesk import config
from elevendesk import constants


class ElevenDeskAPIError(Exception):
	pass


_client = None
_client_api_key = None


def get_client():
	global _client
	global _client_api_key
	api_key = config.load_config()[constants.KEY_API_KEY]
	if not api_key:
		raise ElevenDeskAPIError(constants.ERROR_API_KEY_REQUIRED)
	if _client is None or api_key != _client_api_key:
		try:
			_client = ElevenLabs(api_key=api_key)
		except (TypeError, ValueError) as error:
			raise ElevenDeskAPIError(str(error)) from error
		_client_api_key = api_key
	return _client


def reset_client():
	global _client
	global _client_api_key
	_client = None
	_client_api_key = None


def _get_attribute(value, attribute_name, default_value=None):
	if isinstance(value, dict):
		return value.get(attribute_name, default_value)
	return getattr(value, attribute_name, default_value)


def _get_collection(response, attribute_name):
	collection = _get_attribute(response, attribute_name, response)
	if collection is None:
		return []
	return list(collection)


def _join_audio_chunks(response):
	if isinstance(response, bytes):
		return response
	if isinstance(response, bytearray):
		return bytes(response)
	try:
		return b"".join(response)
	except ApiError as error:
		raise ElevenDeskAPIError(_format_api_error(error)) from error
	except (httpx.HTTPError, OSError, TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error


def _format_api_error(error):
	body = error.body
	if isinstance(body, dict):
		detail = body.get(constants.API_ERROR_DETAIL, body)
		if isinstance(detail, dict):
			message = detail.get(constants.API_ERROR_MESSAGE)
			request_id = detail.get(constants.API_ERROR_REQUEST_ID)
			if message and request_id:
				return constants.ERROR_API_REQUEST_ID_TEMPLATE.format(message, request_id)
			if message:
				return message
		if isinstance(detail, str):
			return detail
	return str(error)


def _call_sdk(callable_object, keyword_arguments):
	try:
		return callable_object(**keyword_arguments)
	except (ElevenDeskAPIError, KeyboardInterrupt, SystemExit):
		raise
	except ApiError as error:
		raise ElevenDeskAPIError(_format_api_error(error)) from error
	except (httpx.HTTPError, OSError, TypeError, ValueError, AttributeError) as error:
		raise ElevenDeskAPIError(str(error)) from error


def _get_sdk_section(client, section_name):
	try:
		return getattr(client, section_name)
	except AttributeError as error:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE) from error


def _get_sdk_method(client, section_name, method_name):
	section = _get_sdk_section(client, section_name)
	try:
		return getattr(section, method_name)
	except AttributeError as error:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE) from error


_LANGUAGE_NAMES = {code: name for name, code in constants.LANGUAGE_FILTERS if code}


def _format_voice_details(source, extra_details=()):
	# Gender, age, accent and language read as one comma-separated column, such as "female, middle aged, british".
	details = []
	for attribute_name in (
		constants.API_ATTR_GENDER,
		constants.API_ATTR_AGE,
		constants.API_ATTR_ACCENT,
		constants.API_ATTR_LANGUAGE,
	):
		value = _get_attribute(source, attribute_name, constants.EMPTY_TEXT)
		if attribute_name == constants.API_ATTR_LANGUAGE:
			value = _LANGUAGE_NAMES.get(value, value)
		if value:
			details.append(str(value).replace(constants.LABEL_WORD_SEPARATOR, constants.SPACE))
	details.extend(extra_details)
	return constants.DETAILS_SEPARATOR.join(details)


def get_voices():
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICES, constants.API_ATTR_GET_ALL),
		{},
	)
	voices = []
	for voice in _get_collection(response, constants.API_ATTR_VOICES):
		voice_id = _get_attribute(voice, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT)
		voices.append({
			constants.KEY_ID: voice_id,
			constants.KEY_VOICE_ID: voice_id,
			constants.KEY_NAME: _get_attribute(voice, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
			constants.KEY_CATEGORY: _get_attribute(voice, constants.API_ATTR_CATEGORY, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
			constants.KEY_DESCRIPTION: _get_attribute(voice, constants.API_ATTR_DESCRIPTION, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
			constants.KEY_DETAILS: _format_voice_details(_get_attribute(voice, constants.API_ATTR_LABELS, None) or {}),
			constants.KEY_PREVIEW_URL: _get_attribute(voice, constants.API_ATTR_PREVIEW_URL, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
		})
	return voices


def get_shared_voices(search, gender, age, language, sort, page):
	client = get_client()
	keyword_arguments = {
		constants.API_KW_PAGE_SIZE: constants.SHARED_VOICES_PAGE_SIZE,
		constants.API_KW_PAGE: page,
		constants.API_KW_SORT: sort,
	}
	# Empty filters are left out so the API does not treat them as "match nothing".
	for keyword, value in (
		(constants.API_KW_SEARCH, search),
		(constants.API_KW_GENDER, gender),
		(constants.API_KW_AGE, age),
		(constants.API_KW_LANGUAGE, language),
	):
		if value:
			keyword_arguments[keyword] = value
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICES, constants.API_ATTR_GET_SHARED),
		keyword_arguments,
	)
	voices = []
	for voice in _get_collection(response, constants.API_ATTR_VOICES):
		voice_id = _get_attribute(voice, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT)
		extra_details = (constants.VOICE_ALREADY_ADDED,) if _get_attribute(voice, constants.API_ATTR_IS_ADDED_BY_USER, False) else ()
		voices.append({
			constants.KEY_ID: voice_id,
			constants.KEY_VOICE_ID: voice_id,
			constants.KEY_PUBLIC_OWNER_ID: _get_attribute(voice, constants.API_ATTR_PUBLIC_OWNER_ID, constants.EMPTY_TEXT),
			constants.KEY_NAME: _get_attribute(voice, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
			constants.KEY_CATEGORY: str(_get_attribute(voice, constants.API_ATTR_CATEGORY, constants.EMPTY_TEXT) or constants.EMPTY_TEXT),
			constants.KEY_DESCRIPTION: _get_attribute(voice, constants.API_ATTR_DESCRIPTION, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
			constants.KEY_DETAILS: _format_voice_details(voice, extra_details),
			constants.KEY_PREVIEW_URL: _get_attribute(voice, constants.API_ATTR_PREVIEW_URL, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
		})
	has_more = bool(_get_attribute(response, constants.API_ATTR_HAS_MORE, False))
	return voices, has_more


def add_shared_voice(public_owner_id, voice_id, name):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICES, constants.API_ATTR_SHARE),
		{
			constants.API_KW_PUBLIC_USER_ID: public_owner_id,
			constants.API_KW_VOICE_ID: voice_id,
			constants.API_KW_NEW_NAME: name,
		},
	)
	return _get_attribute(response, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT) or voice_id


def get_voice_preview(preview_url):
	# Preview samples are public files, so they are downloaded directly rather than through the SDK.
	try:
		response = httpx.get(
			preview_url,
			timeout=constants.PREVIEW_DOWNLOAD_TIMEOUT_SECONDS,
			follow_redirects=True,
		)
		response.raise_for_status()
	except httpx.HTTPError as error:
		raise ElevenDeskAPIError(str(error)) from error
	return response.content


def validate_api_key(api_key):
	try:
		client = ElevenLabs(api_key=api_key)
	except (TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	get_models(client)


def get_models(client=None):
	client = client or get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_MODELS, constants.API_ATTR_LIST),
		{},
	)
	models = []
	for model in _get_collection(response, constants.API_ATTR_MODELS):
		model_id = _get_attribute(model, constants.API_ATTR_MODEL_ID, constants.EMPTY_TEXT)
		if not model_id:
			continue
		models.append({
			constants.KEY_ID: model_id,
			constants.KEY_NAME: _get_attribute(model, constants.API_ATTR_NAME, constants.EMPTY_TEXT) or model_id,
			constants.KEY_CAN_DO_TTS: bool(_get_attribute(model, constants.API_ATTR_CAN_DO_TTS, False)),
			constants.KEY_CAN_DO_STS: bool(_get_attribute(model, constants.API_ATTR_CAN_DO_STS, False)),
		})
	return models


def get_subscription():
	client = get_client()
	user_section = _get_sdk_section(client, constants.API_ATTR_USER)
	response = _call_sdk(
		_get_sdk_method(user_section, constants.API_ATTR_SUBSCRIPTION, constants.API_ATTR_GET),
		{},
	)
	overage = _get_attribute(response, constants.API_ATTR_CURRENT_OVERAGE, None)
	next_invoice = _get_attribute(response, constants.API_ATTR_NEXT_INVOICE, None)
	return {
		constants.KEY_TIER: str(_get_attribute(response, constants.API_ATTR_TIER, constants.EMPTY_TEXT) or constants.EMPTY_TEXT),
		constants.KEY_SUBSCRIPTION_STATUS: str(_get_attribute(response, constants.API_ATTR_STATUS, constants.EMPTY_TEXT) or constants.EMPTY_TEXT),
		constants.KEY_CHARACTER_COUNT: _get_attribute(response, constants.API_ATTR_CHARACTER_COUNT, 0) or 0,
		constants.KEY_CHARACTER_LIMIT: _get_attribute(response, constants.API_ATTR_CHARACTER_LIMIT, 0) or 0,
		constants.KEY_NEXT_RESET_UNIX: _get_attribute(response, constants.API_ATTR_NEXT_RESET_UNIX, None),
		constants.KEY_CHARACTER_REFRESH_PERIOD: _get_attribute(response, constants.API_ATTR_CHARACTER_REFRESH_PERIOD, None),
		constants.KEY_BILLING_PERIOD: _get_attribute(response, constants.API_ATTR_BILLING_PERIOD, None),
		constants.KEY_VOICE_SLOTS_USED: _get_attribute(response, constants.API_ATTR_VOICE_SLOTS_USED, 0) or 0,
		constants.KEY_VOICE_LIMIT: _get_attribute(response, constants.API_ATTR_VOICE_LIMIT, 0) or 0,
		constants.KEY_PROFESSIONAL_VOICE_SLOTS_USED: _get_attribute(response, constants.API_ATTR_PROFESSIONAL_VOICE_SLOTS_USED, 0) or 0,
		constants.KEY_PROFESSIONAL_VOICE_LIMIT: _get_attribute(response, constants.API_ATTR_PROFESSIONAL_VOICE_LIMIT, 0) or 0,
		constants.KEY_VOICE_ADD_EDITS_USED: _get_attribute(response, constants.API_ATTR_VOICE_ADD_EDIT_COUNTER, 0) or 0,
		constants.KEY_MAX_VOICE_ADD_EDITS: _get_attribute(response, constants.API_ATTR_MAX_VOICE_ADD_EDITS, None),
		constants.KEY_CAN_USE_INSTANT_CLONING: bool(_get_attribute(response, constants.API_ATTR_CAN_USE_INSTANT_CLONING, False)),
		constants.KEY_CAN_USE_PROFESSIONAL_CLONING: bool(_get_attribute(response, constants.API_ATTR_CAN_USE_PROFESSIONAL_CLONING, False)),
		constants.KEY_OVERAGE_AMOUNT: _get_attribute(overage, constants.API_ATTR_AMOUNT, None) if overage else None,
		constants.KEY_OVERAGE_CURRENCY: str(_get_attribute(overage, constants.API_ATTR_CURRENCY, constants.EMPTY_TEXT) or constants.EMPTY_TEXT) if overage else constants.EMPTY_TEXT,
		constants.KEY_NEXT_INVOICE_CENTS: _get_attribute(next_invoice, constants.API_ATTR_AMOUNT_DUE_CENTS, None) if next_invoice else None,
		constants.KEY_NEXT_INVOICE_UNIX: _get_attribute(next_invoice, constants.API_ATTR_NEXT_PAYMENT_ATTEMPT_UNIX, None) if next_invoice else None,
		constants.KEY_CURRENCY: str(_get_attribute(response, constants.API_ATTR_CURRENCY, constants.EMPTY_TEXT) or constants.EMPTY_TEXT),
	}


def models_from_ids(model_ids):
	return [{constants.KEY_ID: model_id, constants.KEY_NAME: model_id} for model_id in model_ids]


def filter_tts_models(models):
	return [model for model in models if model[constants.KEY_CAN_DO_TTS]]


def filter_sts_models(models):
	return [model for model in models if model[constants.KEY_CAN_DO_STS]]


def filter_stt_models(models):
	# The models endpoint does not reliably list Scribe models, so always keep the known ones.
	stt_models = [model for model in models if model[constants.KEY_ID].startswith(constants.MODEL_STT_PREFIX)]
	known_ids = {model[constants.KEY_ID] for model in stt_models}
	for known_model in models_from_ids(constants.KNOWN_STT_MODEL_IDS):
		if known_model[constants.KEY_ID] not in known_ids:
			stt_models.append(known_model)
	return stt_models


def text_to_speech(text, voice_id, model_id, voice_settings, output_format, pronunciation_dictionary_ids=()):
	client = get_client()
	try:
		sdk_voice_settings = VoiceSettings(**voice_settings)
	except (TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	keyword_arguments = {
		constants.API_KW_TEXT: text,
		constants.API_KW_VOICE_ID: voice_id,
		constants.API_KW_MODEL_ID: model_id,
		constants.API_KW_VOICE_SETTINGS: sdk_voice_settings,
		constants.API_KW_OUTPUT_FORMAT: output_format,
	}
	if pronunciation_dictionary_ids:
		# Leaving out the version ID makes the API apply each dictionary's latest rules.
		keyword_arguments[constants.API_KW_PRONUNCIATION_DICTIONARY_LOCATORS] = [
			PronunciationDictionaryVersionLocator(pronunciation_dictionary_id=dictionary_id)
			for dictionary_id in pronunciation_dictionary_ids
		]
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_TEXT_TO_SPEECH, constants.API_ATTR_CONVERT),
		keyword_arguments,
	)
	return _join_audio_chunks(response)


def filter_dialogue_models(models):
	dialogue_models = [model for model in models if model[constants.KEY_ID] in constants.KNOWN_DIALOGUE_MODEL_IDS]
	if not any(model[constants.KEY_ID] == constants.MODEL_ELEVEN_V3 for model in dialogue_models):
		dialogue_models.extend(models_from_ids((constants.MODEL_ELEVEN_V3,)))
	return dialogue_models


def text_to_dialogue(inputs, model_id, stability, output_format, pronunciation_dictionary_ids=()):
	client = get_client()
	try:
		sdk_inputs = [DialogueInput(**dialogue_input) for dialogue_input in inputs]
		sdk_settings = ToDialogueSettingsResponseModel(stability=stability)
	except (TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	keyword_arguments = {
		constants.API_KW_INPUTS: sdk_inputs,
		constants.API_KW_MODEL_ID: model_id,
		constants.API_KW_SETTINGS: sdk_settings,
		constants.API_KW_OUTPUT_FORMAT: output_format,
	}
	if pronunciation_dictionary_ids:
		keyword_arguments[constants.API_KW_PRONUNCIATION_DICTIONARY_LOCATORS] = [
			PronunciationDictionaryVersionLocator(pronunciation_dictionary_id=dictionary_id)
			for dictionary_id in pronunciation_dictionary_ids
		]
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_TEXT_TO_DIALOGUE, constants.API_ATTR_CONVERT),
		keyword_arguments,
	)
	return _join_audio_chunks(response)


def speech_to_text(audio_bytes, model_id):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_SPEECH_TO_TEXT, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_FILE: audio_bytes,
			constants.API_KW_MODEL_ID: model_id,
		},
	)
	text = _get_attribute(response, constants.API_ATTR_TEXT, response)
	if not isinstance(text, str):
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	return text


def speech_to_speech(audio_bytes, voice_id, model_id, output_format):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_SPEECH_TO_SPEECH, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_AUDIO: audio_bytes,
			constants.API_KW_VOICE_ID: voice_id,
			constants.API_KW_MODEL_ID: model_id,
			constants.API_KW_OUTPUT_FORMAT: output_format,
		},
	)
	return _join_audio_chunks(response)


def generate_sound_effect(prompt, duration_seconds):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_SOUND_GENERATION, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_TEXT: prompt,
			constants.API_KW_DURATION_SECONDS: duration_seconds,
		},
	)
	return _join_audio_chunks(response)


def design_voice(prompt, name):
	client = get_client()
	preview_response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICE_DESIGN, constants.API_ATTR_CREATE_PREVIEWS),
		{
			constants.API_KW_VOICE_DESCRIPTION: prompt,
			constants.API_KW_AUTO_GENERATE_TEXT: True,
		},
	)
	previews = _get_collection(preview_response, constants.API_ATTR_PREVIEWS)
	if not previews:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	preview = previews[constants.FIRST_ITEM_INDEX]
	preview_id = _get_attribute(preview, constants.API_KW_GENERATED_VOICE_ID, constants.EMPTY_TEXT)
	if not preview_id:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	voice_response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICE_DESIGN, constants.API_ATTR_CREATE),
		{
			constants.API_KW_GENERATED_VOICE_ID: preview_id,
			constants.API_KW_VOICE_NAME: name,
			constants.API_KW_VOICE_DESCRIPTION: prompt,
		},
	)
	return {
		constants.KEY_VOICE_ID: _get_attribute(voice_response, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT),
		constants.KEY_NAME: _get_attribute(voice_response, constants.API_ATTR_NAME, name),
	}


def clone_voice(name, description, file_paths, remove_background_noise=False):
	if len(file_paths) > constants.CLONE_MAX_AUDIO_FILES:
		raise ElevenDeskAPIError(
			constants.ERROR_CLONE_FILE_LIMIT_TEMPLATE.format(constants.CLONE_MAX_AUDIO_FILES)
		)
	client = get_client()
	opened_files = []
	try:
		for file_path in file_paths:
			opened_files.append(open(file_path, constants.FILE_MODE_BINARY_READ))
		voices_client = _get_sdk_section(client, constants.API_ATTR_VOICES)
		ivc_client = getattr(voices_client, constants.API_ATTR_IVC)
		response = _call_sdk(
			getattr(ivc_client, constants.API_ATTR_CREATE),
			{
				constants.API_KW_NAME: name,
				constants.API_KW_DESCRIPTION: description,
				constants.API_KW_FILES: opened_files,
				constants.API_KW_REMOVE_BACKGROUND_NOISE: remove_background_noise,
				# The SDK serializes omitted labels as "null", which the API rejects.
				constants.API_KW_LABELS: {},
			},
		)
	except (AttributeError, OSError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	finally:
		for opened_file in opened_files:
			opened_file.close()
	return {
		constants.KEY_VOICE_ID: _get_attribute(response, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT),
		constants.KEY_NAME: _get_attribute(response, constants.API_ATTR_NAME, name),
	}


def get_history():
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_LIST),
		{constants.API_KW_PAGE_SIZE: constants.HISTORY_PAGE_SIZE},
	)
	history_items = []
	for item in _get_collection(response, constants.API_ATTR_HISTORY_ITEMS):
		date_value = _get_attribute(item, constants.API_ATTR_DATE, constants.EMPTY_TEXT)
		if isinstance(date_value, (int, float)):
			date_time = datetime.datetime.fromtimestamp(date_value)
			date_value = constants.HISTORY_DATE_TEMPLATE.format(
				date_time.strftime(constants.HISTORY_DATE_PREFIX_FORMAT),
				date_time.day,
				date_time.year,
			)
		history_items.append({
			constants.KEY_HISTORY_ITEM_ID: _get_attribute(item, constants.API_ATTR_HISTORY_ITEM_ID, constants.EMPTY_TEXT),
			constants.KEY_DATE: str(date_value),
			constants.KEY_TYPE: str(_get_attribute(item, constants.API_ATTR_TYPE, constants.EMPTY_TEXT)),
			constants.KEY_VOICE: str(_get_attribute(item, constants.API_ATTR_VOICE_NAME, constants.EMPTY_TEXT)),
			constants.KEY_MODEL: str(_get_attribute(item, constants.API_ATTR_MODEL_ID, constants.EMPTY_TEXT)),
			constants.KEY_PREVIEW: str(_get_attribute(item, constants.API_ATTR_TEXT, constants.EMPTY_TEXT)),
		})
	return history_items


def get_history_audio(history_item_id):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_GET_AUDIO),
		{constants.API_KW_HISTORY_ITEM_ID: history_item_id},
	)
	return _join_audio_chunks(response)


def delete_history_item(history_item_id):
	client = get_client()
	_call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_DELETE),
		{constants.API_KW_HISTORY_ITEM_ID: history_item_id},
	)


def _get_pronunciation_method(method_name):
	return _get_sdk_method(get_client(), constants.API_ATTR_PRONUNCIATION, method_name)


def _get_rules_method(method_name):
	pronunciation_client = _get_sdk_section(get_client(), constants.API_ATTR_PRONUNCIATION)
	return _get_sdk_method(pronunciation_client, constants.API_ATTR_RULES, method_name)


def _format_dictionary(item):
	# Listing and fetching name the version fields "latest_version_*"; creating names them "version_*".
	version_id = _get_attribute(item, constants.API_ATTR_LATEST_VERSION_ID, None)
	if not version_id:
		version_id = _get_attribute(item, constants.API_ATTR_VERSION_ID, constants.EMPTY_TEXT)
	rule_count = _get_attribute(item, constants.API_ATTR_LATEST_VERSION_RULES_NUM, None)
	if rule_count is None:
		rule_count = _get_attribute(item, constants.API_ATTR_VERSION_RULES_NUM, 0)
	return {
		constants.KEY_ID: _get_attribute(item, constants.API_ATTR_ID, constants.EMPTY_TEXT),
		constants.KEY_NAME: _get_attribute(item, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
		constants.KEY_DESCRIPTION: _get_attribute(item, constants.API_ATTR_DESCRIPTION, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
		constants.KEY_VERSION_ID: version_id or constants.EMPTY_TEXT,
		constants.KEY_RULE_COUNT: rule_count or 0,
	}


def _format_rule(rule):
	rule_type = _get_attribute(rule, constants.API_ATTR_RULE_TYPE, constants.EMPTY_TEXT)
	is_phoneme = rule_type == constants.RULE_TYPE_PHONEME
	options = []
	if _get_attribute(rule, constants.API_ATTR_CASE_SENSITIVE, None):
		options.append(constants.RULE_OPTION_CASE_SENSITIVE)
	if _get_attribute(rule, constants.API_ATTR_WORD_BOUNDARIES, None):
		options.append(constants.RULE_OPTION_WORD_BOUNDARIES)
	return {
		constants.KEY_STRING_TO_REPLACE: _get_attribute(rule, constants.API_ATTR_STRING_TO_REPLACE, constants.EMPTY_TEXT),
		constants.KEY_RULE_TYPE: rule_type,
		constants.KEY_REPLACEMENT: _get_attribute(
			rule,
			constants.API_ATTR_PHONEME if is_phoneme else constants.API_ATTR_ALIAS,
			constants.EMPTY_TEXT,
		),
		constants.KEY_ALPHABET: _get_attribute(rule, constants.API_ATTR_ALPHABET, constants.EMPTY_TEXT) if is_phoneme else constants.EMPTY_TEXT,
		constants.KEY_OPTIONS: constants.DETAILS_SEPARATOR.join(options),
	}


def _build_rule(rule):
	# rule is a dictionary keyed by the KEY_* rule constants, as produced by the rule dialog.
	sdk_rule = {
		constants.API_ATTR_RULE_TYPE: rule[constants.KEY_RULE_TYPE],
		constants.API_ATTR_STRING_TO_REPLACE: rule[constants.KEY_STRING_TO_REPLACE],
		constants.API_ATTR_CASE_SENSITIVE: rule[constants.KEY_CASE_SENSITIVE],
		constants.API_ATTR_WORD_BOUNDARIES: rule[constants.KEY_WORD_BOUNDARIES],
	}
	if rule[constants.KEY_RULE_TYPE] == constants.RULE_TYPE_PHONEME:
		sdk_rule[constants.API_ATTR_PHONEME] = rule[constants.KEY_REPLACEMENT]
		sdk_rule[constants.API_ATTR_ALPHABET] = rule[constants.KEY_ALPHABET]
	else:
		sdk_rule[constants.API_ATTR_ALIAS] = rule[constants.KEY_REPLACEMENT]
	return sdk_rule


def get_pronunciation_dictionaries():
	response = _call_sdk(_get_pronunciation_method(constants.API_ATTR_LIST), {})
	return [_format_dictionary(item) for item in _get_collection(response, constants.API_ATTR_DICTIONARIES)]


def get_pronunciation_rules(dictionary_id):
	response = _call_sdk(
		_get_pronunciation_method(constants.API_ATTR_GET),
		{constants.API_KW_PRONUNCIATION_DICTIONARY_ID: dictionary_id},
	)
	return [_format_rule(rule) for rule in _get_collection(response, constants.API_ATTR_RULES)]


def create_pronunciation_dictionary(name, description, rule):
	# The API only creates dictionaries from at least one rule or from a PLS file, never empty ones.
	keyword_arguments = {
		constants.API_KW_NAME: name,
		constants.API_KW_RULES: [_build_rule(rule)],
	}
	if description:
		keyword_arguments[constants.API_KW_DESCRIPTION] = description
	response = _call_sdk(_get_pronunciation_method(constants.API_ATTR_CREATE_FROM_RULES), keyword_arguments)
	return _format_dictionary(response)


def import_pronunciation_dictionary(name, description, file_path):
	keyword_arguments = {constants.API_KW_NAME: name}
	if description:
		keyword_arguments[constants.API_KW_DESCRIPTION] = description
	create_from_file = _get_pronunciation_method(constants.API_ATTR_CREATE_FROM_FILE)
	try:
		with open(file_path, constants.FILE_MODE_BINARY_READ) as dictionary_file:
			keyword_arguments[constants.API_KW_FILE] = dictionary_file
			response = _call_sdk(create_from_file, keyword_arguments)
	except OSError as error:
		raise ElevenDeskAPIError(str(error)) from error
	return _format_dictionary(response)


def rename_pronunciation_dictionary(dictionary_id, name):
	_call_sdk(
		_get_pronunciation_method(constants.API_ATTR_UPDATE),
		{
			constants.API_KW_PRONUNCIATION_DICTIONARY_ID: dictionary_id,
			constants.API_KW_NAME: name,
		},
	)


def archive_pronunciation_dictionary(dictionary_id):
	# The API has no delete endpoint for pronunciation dictionaries; archiving is the only way to remove one.
	_call_sdk(
		_get_pronunciation_method(constants.API_ATTR_UPDATE),
		{
			constants.API_KW_PRONUNCIATION_DICTIONARY_ID: dictionary_id,
			constants.API_KW_ARCHIVED: True,
		},
	)


def download_pronunciation_dictionary(dictionary_id, version_id):
	response = _call_sdk(
		_get_pronunciation_method(constants.API_ATTR_DOWNLOAD),
		{
			constants.API_KW_DICTIONARY_ID: dictionary_id,
			constants.API_KW_VERSION_ID: version_id,
		},
	)
	return _join_audio_chunks(response)


def add_pronunciation_rule(dictionary_id, rule):
	_call_sdk(
		_get_rules_method(constants.API_ATTR_ADD),
		{
			constants.API_KW_PRONUNCIATION_DICTIONARY_ID: dictionary_id,
			constants.API_KW_RULES: [_build_rule(rule)],
		},
	)


def remove_pronunciation_rule(dictionary_id, string_to_replace):
	_call_sdk(
		_get_rules_method(constants.API_ATTR_REMOVE),
		{
			constants.API_KW_PRONUNCIATION_DICTIONARY_ID: dictionary_id,
			constants.API_KW_RULE_STRINGS: [string_to_replace],
		},
	)
