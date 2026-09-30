APP_NAME = "ElevenDesk"
APP_TITLE = "ElevenDesk"
APP_VERSION = "1.0.0"
CONFIG_FILE_NAME = "settings.json"
MAIN_MODULE_NAME = "__main__"

MODEL_MULTILINGUAL_V2 = "eleven_multilingual_v2"
MODEL_SCRIBE_V2 = "scribe_v2"
MODEL_STS_MULTILINGUAL_V2 = "eleven_multilingual_sts_v2"
# The models endpoint does not list Scribe models, so these are built in.
KNOWN_STT_MODEL_IDS = (
	MODEL_SCRIBE_V2,
)
MODEL_STT_PREFIX = "scribe"
MODEL_ELEVEN_V3 = "eleven_v3"
MODEL_ELEVEN_V4 = "eleven_v4"
# Only these models can speak dialogue; Eleven v3 is kept even if the models endpoint leaves it out.
KNOWN_DIALOGUE_MODEL_IDS = (
	MODEL_ELEVEN_V3,
	MODEL_ELEVEN_V4,
)

OUTPUT_MP3_44100_128 = "mp3_44100_128"
OUTPUT_MP3_44100_192 = "mp3_44100_192"
OUTPUT_PCM_44100 = "pcm_44100"
OUTPUT_ULAW_8000 = "ulaw_8000"
OUTPUT_FORMATS = (
	OUTPUT_MP3_44100_128,
	OUTPUT_MP3_44100_192,
	OUTPUT_PCM_44100,
	OUTPUT_ULAW_8000,
)

KEY_API_KEY = "api_key"
KEY_DEFAULT_MODEL = "default_model"
KEY_DEFAULT_STS_MODEL = "default_sts_model"
KEY_DEFAULT_STT_MODEL = "default_stt_model"
KEY_DEFAULT_VOICE_ID = "default_voice_id"
KEY_DEFAULT_OUTPUT_FORMAT = "default_output_format"
KEY_OUTPUT_DIRECTORY = "output_directory"
KEY_OUTPUT_DEVICE = "output_device"
KEY_INPUT_DEVICE = "input_device"
KEY_TTS_PRONUNCIATION_DICTIONARY_IDS = "tts_pronunciation_dictionary_ids"
KEY_ID = "id"
KEY_VOICE_ID = "voice_id"
KEY_NAME = "name"
KEY_CATEGORY = "category"
KEY_DESCRIPTION = "description"
KEY_DATE = "date"
KEY_TYPE = "type"
KEY_VOICE = "voice"
KEY_MODEL = "model"
KEY_CAN_DO_TTS = "can_do_tts"
KEY_CAN_DO_STS = "can_do_sts"
KEY_PREVIEW = "preview"
KEY_PREVIEW_URL = "preview_url"
KEY_DETAILS = "details"
KEY_PUBLIC_OWNER_ID = "public_owner_id"
KEY_HISTORY_ITEM_ID = "history_item_id"
KEY_AUDIO = "audio"
KEY_FILE_PATH = "file_path"
KEY_FILE_NAME = "file_name"
KEY_FILE_DURATION = "file_duration"
KEY_FILE_FORMAT = "file_format"
KEY_FILE_SAMPLE_RATE = "file_sample_rate"
KEY_FILE_CHANNELS = "file_channels"
KEY_FILE_SIZE = "file_size"
KEY_TIER = "tier"
KEY_SUBSCRIPTION_STATUS = "subscription_status"
KEY_CHARACTER_COUNT = "character_count"
KEY_CHARACTER_LIMIT = "character_limit"
KEY_NEXT_RESET_UNIX = "next_reset_unix"
KEY_CHARACTER_REFRESH_PERIOD = "character_refresh_period"
KEY_BILLING_PERIOD = "billing_period"
KEY_VOICE_SLOTS_USED = "voice_slots_used"
KEY_VOICE_LIMIT = "voice_limit"
KEY_PROFESSIONAL_VOICE_SLOTS_USED = "professional_voice_slots_used"
KEY_PROFESSIONAL_VOICE_LIMIT = "professional_voice_limit"
KEY_VOICE_ADD_EDITS_USED = "voice_add_edits_used"
KEY_MAX_VOICE_ADD_EDITS = "max_voice_add_edits"
KEY_CAN_USE_INSTANT_CLONING = "can_use_instant_cloning"
KEY_CAN_USE_PROFESSIONAL_CLONING = "can_use_professional_cloning"
KEY_OVERAGE_AMOUNT = "overage_amount"
KEY_OVERAGE_CURRENCY = "overage_currency"
KEY_NEXT_INVOICE_CENTS = "next_invoice_cents"
KEY_NEXT_INVOICE_UNIX = "next_invoice_unix"
KEY_CURRENCY = "currency"
KEY_VERSION_ID = "version_id"
KEY_RULE_COUNT = "rule_count"
KEY_USED_IN_TTS = "used_in_tts"
KEY_STRING_TO_REPLACE = "string_to_replace"
KEY_RULE_TYPE = "rule_type"
KEY_REPLACEMENT = "replacement"
KEY_ALPHABET = "alphabet"
KEY_OPTIONS = "options"
KEY_CASE_SENSITIVE = "case_sensitive"
KEY_WORD_BOUNDARIES = "word_boundaries"

EMPTY_TEXT = ""
SPACE = " "
COLON_SPACE = ": "
NEWLINE = "\n"
ELLIPSIS = "..."
DOT = "."
WILDCARD_ALL = "*.*"
JSON_ENCODING = "utf-8"
TEXT_ENCODING = "utf-8"
FILE_MODE_BINARY_READ = "rb"
FILE_MODE_BINARY_WRITE = "wb"
FILE_MODE_TEXT_WRITE = "w"
ID_LIST_SEPARATOR = ","

