"""Parsing and editing helpers for Text to Dialogue scripts.

A script is plain text in which a line starting with "@Name:" switches to that voice. Every following line,
blank lines included, belongs to that voice until the next tag. Text before the first tag uses a default voice.
All positions here are indexes into the script string, where each line break counts as one character.
"""

import unicodedata

from elevendesk import constants


class ScriptError(Exception):
	def __init__(self, line_index, message, column=0):
		super().__init__(constants.ERROR_DIALOGUE_LINE_TEMPLATE.format(line_index + constants.INDEX_STEP, message))
		self.line_index = line_index
		# Where on the line the problem is, so the caret can land on it.
		self.column = column


def short_voice_name(name):
	return name.split(constants.VOICE_NAME_DESCRIPTION_SEPARATOR, 1)[0].strip()


def tag_name_for_voice(voice, voices):
	# The short name is enough unless another voice shares it.
	short_name = short_voice_name(voice[constants.KEY_NAME])
	folded = short_name.casefold()
	sharing = [other for other in voices if short_voice_name(other[constants.KEY_NAME]).casefold() == folded]
	if len(sharing) > 1:
		return voice[constants.KEY_NAME]
	return short_name


def line_bounds(text, index):
	start = text.rfind(constants.NEWLINE, 0, index) + constants.INDEX_STEP
	end = text.find(constants.NEWLINE, index)
	if end == -1:
		end = len(text)
	return start, end


def line_index_at(text, index):
	return text.count(constants.NEWLINE, 0, index)


def line_start_index(text, line_index):
	start = 0
	for _ in range(line_index):
		start = text.find(constants.NEWLINE, start)
		if start == -1:
			return len(text)
		start += constants.INDEX_STEP
	return start


def partial_tag_at(text, caret):
	# Returns what has been typed after "@" when the caret sits inside an unfinished tag, otherwise None.
	start, _ = line_bounds(text, caret)
	typed = text[start:caret].lstrip()
	if not typed.startswith(constants.DIALOGUE_TAG_PREFIX) or constants.DIALOGUE_TAG_END in typed:
		return None
	return typed[len(constants.DIALOGUE_TAG_PREFIX):]


def matching_voices(partial, voices):
	folded = partial.strip().casefold()
	return [
		voice for voice in voices
		if constants.DIALOGUE_TAG_END not in voice[constants.KEY_NAME]
		and voice[constants.KEY_NAME].casefold().startswith(folded)
	]


def suggestion_edit(text, caret, voice, voices):
	# Returns (start, end, replacement) that turns the tag being typed into a finished "@Name: ".
	# When the caret is inside an existing tag, the old name, colon and following space are replaced too.
	start, end = line_bounds(text, caret)
	replace_end = caret
	colon = text.find(constants.DIALOGUE_TAG_END, caret, end)
	if colon != -1:
		replace_end = colon + len(constants.DIALOGUE_TAG_END)
		if text.startswith(constants.SPACE, replace_end):
			replace_end += len(constants.SPACE)
	return start, replace_end, constants.DIALOGUE_TAG_TEMPLATE.format(tag_name_for_voice(voice, voices))


def _tag_on_line(line):
	# Spaces before the "@" are allowed: a screen reader does not speak them, so they are easy to leave in by accident.
	line = line.lstrip()
	if not line.startswith(constants.DIALOGUE_TAG_PREFIX):
		return None
	colon = line.find(constants.DIALOGUE_TAG_END)
	if colon == -1:
		return None
	return line[len(constants.DIALOGUE_TAG_PREFIX):colon].strip()


def next_speaker_edit(text, caret, default_tag=None):
	# Returns (position, insertion) for Shift+Enter: a blank line, then a tag for the speaker before the current one,
	# so two voices alternate as on the ElevenLabs website. Returns None when the script is empty.
	if not text.strip():
		return None
	line_start, line_end = line_bounds(text, caret)
	speakers = []
	for line in text[:line_end].split(constants.NEWLINE):
		tag = _tag_on_line(line)
		if tag:
			speakers.append(tag)
		elif line.strip() and not speakers and default_tag:
			# Untagged text at the top is spoken by the default voice, so it takes part in the alternation.
			speakers.append(default_tag)
	speaker = default_tag
	if speakers:
		current = speakers[-1].casefold()
		speaker = next((tag for tag in reversed(speakers) if tag.casefold() != current), speakers[-1])
	# A blank current line already separates the new line from the text above it.
	separator = constants.NEWLINE if not text[line_start:line_end].strip() else constants.NEWLINE * 2
	insertion = separator + (constants.DIALOGUE_TAG_TEMPLATE.format(speaker) if speaker else constants.EMPTY_TEXT)
	return line_end, insertion


