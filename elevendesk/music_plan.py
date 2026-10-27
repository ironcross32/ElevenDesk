"""Parsing and formatting for the plain-text music composition plan.

A plan is a list of sections. Each starts with a line such as "[Verse 1] 30", giving the section name and its
length in seconds. Inside a section, a line starting with "+" lists styles to include and a line starting with
"-" lists styles to avoid, both comma separated. Every other line is a lyric line, which may hold inline
directions in curly braces, such as {guitar solo}. Blank lines are ignored.
Sections become the chunks of a v2 composition plan: {text, duration_ms, positive_styles, negative_styles}.
"""

from elevendesk import constants


class MusicPlanError(Exception):
	def __init__(self, line_index, message):
		super().__init__(constants.ERROR_DIALOGUE_LINE_TEMPLATE.format(line_index + constants.INDEX_STEP, message))
		self.line_index = line_index


def _split_styles(text):
	return [style.strip() for style in text.split(constants.MUSIC_PLAN_STYLE_SEPARATOR) if style.strip()]


def _parse_section_line(line, line_index):
	# Returns (name, duration_ms), or None when the line is not a section line.
	if not line.startswith(constants.MUSIC_PLAN_SECTION_OPEN):
		return None
	close = line.find(constants.MUSIC_PLAN_SECTION_CLOSE)
	if close == -1:
		return None
	name = line[len(constants.MUSIC_PLAN_SECTION_OPEN):close].strip()
	if len(name) > constants.MUSIC_SECTION_NAME_MAX_LENGTH:
		raise MusicPlanError(
			line_index,
			constants.ERROR_MUSIC_SECTION_NAME_LENGTH_TEMPLATE.format(constants.MUSIC_SECTION_NAME_MAX_LENGTH),
		)
	try:
		seconds = float(line[close + len(constants.MUSIC_PLAN_SECTION_CLOSE):].strip())
	except ValueError:
		raise MusicPlanError(line_index, constants.ERROR_MUSIC_SECTION_DURATION) from None
	if not constants.MUSIC_SECTION_MINIMUM_SECONDS <= seconds <= constants.MUSIC_SECTION_MAXIMUM_SECONDS:
		raise MusicPlanError(
			line_index,
			constants.ERROR_MUSIC_SECTION_DURATION_RANGE_TEMPLATE.format(
				constants.MUSIC_SECTION_MINIMUM_SECONDS,
				constants.MUSIC_SECTION_MAXIMUM_SECONDS,
			),
		)
	return name, round(seconds * constants.MILLISECONDS_PER_SECOND)


def _finish_section(section):
	lines = section.pop(constants.KEY_LINES)
	name = section.pop(constants.KEY_NAME)
	if name:
		lines.insert(constants.FIRST_ITEM_INDEX, constants.MUSIC_PLAN_SECTION_OPEN + name + constants.MUSIC_PLAN_SECTION_CLOSE)
	section[constants.API_ATTR_TEXT] = constants.NEWLINE.join(lines)
	return section