TAB_TTS = "Text to Speech"
TAB_STT = "Speech to Text"
TAB_STS = "Speech to Speech"
TAB_SFX = "Sound Effects"
TAB_VOICE_DESIGN = "Voice Design"
TAB_DIALOGUE = "Text to Dialogue"
LABEL_VOICE = "Voice"
LABEL_MODEL = "Model"
LABEL_OUTPUT_FORMAT = "Output Format"
LABEL_TEXT = "Text"
LABEL_SCRIPT = "Script"
LABEL_VOICE_SETTINGS = "Voice Settings"
LABEL_STABILITY = "Stability"
LABEL_SIMILARITY = "Similarity Boost"
LABEL_STYLE = "Style"
LABEL_SPEED = "Speed"
LABEL_GENERATE = "Generate"
NAME_GENERATE_SPEECH_SHORTCUT = "Generate speech, Ctrl+Enter"
NAME_PLAY_GENERATED_SPEECH = "Play generated speech"
NAME_SAVE_GENERATED_SPEECH = "Save generated speech"
NAME_GENERATE_SOUND_EFFECT = "Generate sound effect"
NAME_PLAY_GENERATED_SOUND_EFFECT = "Play generated sound effect"
NAME_SAVE_GENERATED_SOUND_EFFECT = "Save generated sound effect"
NAME_GENERATE_DIALOGUE_SHORTCUT = "Generate dialogue, Ctrl+Enter"
NAME_PLAY_GENERATED_DIALOGUE = "Play generated dialogue"
NAME_SAVE_GENERATED_DIALOGUE = "Save generated dialogue"
NAME_DESIGN_NEW_VOICE = "Design new voice"
NAME_VOICE_DESIGN_RESULT = "Designed voice result, read only"
NAME_ADD_DESIGNED_VOICE = "Add designed voice to Text to Speech voice list"
NAME_OPEN_TRANSCRIPTION_AUDIO = "Open audio file for transcription"
NAME_SELECTED_TRANSCRIPTION_FILE = "Selected transcription audio file, read only"
NAME_TRANSCRIBE_SELECTED_AUDIO = "Transcribe selected audio file"
NAME_TRANSCRIPT_OUTPUT = "Transcript output, read only"
NAME_COPY_TRANSCRIPT = "Copy transcript to clipboard"
NAME_SAVE_TRANSCRIPT = "Save transcript to a text file"
NAME_OPEN_STS_AUDIO = "Open audio file for voice conversion"
NAME_SELECTED_STS_FILE = "Selected audio file for conversion, read only"
NAME_CONVERT_STS = "Convert audio with selected voice"
NAME_PLAY_STS_AUDIO = "Play converted audio"
NAME_SAVE_STS_AUDIO = "Save converted audio"
SLIDER_ACCESSIBLE_NAME_TEMPLATE = "{0}, {1} percent"
SPEED_ACCESSIBLE_NAME_TEMPLATE = "{0}, {1:.2f} times normal speed"
LABEL_PLAY = "Play"
LABEL_PAUSE = "Pause"
LABEL_SAVE = "Save"
LABEL_STATUS = "Status"
LABEL_OPEN_AUDIO = "Open Audio File"
LABEL_SELECTED_FILE = "Selected File"
LABEL_TRANSCRIBE = "Transcribe"
LABEL_TRANSCRIPT = "Transcript"
LABEL_COPY = "Copy"
LABEL_SAVE_TRANSCRIPT = "Save Transcript"
LABEL_SOUND_PROMPT = "Describe the sound"
LABEL_DURATION = "Duration (seconds)"
LABEL_VOICE_DESCRIPTION = "Describe the voice"
LABEL_VOICE_NAME = "Name for new voice"
LABEL_DESIGN_VOICE = "Design Voice"
LABEL_RESULT = "Result"
LABEL_ADD_TO_VOICE_LIST = "Add to Voice List"
LABEL_SEARCH = "Search"
LABEL_USE_VOICE = "Use Voice"
LABEL_ADD_FILE = "Add File"
LABEL_ADD_DIRECTORY = "Add Directory"
LABEL_REMOVE_FILE = "Remove File"
LABEL_CLONE = "Clone"
LABEL_VOICE_RIGHTS_CONFIRMATION = "I understand that I have the rights and consent to clone this voice."
LABEL_CLONE_PROGRESS = "Voice cloning progress"
LABEL_DELETE = "Delete"
LABEL_API_KEY = "API Key"
LABEL_DEFAULT_MODEL = "Default Model"
LABEL_DEFAULT_VOICE_ID = "Default Voice ID"
LABEL_DEFAULT_OUTPUT_FORMAT = "Default Output Format"
LABEL_OUTPUT_DIRECTORY = "Output Directory"
LABEL_OUTPUT_DEVICE = "Output Device"
LABEL_INPUT_DEVICE = "Input Device"
LABEL_DEFAULT_DEVICE = "(Default)"
LABEL_BROWSE = "Browse"
LABEL_CANCEL = "Cancel"
LABEL_CLOSE = "Close"
LABEL_AUDIO_FILES = "Audio files"
LABEL_CLONE_HELP = (
	"Eleven v4 needs only about 10 seconds of clear speech from a single speaker to clone a voice. "
	"Older models give better results with 1 to 2 minutes. Avoid music, other voices and reverb."
)
LABEL_REMOVE_BACKGROUND_NOISE = "Remove background noise from the audio samples"
LABEL_CONVERT = "Convert"
LABEL_SHOW = "Show"
LABEL_GENDER = "Gender"
LABEL_AGE = "Age"
LABEL_LANGUAGE = "Language"
LABEL_SORT = "Sort by"
LABEL_PREVIEW = "Preview"
LABEL_STOP = "Stop"
LABEL_LOAD_MORE = "Load More"
LABEL_ADD_TO_MY_VOICES = "Add to My Voices"
LABEL_DICTIONARIES = "Dictionaries"
LABEL_RULES = "Rules"
LABEL_NEW_DICTIONARY = "New Dictionary"
LABEL_IMPORT_DICTIONARY = "Import PLS File"
LABEL_RENAME = "Rename"
LABEL_ARCHIVE = "Archive"
LABEL_DOWNLOAD_DICTIONARY = "Download PLS File"
LABEL_USE_IN_TTS = "Use selected dictionary in Text to Speech"
LABEL_ADD_RULE = "Add Rule"
LABEL_REMOVE_RULE = "Remove Rule"
LABEL_DICTIONARY_NAME = "Dictionary name"
LABEL_DICTIONARY_DESCRIPTION = "Description (optional)"
LABEL_RULE_TEXT = "Word or phrase to replace"
LABEL_RULE_TYPE = "Rule type"
LABEL_ALIAS = "Say it as"
LABEL_PHONEMES = "Phonemes"
LABEL_ALPHABET = "Phoneme alphabet"
LABEL_CASE_SENSITIVE = "Match case"
LABEL_WORD_BOUNDARIES = "Match whole words only"
LABEL_OK = "OK"
LABEL_RULE_HELP = (
	"An alias rule has the voice say other text in place of the word, and works with every model. "
	"A phoneme rule spells out the exact pronunciation, but ElevenLabs only applies phoneme rules "
	"with the Flash v2, Turbo v2 and English v1 models."
)
RULE_TYPE_ALIAS = "alias"
RULE_TYPE_PHONEME = "phoneme"
RULE_TYPES = (
	("Alias", RULE_TYPE_ALIAS),
	("Phoneme", RULE_TYPE_PHONEME),
)
PHONEME_ALPHABETS = (
	("IPA", "ipa"),
	("CMU Arpabet", "cmu-arpabet"),
)
DICTIONARY_IN_TTS = "Yes"
RULE_OPTION_CASE_SENSITIVE = "match case"
RULE_OPTION_WORD_BOUNDARIES = "whole words"
NAME_SEARCH_COMMUNITY = "Search, press Enter to search"
NAME_PREVIEW_VOICE = "Preview selected voice, or press Enter on a voice"
NAME_STOP_PREVIEW = "Stop preview"
NAME_LOAD_MORE_VOICES = "Load more voices"
VOICE_SOURCE_MY_VOICES = "My Voices"
VOICE_SOURCE_COMMUNITY = "Community Library"
VOICE_SOURCES = (
	VOICE_SOURCE_MY_VOICES,
	VOICE_SOURCE_COMMUNITY,
)
FILTER_ANY = "Any"
GENDER_FILTERS = (
	(FILTER_ANY, EMPTY_TEXT),
	("Female", "female"),
	("Male", "male"),
	("Neutral", "neutral"),
)
AGE_FILTERS = (
	(FILTER_ANY, EMPTY_TEXT),
	("Young", "young"),
	("Middle aged", "middle_aged"),
	("Old", "old"),
)
LANGUAGE_FILTERS = (
	(FILTER_ANY, EMPTY_TEXT),
	("Arabic", "ar"),
	("Chinese", "zh"),
	("Dutch", "nl"),
	("English", "en"),
	("French", "fr"),
	("German", "de"),
	("Hindi", "hi"),
	("Indonesian", "id"),
	("Italian", "it"),
	("Japanese", "ja"),
	("Korean", "ko"),
	("Polish", "pl"),
	("Portuguese", "pt"),
	("Russian", "ru"),
	("Spanish", "es"),
	("Swedish", "sv"),
	("Turkish", "tr"),
	("Ukrainian", "uk"),
)
SORT_FILTERS = (
	("Trending", "trending"),
	("Most used", "usage_character_count_1y"),
	("Most cloned", "cloned_by_count"),
	("Newest", "created_date"),
)