def _resolve_voice(tag, voices, line_index):
	if not tag:
		raise ScriptError(line_index, constants.ERROR_DIALOGUE_TAG_EMPTY)
	folded = tag.casefold()
	for voice in voices:
		if voice[constants.KEY_NAME].casefold() == folded:
			return voice
	matches = [voice for voice in voices if short_voice_name(voice[constants.KEY_NAME]).casefold() == folded]
	if len(matches) == 1:
		return matches[0]
	if matches:
		raise ScriptError(line_index, constants.ERROR_DIALOGUE_AMBIGUOUS_VOICE_TEMPLATE.format(tag, len(matches)))
	raise ScriptError(line_index, constants.ERROR_DIALOGUE_UNKNOWN_VOICE_TEMPLATE.format(tag))


def _check_brackets(line, line_index, first_column):
	# Audio tags such as [laughs] never nest or span lines, and braces have no meaning to the API,
	# so any of these is almost certainly a typo that would waste a generation.
	open_column = None
	for column in range(first_column, len(line)):
		character = line[column]
		if character in constants.DIALOGUE_INVALID_CHARACTERS:
			raise ScriptError(line_index, constants.ERROR_DIALOGUE_BRACE_TEMPLATE.format(character), column)
		if character == constants.DIALOGUE_AUDIO_TAG_OPEN:
			if open_column is not None:
				raise ScriptError(line_index, constants.ERROR_DIALOGUE_BRACKET_NESTED, column)
			open_column = column
		elif character == constants.DIALOGUE_AUDIO_TAG_CLOSE:
			if open_column is None:
				raise ScriptError(line_index, constants.ERROR_DIALOGUE_BRACKET_UNOPENED, column)
			open_column = None
	if open_column is not None:
		raise ScriptError(line_index, constants.ERROR_DIALOGUE_BRACKET_UNCLOSED, open_column)


def _has_spoken_text(text):
	# The API rejects the whole request when one voice's text is nothing but audio tags and emojis.
	in_audio_tag = False
	for character in text:
		if character == constants.DIALOGUE_AUDIO_TAG_OPEN:
			in_audio_tag = True
		elif character == constants.DIALOGUE_AUDIO_TAG_CLOSE:
			in_audio_tag = False
		elif not in_audio_tag and unicodedata.category(character).startswith(constants.DIALOGUE_SPOKEN_CATEGORIES):
			return True
	return False


def parse_script(text, voices, default_voice=None):
	# Returns a list of {voice_id, text} dialogue inputs, or raises ScriptError for the first problem found.
	segments = []
	voice = default_voice
	segment_lines = []
	segment_line_index = 0
	# Where the segment's text starts on its first line, which is after the voice tag when there is one.
	segment_column = 0

	def finish_segment():
		segment_text = constants.NEWLINE.join(segment_lines).strip()
		if not segment_text:
			return
		if voice is None:
			raise ScriptError(segment_line_index, constants.ERROR_DIALOGUE_NO_DEFAULT_VOICE)
		if not _has_spoken_text(segment_text):
			first_line = segment_lines[0]
			column = segment_column + len(first_line) - len(first_line.lstrip())
			raise ScriptError(segment_line_index, constants.ERROR_DIALOGUE_NO_SPOKEN_TEXT, column)
		segments.append((segment_line_index, voice, segment_text))

	for line_index, line in enumerate(text.split(constants.NEWLINE)):
		tag_column = len(line) - len(line.lstrip())
		if line.startswith(constants.DIALOGUE_TAG_PREFIX, tag_column):
			colon = line.find(constants.DIALOGUE_TAG_END, tag_column)
			if colon == -1:
				raise ScriptError(line_index, constants.ERROR_DIALOGUE_TAG_COLON, tag_column)
			tagged_voice = _resolve_voice(_tag_on_line(line), voices, line_index)
			_check_brackets(line, line_index, colon + len(constants.DIALOGUE_TAG_END))
			finish_segment()
			voice = tagged_voice
			segment_lines = [line[colon + len(constants.DIALOGUE_TAG_END):]]
			segment_line_index = line_index
			segment_column = colon + len(constants.DIALOGUE_TAG_END)
		else:
			_check_brackets(line, line_index, 0)
			segment_lines.append(line)
	finish_segment()
	if not segments:
		raise ScriptError(0, constants.ERROR_DIALOGUE_SCRIPT_REQUIRED)
	voice_ids = []
	character_count = 0
	for line_index, segment_voice, segment_text in segments:
		voice_id = segment_voice[constants.KEY_VOICE_ID]
		if voice_id not in voice_ids:
			voice_ids.append(voice_id)
			if len(voice_ids) > constants.DIALOGUE_MAX_VOICES:
				raise ScriptError(line_index, constants.ERROR_DIALOGUE_TOO_MANY_VOICES_TEMPLATE.format(
					len(voice_ids), constants.DIALOGUE_MAX_VOICES,
				))
		character_count += len(segment_text)
		if character_count > constants.DIALOGUE_MAX_CHARACTERS:
			raise ScriptError(line_index, constants.ERROR_DIALOGUE_TOO_LONG_TEMPLATE.format(
				character_count, constants.DIALOGUE_MAX_CHARACTERS,
			))
	return [
		{constants.API_KW_VOICE_ID: segment_voice[constants.KEY_VOICE_ID], constants.API_KW_TEXT: segment_text}
		for _, segment_voice, segment_text in segments
	]