def parse(text):
	chunks = []
	section = None
	total_ms = 0
	maximum_ms = constants.MUSIC_LENGTH_MAXIMUM * constants.MILLISECONDS_PER_SECOND
	for line_index, raw_line in enumerate(text.split(constants.NEWLINE)):
		line = raw_line.strip()
		if not line:
			continue
		section_line = _parse_section_line(line, line_index)
		if section_line is not None:
			if section is not None:
				chunks.append(_finish_section(section))
			name, duration_ms = section_line
			total_ms += duration_ms
			if total_ms > maximum_ms:
				raise MusicPlanError(
					line_index,
					constants.ERROR_MUSIC_PLAN_TOO_LONG_TEMPLATE.format(format_length(total_ms), format_length(maximum_ms)),
				)
			section = {
				constants.KEY_NAME: name,
				constants.KEY_LINES: [],
				constants.API_ATTR_DURATION_MS: duration_ms,
				constants.API_ATTR_POSITIVE_STYLES: [],
				constants.API_ATTR_NEGATIVE_STYLES: [],
			}
			continue
		if section is None:
			raise MusicPlanError(line_index, constants.ERROR_MUSIC_SECTION_REQUIRED)
		if line.startswith(constants.MUSIC_PLAN_STYLES_PREFIX):
			section[constants.API_ATTR_POSITIVE_STYLES].extend(_split_styles(line[len(constants.MUSIC_PLAN_STYLES_PREFIX):]))
		elif line.startswith(constants.MUSIC_PLAN_NEGATIVE_STYLES_PREFIX):
			section[constants.API_ATTR_NEGATIVE_STYLES].extend(_split_styles(line[len(constants.MUSIC_PLAN_NEGATIVE_STYLES_PREFIX):]))
		else:
			if len(line) > constants.MUSIC_LINE_MAX_LENGTH:
				raise MusicPlanError(line_index, constants.ERROR_MUSIC_LINE_TOO_LONG_TEMPLATE.format(constants.MUSIC_LINE_MAX_LENGTH))
			if len(section[constants.KEY_LINES]) >= constants.MUSIC_SECTION_MAX_LINES:
				raise MusicPlanError(line_index, constants.ERROR_MUSIC_TOO_MANY_LINES_TEMPLATE.format(constants.MUSIC_SECTION_MAX_LINES))
			section[constants.KEY_LINES].append(line)
	if section is None:
		raise MusicPlanError(constants.FIRST_ITEM_INDEX, constants.ERROR_MUSIC_PLAN_EMPTY)
	chunks.append(_finish_section(section))
	return chunks


def format_plan(chunks):
	# Writes chunks (as returned by api.create_music_plan) back out as plan text.
	output = []
	for chunk in chunks:
		lines = chunk[constants.API_ATTR_TEXT].split(constants.NEWLINE)
		name = constants.EMPTY_TEXT
		first = lines[constants.FIRST_ITEM_INDEX].strip() if lines else constants.EMPTY_TEXT
		if first.startswith(constants.MUSIC_PLAN_SECTION_OPEN) and first.endswith(constants.MUSIC_PLAN_SECTION_CLOSE):
			name = first[len(constants.MUSIC_PLAN_SECTION_OPEN):-len(constants.MUSIC_PLAN_SECTION_CLOSE)].strip()
			lines = lines[constants.INDEX_STEP:]
		seconds = chunk[constants.API_ATTR_DURATION_MS] / constants.MILLISECONDS_PER_SECOND
		output.append(constants.MUSIC_PLAN_SECTION_TEMPLATE.format(name, constants.MUSIC_PLAN_SECONDS_FORMAT.format(seconds)))
		for prefix, attribute_name in (
			(constants.MUSIC_PLAN_STYLES_PREFIX, constants.API_ATTR_POSITIVE_STYLES),
			(constants.MUSIC_PLAN_NEGATIVE_STYLES_PREFIX, constants.API_ATTR_NEGATIVE_STYLES),
		):
			styles = chunk.get(attribute_name) or []
			if styles:
				output.append(constants.MUSIC_PLAN_STYLES_TEMPLATE.format(prefix, constants.MUSIC_PLAN_STYLE_JOINER.join(styles)))
		output.extend(line.strip() for line in lines if line.strip())
	return constants.NEWLINE.join(output)


def total_ms(chunks):
	return sum(chunk[constants.API_ATTR_DURATION_MS] for chunk in chunks)


def _plural(count, singular_template, plural_template):
	return (singular_template if count == 1 else plural_template).format(count)


def format_length(milliseconds):
	# "1 minute 30 seconds" reads better through speech than "1:30".
	seconds = round(milliseconds / constants.MILLISECONDS_PER_SECOND)
	minutes, seconds = divmod(seconds, constants.SECONDS_PER_MINUTE)
	parts = []
	if minutes:
		parts.append(_plural(minutes, constants.MUSIC_MINUTE_TEMPLATE, constants.MUSIC_MINUTES_TEMPLATE))
	if seconds or not minutes:
		parts.append(_plural(seconds, constants.MUSIC_SECOND_TEMPLATE, constants.MUSIC_SECONDS_TEMPLATE))
	return constants.SPACE.join(parts)


def format_summary(chunks):
	return (
		_plural(len(chunks), constants.MUSIC_SECTION_TEMPLATE, constants.MUSIC_SECTIONS_TEMPLATE),
		format_length(total_ms(chunks)),
	)