MENU_FILE = "&File"
MENU_VIEW = "&View"
MENU_TOOLS = "&Tools"
MENU_SETTINGS = "&Settings"
MENU_HELP = "&Help"
MENU_SAVE_LAST_OUTPUT = "Save Last Output...\tCtrl+S"
MENU_OPEN_AUDIO_FILE = "Open Audio File...\tCtrl+O"
MENU_EXIT = "Exit\tAlt+F4"
MENU_USAGE = "Show Usage Data..."
MENU_VOICE_LIBRARY = "Voice Library..."
MENU_CLONE_VOICE = "Clone Voice..."
MENU_HISTORY = "Generation History..."
MENU_PRONUNCIATION = "Pronunciation Dictionaries..."
MENU_AUDIO_DEVICES = "Audio Devices..."
MENU_PREFERENCES = "Preferences..."
MENU_ABOUT = "About"

TITLE_VOICE_LIBRARY = "Voice Library"
TITLE_CLONE_VOICE = "Clone Voice"
TITLE_HISTORY = "Generation History"
TITLE_PRONUNCIATION = "Pronunciation Dictionaries"
TITLE_AUDIO_DEVICES = "Audio Devices"
TITLE_USAGE = "Usage Data"
TITLE_PREFERENCES = "Preferences"
TITLE_ABOUT = "About ElevenDesk"
TITLE_ERROR = "ElevenDesk Error"
TITLE_SUCCESS = "Success"
TITLE_SELECT_AUDIO = "Select an audio file"
TITLE_SELECT_AUDIO_DIRECTORY = "Select a directory containing audio files"
TITLE_SELECT_OUTPUT_DIRECTORY = "Select output directory"
TITLE_SAVE_AUDIO = "Save audio"
TITLE_SAVE_TRANSCRIPT = "Save transcript"
TITLE_NEW_DICTIONARY = "New Pronunciation Dictionary"
TITLE_ADD_RULE = "Add Pronunciation Rule"
TITLE_RENAME_DICTIONARY = "Rename Dictionary"
TITLE_IMPORT_DICTIONARY = "Select a PLS pronunciation file"
TITLE_SAVE_DICTIONARY = "Save pronunciation dictionary"
TITLE_ARCHIVE_DICTIONARY = "Archive Dictionary"
TITLE_REMOVE_RULE = "Remove Rule"

