# ElevenDesk

A desktop client for the ElevenLabs API. Not affiliated with or endorsed by ElevenLabs.

## Why this project exists

I created ElevenDesk because the accessibility of the ElevenLabs website has been degrading. Tasks that should be straightforward with a keyboard and screen reader have become harder to complete reliably.

## Requirements

- Python 3.13 or 3.14
- An ElevenLabs API key
- Windows or macOS
- A working audio output device

## Installation

Install dependencies with [uv](https://docs.astral.sh/uv/):

```shell
uv sync
```

Run ElevenDesk:

```shell
uv run python -m elevendesk
```

On first launch, ElevenDesk opens Preferences so you can enter your API key and choose an output directory.

## API key storage

The API key is saved to ElevenDesk's per-user settings file outside the repository:

- Windows: `%APPDATA%\ElevenDesk\settings.json`
- macOS: standard per-user application data directory

## Keyboard shortcuts

- `Ctrl+Enter` — generate and play speech (Text to Speech and Text to Dialogue tabs)
- `Shift+Enter` — start the next speaker's line (Text to Dialogue script)
- `Ctrl+S` — save last output
- `Ctrl+O` — open audio file for transcription

## Features

- Text to speech with voice, model, output format, and voice setting controls
- Text to dialogue: multi-speaker scripts with up to 10 voices (see below)
- Speech to text transcription
- Sound effect generation
- Voice design and cloning
- Voice library browser
- Generation history with playback and download
- Character quota and subscription details (View > Show Usage Data), with a summary in the status line
- Pronunciation dictionaries: create, import and download PLS files, add and remove alias or phoneme rules, rename, archive, and choose up to three to apply in Text to Speech
- Recursive audio directory import for voice cloning


## Writing dialogue scripts

On the Text to Dialogue tab, a line that starts with `@Name:` switches to that voice. Everything after it, including blank lines and audio tags such as `[door slams]`, is spoken by that voice until the next tag. Text before the first tag uses the voice selected on the Text to Speech tab.

```
The door creaks open.

@Alice: [whispering] Is anyone there?

@Bob: Just me.
```

- Type `@` at the start of a line to hear matching voices. Keep typing to narrow the list, use `Up` and `Down` to move through it, and press `Tab` or `Enter` to insert the voice. `Escape` closes the list, and `Left` or `Right` closes it and moves the cursor.
- `Shift+Enter` adds a blank line and a tag for the speaker before the current one, so two voices alternate. After a third voice speaks, it alternates between that voice and the one before it.
- Tags use the part of the voice name before " - ". If two voices share that name, the full name is inserted instead.
- A script can use up to 10 voices and 2,000 characters of spoken text. Square brackets must be paired on the same line and not nested, and curly braces are not allowed. Problems are announced with their line number, and the cursor moves to the spot.