COLUMN_NAME = "Name"
COLUMN_CATEGORY = "Category"
COLUMN_DESCRIPTION = "Description"
COLUMN_DATE = "Date"
COLUMN_TYPE = "Type"
COLUMN_VOICE = "Voice"
COLUMN_MODEL = "Model"
COLUMN_PREVIEW = "Preview"
COLUMN_ID = "ID"
COLUMN_FILE = "File"
COLUMN_DURATION = "Duration"
COLUMN_FORMAT = "Format"
COLUMN_SAMPLE_RATE = "Sample Rate"
COLUMN_CHANNELS = "Channels"
COLUMN_SIZE = "Size"
COLUMN_PATH = "Path"
COLUMN_DETAILS = "Details"
COLUMN_RULES = "Rules"
COLUMN_TEXT = "Text"
COLUMN_RULE_TYPE = "Type"
COLUMN_REPLACEMENT = "Replacement"
COLUMN_ALPHABET = "Alphabet"
COLUMN_OPTIONS = "Options"

STATUS_CONVERTING = "Converting audio..."
STATUS_CONVERTED = "Audio converted."
STATUS_READY = "Ready"
STATUS_READY_WITH_USAGE_TEMPLATE = "{0} | {1}"
STATUS_LOADING_VOICES = "Loading voices..."
STATUS_GENERATING = "Generating audio..."
STATUS_GENERATED = "Audio generated."
STATUS_TRANSCRIBING = "Transcribing audio..."
STATUS_TRANSCRIBED = "Transcription complete."
STATUS_GENERATING_EFFECT = "Generating sound effect..."
STATUS_EFFECT_GENERATED = "Sound effect generated."
STATUS_GENERATING_DIALOGUE_TEMPLATE = "Generating dialogue: {0} lines, {1} voices, {2:,} characters..."
STATUS_SUGGESTION_TEMPLATE = "{0}, {1} of {2}"
STATUS_NO_MATCHING_VOICES = "No matching voices"
STATUS_DESIGNING_VOICE = "Designing voice..."
STATUS_VOICE_DESIGNED = "Voice designed."
STATUS_CLONING_VOICE = "Cloning voice..."
STATUS_CLONING_FILES_TEMPLATE = "Cloning voice. Uploading {0} audio files..."
STATUS_CLONE_COMPLETE = "Voice cloning complete."
STATUS_CLONE_CLOSE_BLOCKED = "Voice cloning is still in progress. Wait for it to finish."
STATUS_PLAYING = "Playing audio."
STATUS_PAUSED = "Audio paused."
STATUS_LOADING_AUDIO = "Loading audio..."
STATUS_SAVED = "Saved: "
STATUS_COPIED = "Transcript copied."
STATUS_VOICES_REFRESHED = "Voice list refreshed."
STATUS_LOADING = "Loading..."
STATUS_NO_PRONUNCIATION_DICTIONARIES = "No pronunciation dictionaries yet. Use New Dictionary or Import PLS File to create one."
STATUS_DICTIONARIES_LOADED_TEMPLATE = "Dictionaries: {0}."
STATUS_LOADING_RULES = "Loading rules..."
STATUS_RULES_LOADED_TEMPLATE = "{0}, rules: {1}."
STATUS_WORKING = "Working..."
STATUS_DICTIONARY_CREATED_TEMPLATE = "Created {0}."
STATUS_DICTIONARY_RENAMED_TEMPLATE = "Renamed to {0}."
STATUS_DICTIONARY_ARCHIVED_TEMPLATE = "Archived {0}."
STATUS_DICTIONARY_DOWNLOADED = "Saved: "
STATUS_RULE_ADDED_TEMPLATE = "Added a rule for {0}."
STATUS_RULE_REMOVED_TEMPLATE = "Removed the rule for {0}."
STATUS_TTS_DICTIONARY_ON_TEMPLATE = "Text to Speech will use {0}."
STATUS_TTS_DICTIONARY_OFF_TEMPLATE = "Text to Speech will no longer use {0}."
PLACEHOLDER_NO_API_KEY = "No API key. Set one in Preferences."
PLACEHOLDER_LOADING = "Loading..."
PLACEHOLDER_MODELS_FAILED_TEMPLATE = "Models could not be loaded: {0}"
LABEL_VERIFYING_API_KEY = "Verifying API key..."
STATUS_VOICES_LOADED_TEMPLATE = "Voices: {0}."
STATUS_MORE_VOICES_TEMPLATE = "Voices: {0}. More are available with Load More."
STATUS_LOADING_PREVIEW = "Loading preview..."
STATUS_PLAYING_PREVIEW_TEMPLATE = "Playing preview of {0}."
STATUS_PREVIEW_STOPPED = "Preview stopped."
STATUS_ADDING_VOICE_TEMPLATE = "Adding {0} to My Voices..."
STATUS_AUDIO_FILES_ADDED_TEMPLATE = "Added {0} audio files; skipped {1} unreadable files."
STATUS_AUDIO_FILES_LIMIT_TEMPLATE = "Added {0} audio files; skipped {1} unreadable files; {2} files were not added because the maximum is {3}."

ERROR_CONFIG_READ = "The settings file could not be read."
ERROR_CONFIG_WRITE = "The settings file could not be saved."
ERROR_API_KEY_REQUIRED = "Enter an ElevenLabs API key in Preferences."
ERROR_API_KEY_INVALID = "The API key could not be verified."
ERROR_API_REQUEST = "The ElevenLabs request failed."
ERROR_LOAD_VOICES = "Voices could not be loaded."
ERROR_TEXT_REQUIRED = "Enter text to synthesize."
ERROR_VOICE_REQUIRED = "Select a voice."
ERROR_AUDIO_REQUIRED = "Select an audio file."
ERROR_PROMPT_REQUIRED = "Enter a sound description."
ERROR_VOICE_DESCRIPTION_REQUIRED = "Enter a voice description."
ERROR_VOICE_NAME_REQUIRED = "Enter a voice name."
ERROR_CLONE_FILES_REQUIRED = "Add at least one audio file before cloning."
ERROR_CLONE_FILE_LIMIT_TEMPLATE = "Voice cloning accepts no more than {0} audio files."
ERROR_VOICE_RIGHTS_REQUIRED = "Confirm that you have the rights and consent to clone this voice."
ERROR_SELECTION_REQUIRED = "Select an item first."
ERROR_PLAYBACK = "Audio playback failed."
ERROR_SAVE = "The file could not be saved."
ERROR_CLIPBOARD = "The clipboard could not be opened."
ERROR_HISTORY_AUDIO = "Audio is not available for this history item."
ERROR_UNSUPPORTED_AUDIO = "The selected output format cannot be played."
ERROR_AUDIO_METADATA = "Audio metadata could not be read."
ERROR_SDK_RESPONSE = "The ElevenLabs SDK returned an unexpected response."
ERROR_API_REQUEST_ID_TEMPLATE = "{0} Request ID: {1}"
ERROR_DELETE_HISTORY = "The history item could not be deleted."
ERROR_NO_PREVIEW = "This voice has no preview."
ERROR_DICTIONARY_NAME_REQUIRED = "Enter a dictionary name."
ERROR_RULE_TEXT_REQUIRED = "Enter the word or phrase to replace."
ERROR_RULE_REPLACEMENT_REQUIRED = "Enter what the word should be replaced with."
ERROR_DICTIONARY_SELECTION_REQUIRED = "Select a dictionary first."
ERROR_RULE_SELECTION_REQUIRED = "Select a rule first."
ERROR_TTS_DICTIONARY_LIMIT_TEMPLATE = "Text to Speech can use at most {0} dictionaries at once. Stop using another one first."
ERROR_DIALOGUE_SCRIPT_REQUIRED = "Enter a script to generate."
ERROR_DIALOGUE_LINE_TEMPLATE = "Line {0}: {1}"
ERROR_DIALOGUE_TAG_COLON = "the voice tag needs a colon after the voice name."
ERROR_DIALOGUE_TAG_EMPTY = "the voice tag has no voice name."
ERROR_DIALOGUE_UNKNOWN_VOICE_TEMPLATE = "no voice is named {0}."
ERROR_DIALOGUE_AMBIGUOUS_VOICE_TEMPLATE = "{0} matches {1} voices. Use the full voice name."
ERROR_DIALOGUE_NO_DEFAULT_VOICE = "no voice is chosen for this text. Add a voice tag, or select a voice on the Text to Speech tab."
ERROR_DIALOGUE_TOO_MANY_VOICES_TEMPLATE = "this is voice number {0}, but a dialogue can use at most {1}."
ERROR_DIALOGUE_TOO_LONG_TEMPLATE = "the script reaches {0:,} characters here, but a dialogue can be at most {1:,}."
ERROR_DIALOGUE_VOICES_NOT_LOADED = "Voices have not loaded yet. Check the Text to Speech tab."
ERROR_DIALOGUE_BRACE_TEMPLATE = "{0} is not used in scripts. Audio tags use square brackets, such as [laughs]."
ERROR_DIALOGUE_BRACKET_NESTED = "this [ opens before the previous [ on the line is closed."
ERROR_DIALOGUE_BRACKET_UNOPENED = "this ] has no matching [."
ERROR_DIALOGUE_BRACKET_UNCLOSED = "this [ is not closed on the same line."
CONFIRM_ARCHIVE_DICTIONARY_TEMPLATE = (
	"Archive {0}? It will disappear from this list and Text to Speech will stop using it. "
	"ElevenLabs does not allow pronunciation dictionaries to be deleted, only archived."
)
CONFIRM_REMOVE_RULE_TEMPLATE = "Remove the rule for {0}? Every rule for this exact text will be removed."

ABOUT_TEXT_TEMPLATE = "{0} version {1}\nAccessible desktop client for ElevenLabs."
VOICE_RESULT_TEMPLATE = "Name: {0}\nVoice ID: {1}"
VOICE_CHOICE_TEMPLATE = "{0} ({1})"
DETAILS_SEPARATOR = ", "
VOICE_ALREADY_ADDED = "in My Voices"
LABEL_WORD_SEPARATOR = "_"
SLIDER_VALUE_TEMPLATE = "{0}: {1}"
SPEED_VALUE_TEMPLATE = "{0}: {1:.2f}"
SUCCESS_CLONE_TEMPLATE = "Voice cloned.\nVoice ID: {0}"
ERROR_DETAIL_TEMPLATE = "{0}\n\n{1}"

AUDIO_FILE_WILDCARD = "Audio files (*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.opus;*.aac;*.wma)|*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.opus;*.aac;*.wma|All files (*.*)|*.*"
MP3_FILE_WILDCARD = "MP3 audio (*.mp3)|*.mp3|All files (*.*)|*.*"
WAV_FILE_WILDCARD = "WAV audio (*.wav)|*.wav|All files (*.*)|*.*"
PCM_FILE_WILDCARD = "PCM audio (*.pcm)|*.pcm|All files (*.*)|*.*"
ULAW_FILE_WILDCARD = "u-law audio (*.ulaw)|*.ulaw|All files (*.*)|*.*"
BIN_FILE_WILDCARD = "Binary audio (*.bin)|*.bin|All files (*.*)|*.*"
TEXT_FILE_WILDCARD = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
PLS_FILE_WILDCARD = "Pronunciation lexicons (*.pls)|*.pls|All files (*.*)|*.*"
DEFAULT_AUDIO_BASENAME = "elevendesk_audio"
DEFAULT_TRANSCRIPT_BASENAME = "elevendesk_transcript.txt"
EXTENSION_MP3 = ".mp3"
EXTENSION_WAV = ".wav"
EXTENSION_PCM = ".pcm"
EXTENSION_ULAW = ".ulaw"
EXTENSION_BIN = ".bin"
EXTENSION_TXT = ".txt"
EXTENSION_PLS = ".pls"
OUTPUT_FILE_OPTIONS = {
	OUTPUT_MP3_44100_128: (EXTENSION_MP3, MP3_FILE_WILDCARD),
	OUTPUT_MP3_44100_192: (EXTENSION_MP3, MP3_FILE_WILDCARD),
	OUTPUT_PCM_44100: (EXTENSION_PCM, PCM_FILE_WILDCARD),
	OUTPUT_ULAW_8000: (EXTENSION_ULAW, ULAW_FILE_WILDCARD),
}
DEFAULT_OUTPUT_FILE_OPTION = (EXTENSION_BIN, BIN_FILE_WILDCARD)
AUDIO_FILE_EXTENSIONS = (
	".mp3",
	".wav",
	".m4a",
	".flac",
	".ogg",
	".opus",
	".aac",
	".wma",
)

API_ATTR_SPEECH_TO_SPEECH = "speech_to_speech"
API_ATTR_VOICES = "voices"
API_ATTR_GET_ALL = "get_all"
API_ATTR_GET = "get"
API_ATTR_TEXT_TO_SPEECH = "text_to_speech"
API_ATTR_CONVERT = "convert"
API_ATTR_TEXT_TO_DIALOGUE = "text_to_dialogue"
API_ATTR_SPEECH_TO_TEXT = "speech_to_text"
API_ATTR_SOUND_GENERATION = "text_to_sound_effects"
API_ATTR_VOICE_DESIGN = "text_to_voice"
API_ATTR_CREATE = "create"
API_ATTR_CREATE_PREVIEWS = "create_previews"
API_ATTR_PREVIEWS = "previews"
API_ATTR_ADD = "add"
API_ATTR_IVC = "ivc"
API_ATTR_HISTORY = "history"
API_ATTR_DELETE = "delete"
API_ATTR_GET_AUDIO = "get_audio"
API_ATTR_RULES = "rules"
API_ATTR_UPDATE = "update"
API_ATTR_REMOVE = "remove"
API_ATTR_DOWNLOAD = "download"
API_ATTR_CREATE_FROM_RULES = "create_from_rules"
API_ATTR_CREATE_FROM_FILE = "create_from_file"
API_ATTR_LATEST_VERSION_ID = "latest_version_id"
API_ATTR_LATEST_VERSION_RULES_NUM = "latest_version_rules_num"
API_ATTR_VERSION_RULES_NUM = "version_rules_num"
API_ATTR_VERSION_ID = "version_id"
API_ATTR_RULE_TYPE = "type"
API_ATTR_STRING_TO_REPLACE = "string_to_replace"
API_ATTR_ALIAS = "alias"
API_ATTR_PHONEME = "phoneme"
API_ATTR_ALPHABET = "alphabet"
API_ATTR_CASE_SENSITIVE = "case_sensitive"
API_ATTR_WORD_BOUNDARIES = "word_boundaries"
API_ATTR_PRONUNCIATION = "pronunciation_dictionaries"
API_ATTR_LIST = "list"
API_ATTR_DATA = "data"
API_ATTR_VOICE_ID = "voice_id"
API_ATTR_NAME = "name"
API_ATTR_CATEGORY = "category"
API_ATTR_DESCRIPTION = "description"
API_ATTR_MODELS = "models"
API_ATTR_MODEL_ID = "model_id"
API_ATTR_CAN_DO_TTS = "can_do_text_to_speech"
API_ATTR_CAN_DO_STS = "can_do_voice_conversion"
API_ATTR_HISTORY_ITEMS = "history"
API_ATTR_DICTIONARIES = "pronunciation_dictionaries"
API_ATTR_ID = "id"
API_ATTR_DATE = "date_unix"
API_ATTR_TYPE = "source"
API_ATTR_VOICE_NAME = "voice_name"
API_ATTR_TEXT = "text"
API_ATTR_HISTORY_ITEM_ID = "history_item_id"
API_ATTR_GET_SHARED = "get_shared"
API_ATTR_SHARE = "share"
API_ATTR_PREVIEW_URL = "preview_url"
API_ATTR_PUBLIC_OWNER_ID = "public_owner_id"
API_ATTR_HAS_MORE = "has_more"
API_ATTR_LABELS = "labels"
API_ATTR_GENDER = "gender"
API_ATTR_AGE = "age"
API_ATTR_ACCENT = "accent"
API_ATTR_LANGUAGE = "language"
API_ATTR_IS_ADDED_BY_USER = "is_added_by_user"
API_ATTR_USER = "user"
API_ATTR_SUBSCRIPTION = "subscription"
API_ATTR_TIER = "tier"
API_ATTR_STATUS = "status"
API_ATTR_CHARACTER_COUNT = "character_count"
API_ATTR_CHARACTER_LIMIT = "character_limit"
API_ATTR_NEXT_RESET_UNIX = "next_character_count_reset_unix"
API_ATTR_CHARACTER_REFRESH_PERIOD = "character_refresh_period"
API_ATTR_BILLING_PERIOD = "billing_period"
API_ATTR_VOICE_SLOTS_USED = "voice_slots_used"
API_ATTR_VOICE_LIMIT = "voice_limit"
API_ATTR_PROFESSIONAL_VOICE_SLOTS_USED = "professional_voice_slots_used"
API_ATTR_PROFESSIONAL_VOICE_LIMIT = "professional_voice_limit"
API_ATTR_VOICE_ADD_EDIT_COUNTER = "voice_add_edit_counter"
API_ATTR_MAX_VOICE_ADD_EDITS = "max_voice_add_edits"
API_ATTR_CAN_USE_INSTANT_CLONING = "can_use_instant_voice_cloning"
API_ATTR_CAN_USE_PROFESSIONAL_CLONING = "can_use_professional_voice_cloning"
API_ATTR_CURRENT_OVERAGE = "current_overage"
API_ATTR_AMOUNT = "amount"
API_ATTR_CURRENCY = "currency"
API_ATTR_NEXT_INVOICE = "next_invoice"
API_ATTR_AMOUNT_DUE_CENTS = "amount_due_cents"
API_ATTR_NEXT_PAYMENT_ATTEMPT_UNIX = "next_payment_attempt_unix"
API_ERROR_DETAIL = "detail"
API_ERROR_MESSAGE = "message"
API_ERROR_REQUEST_ID = "request_id"

API_KW_TEXT = "text"
API_KW_VOICE_ID = "voice_id"
API_KW_MODEL_ID = "model_id"
API_KW_VOICE_SETTINGS = "voice_settings"
API_KW_OUTPUT_FORMAT = "output_format"
API_KW_FILE = "file"
API_KW_AUDIO = "audio"
API_KW_DURATION_SECONDS = "duration_seconds"
API_KW_PROMPT = "prompt"
API_KW_TEXT_DESCRIPTION = "text"
API_KW_VOICE_DESCRIPTION = "voice_description"
API_KW_VOICE_NAME = "voice_name"
API_KW_GENERATED_VOICE_ID = "generated_voice_id"
API_KW_AUTO_GENERATE_TEXT = "auto_generate_text"
API_KW_NAME = "name"
API_KW_DESCRIPTION = "description"
API_KW_FILES = "files"
API_KW_REMOVE_BACKGROUND_NOISE = "remove_background_noise"
API_KW_LABELS = "labels"
API_KW_PAGE_SIZE = "page_size"
API_KW_VOICE_PREVIEW_ID = "voice_preview_id"
API_KW_HISTORY_ITEM_ID = "history_item_id"
API_KW_SEARCH = "search"
API_KW_GENDER = "gender"
API_KW_AGE = "age"
API_KW_LANGUAGE = "language"
API_KW_SORT = "sort"
API_KW_PAGE = "page"
API_KW_PUBLIC_USER_ID = "public_user_id"
API_KW_NEW_NAME = "new_name"
API_KW_RULES = "rules"
API_KW_RULE_STRINGS = "rule_strings"
API_KW_PRONUNCIATION_DICTIONARY_ID = "pronunciation_dictionary_id"
API_KW_DICTIONARY_ID = "dictionary_id"
API_KW_VERSION_ID = "version_id"
API_KW_ARCHIVED = "archived"
API_KW_PRONUNCIATION_DICTIONARY_LOCATORS = "pronunciation_dictionary_locators"
API_KW_INPUTS = "inputs"
API_KW_SETTINGS = "settings"
API_KEY_SIMILARITY_BOOST = "similarity_boost"
API_KEY_STABILITY = "stability"
API_KEY_STYLE = "style"
API_KEY_SPEED = "speed"

METHOD_SAVE_LAST_OUTPUT = "save_last_output"
METHOD_GET_LAST_OUTPUT = "get_last_output"

DEFAULT_API_KEY = EMPTY_TEXT
DEFAULT_VOICE_ID = EMPTY_TEXT
DEFAULT_MODEL = MODEL_MULTILINGUAL_V2
DEFAULT_STS_MODEL = MODEL_STS_MULTILINGUAL_V2
DEFAULT_STT_MODEL = MODEL_SCRIBE_V2
DEFAULT_OUTPUT_FORMAT = OUTPUT_MP3_44100_128
DEFAULT_OUTPUT_DIRECTORY_NAME = APP_NAME
DEFAULT_SETTINGS = {
	KEY_API_KEY: DEFAULT_API_KEY,
	KEY_DEFAULT_MODEL: DEFAULT_MODEL,
	KEY_DEFAULT_STS_MODEL: DEFAULT_STS_MODEL,
	KEY_DEFAULT_STT_MODEL: DEFAULT_STT_MODEL,
	KEY_DEFAULT_VOICE_ID: DEFAULT_VOICE_ID,
	KEY_DEFAULT_OUTPUT_FORMAT: DEFAULT_OUTPUT_FORMAT,
	KEY_OUTPUT_DIRECTORY: EMPTY_TEXT,
	KEY_OUTPUT_DEVICE: EMPTY_TEXT,
	KEY_INPUT_DEVICE: EMPTY_TEXT,
	KEY_TTS_PRONUNCIATION_DICTIONARY_IDS: EMPTY_TEXT,
}

FRAME_SIZE = (900, 720)
DIALOG_SIZE = (760, 520)
SMALL_DIALOG_SIZE = (620, 440)
PANEL_BORDER = 12
CONTROL_GAP = 8
SECTION_GAP = 12
TEXT_MIN_HEIGHT = 180
RESULT_MIN_HEIGHT = 80
LIST_MIN_HEIGHT = 260
COLUMN_WIDTH_NAME = 180
COLUMN_WIDTH_CATEGORY = 130
COLUMN_WIDTH_DESCRIPTION = 360
COLUMN_WIDTH_DATE = 220
COLUMN_WIDTH_TYPE = 100
COLUMN_WIDTH_VOICE = 140
COLUMN_WIDTH_MODEL = 170
COLUMN_WIDTH_PREVIEW = 260
COLUMN_WIDTH_ID = 240
COLUMN_WIDTH_FILE = 180
COLUMN_WIDTH_DURATION = 100
COLUMN_WIDTH_FORMAT = 80
COLUMN_WIDTH_SAMPLE_RATE = 110
COLUMN_WIDTH_CHANNELS = 90
COLUMN_WIDTH_SIZE = 100
COLUMN_WIDTH_PATH = 360
COLUMN_WIDTH_DETAILS = 220
COLUMN_WIDTH_RULES = 70
COLUMN_WIDTH_TEXT = 180
COLUMN_WIDTH_RULE_TYPE = 90
COLUMN_WIDTH_REPLACEMENT = 200
COLUMN_WIDTH_ALPHABET = 110
COLUMN_WIDTH_OPTIONS = 180
SLIDER_MINIMUM = 0
SLIDER_MAXIMUM = 100
SLIDER_DEFAULT_STABILITY = 50
SLIDER_DEFAULT_SIMILARITY = 75
SLIDER_DEFAULT_STYLE = 0
SLIDER_SPEED_MINIMUM = 70
SLIDER_SPEED_MAXIMUM = 120
SLIDER_SPEED_DEFAULT = 100
SLIDER_SPEED_DIVISOR = 100.0
PERCENT_DIVISOR = 100.0
DURATION_MINIMUM = 0.5
DURATION_MAXIMUM = 22.0
DURATION_DEFAULT = 5.0
DURATION_INCREMENT = 0.5
SPIN_DIGITS = 1
PROGRESS_RANGE = 100
PROGRESS_COMPLETE = 100
PROGRESS_PULSE_INTERVAL_MS = 120
PREVIEW_MAX_LENGTH = 80
HISTORY_PAGE_SIZE = 100
SHARED_VOICES_PAGE_SIZE = 50
PREVIEW_DOWNLOAD_TIMEOUT_SECONDS = 30.0
PREVIEW_OUTPUT_FORMAT = OUTPUT_MP3_44100_128
CLONE_MAX_AUDIO_FILES = 25
TTS_MAX_PRONUNCIATION_DICTIONARIES = 3
DIALOGUE_TAG_PREFIX = "@"
DIALOGUE_TAG_END = ":"
DIALOGUE_TAG_TEMPLATE = "@{0}: "
DIALOGUE_AUDIO_TAG_OPEN = "["
DIALOGUE_AUDIO_TAG_CLOSE = "]"
DIALOGUE_INVALID_CHARACTERS = ("{", "}")
# ElevenLabs voice names often read "Liam - Energetic, Social Media Creator"; tags use the part before the dash.
VOICE_NAME_DESCRIPTION_SEPARATOR = " - "
DIALOGUE_MAX_VOICES = 10
# The API documents 2,000 characters as the reliable limit for one dialogue request.
DIALOGUE_MAX_CHARACTERS = 2000
HISTORY_DATE_PREFIX_FORMAT = "%A, %B"
HISTORY_DATE_TEMPLATE = "{0} {1}, {2}"
FILE_DURATION_TEMPLATE = "{0:.2f} seconds"
FILE_SAMPLE_RATE_TEMPLATE = "{0} Hz"
FILE_SIZE_TEMPLATE = "{0:.2f} MB"
BYTES_PER_MEGABYTE = 1048576.0
AUDIO_SAMPLE_WIDTH = 2
PCM_SAMPLE_RATE = 44100
ULAW_SAMPLE_RATE = 8000
MONO_CHANNEL_COUNT = 1
FORMAT_MP3 = "mp3"
FORMAT_WAV = "wav"
OUTPUT_MP3_PREFIX = "mp3_"
PLAYBACK_POLL_SECONDS = 0.05
ULAW_BYTE_MASK = 255
ULAW_SIGN_BIT = 128
ULAW_EXPONENT_SHIFT = 4
ULAW_EXPONENT_MASK = 7
ULAW_MANTISSA_MASK = 15
ULAW_MANTISSA_SHIFT = 3
ULAW_BIAS = 132
PCM_SAMPLE_PACK_FORMAT = "<h"
THREAD_DAEMON = True
FILE_DIALOG_MULTIPLE = 0
SIZER_PROPORTION_NONE = 0
SIZER_PROPORTION_EXPAND = 1
DEFAULT_SIZE_WIDTH = -1
FIRST_ITEM_INDEX = 0
INDEX_STEP = 1
COLUMN_INDEX_NAME = 0
COLUMN_INDEX_CATEGORY = 1
COLUMN_INDEX_DESCRIPTION = 2
COLUMN_INDEX_DATE = 0
COLUMN_INDEX_TYPE = 1
COLUMN_INDEX_VOICE = 2
COLUMN_INDEX_MODEL = 3
COLUMN_INDEX_PREVIEW = 4
COLUMN_INDEX_FILE = 0
COLUMN_INDEX_DURATION = 1
COLUMN_INDEX_FORMAT = 2
COLUMN_INDEX_SAMPLE_RATE = 3
COLUMN_INDEX_CHANNELS = 4
COLUMN_INDEX_SIZE = 5
COLUMN_INDEX_PATH = 6

USAGE_PERCENT_LEFT_TEMPLATE = "{0}% left"
USAGE_SUMMARY_TEMPLATE = "{0}, resets in {1}"
USAGE_DAY_TEMPLATE = "{0} day"
USAGE_DAYS_TEMPLATE = "{0} days"
USAGE_HOUR_TEMPLATE = "{0} hour"
USAGE_HOURS_TEMPLATE = "{0} hours"
USAGE_LESS_THAN_HOUR = "less than an hour"
USAGE_LINE_TEMPLATE = "{0}: {1}"
USAGE_OF_TEMPLATE = "{0:,} of {1:,}"
USAGE_COUNT_TEMPLATE = "{0:,}"
USAGE_REMAINING_TEMPLATE = "{0:,} ({1} percent)"
USAGE_RESET_TEMPLATE = "{0} (in {1})"
USAGE_DATE_TEMPLATE = "{0} {1}, {2} at {3}"
USAGE_TIME_FORMAT = "%I:%M %p"
USAGE_TIME_LEADING_ZERO = "0"
USAGE_MONEY_TEMPLATE = "{0} {1}"
USAGE_CENTS_TEMPLATE = "{0:.2f}"
USAGE_INVOICE_TEMPLATE = "{0}, due {1}"
USAGE_AVAILABLE = "Available"
USAGE_NOT_AVAILABLE = "Not available"
USAGE_LABEL_PLAN = "Plan"
USAGE_LABEL_STATUS = "Subscription status"
USAGE_LABEL_CHARACTERS_USED = "Characters used"
USAGE_LABEL_CHARACTERS_REMAINING = "Characters remaining"
USAGE_LABEL_NEXT_RESET = "Next reset"
USAGE_LABEL_REFRESH_PERIOD = "Character refresh period"
USAGE_LABEL_BILLING_PERIOD = "Billing period"
USAGE_LABEL_VOICE_SLOTS = "Voice slots used"
USAGE_LABEL_PROFESSIONAL_VOICE_SLOTS = "Professional voice slots used"
USAGE_LABEL_VOICE_ADD_EDITS = "Voice additions and edits used"
USAGE_LABEL_INSTANT_CLONING = "Instant voice cloning"
USAGE_LABEL_PROFESSIONAL_CLONING = "Professional voice cloning"
USAGE_LABEL_OVERAGE = "Current usage-based overage"
USAGE_LABEL_NEXT_INVOICE = "Next invoice"
USAGE_PERIOD_NAMES = {
	"monthly_period": "Monthly",
	"3_month_period": "Every 3 months",
	"6_month_period": "Every 6 months",
	"annual_period": "Annually",
}
SECONDS_PER_DAY = 86400
SECONDS_PER_HOUR = 3600
CENTS_PER_UNIT = 100.0
