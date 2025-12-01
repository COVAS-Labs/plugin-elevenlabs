# COVAS:NEXT ElevenLabs Plugin

ElevenLabs Text-to-Speech and Speech-to-Text integration for COVAS:NEXT.


## Features

- **Low-latency streaming TTS**: Uses ElevenLabs streaming API for real-time audio output
- **24kHz 16-bit PCM output**: Optimized audio format for COVAS:NEXT playback
- **Configurable voice settings**: Adjust stability, similarity boost, and style
- **Multiple TTS model support**: Use any ElevenLabs TTS model (eleven_flash_v2_5, eleven_multilingual_v2, etc.)
- **Scribe STT**: High-quality speech-to-text transcription with language support


## Installation

Download the latest release under the *Releases* section on the right. Follow the instructions on [COVAS:NEXT Plugins](https://ratherrude.github.io/Elite-Dangerous-AI-Integration/plugins/) to install the plugin.

Unpack the plugin into the `plugins` folder in the COVAS:NEXT AppData folder, leading to the following folder structure:
* `plugins`
    * `cn-plugin-elevenlabs`
        * `cn-plugin-elevenlabs.py`
        * `requirements.txt`
        * `deps`
        * `__init__.py`
        * etc.
    * `OtherPlugin`


## TTS Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| API Key | Your ElevenLabs API key | (required) |
| Model ID | The TTS model to use | eleven_flash_v2_5 |
| Voice ID | The voice to use for synthesis | JBFqnCBsd6RMkjVDRZzb |
| Stability | Voice stability (0.0-1.0) | 0.5 |
| Similarity Boost | Voice similarity boost (0.0-1.0) | 0.75 |
| Style | Voice style exaggeration (0.0-1.0) | 0.0 |


## STT Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| API Key | Your ElevenLabs API key | (required) |
| Model ID | The STT model to use | scribe_v1 |
| Language Code | Language hint for transcription (optional) | (auto-detect) |


## TTS Models

Recommended models for low latency:
- `eleven_flash_v2_5` - Fastest, lowest latency (default)
- `eleven_turbo_v2_5` - Fast with good quality
- `eleven_multilingual_v2` - Best quality, higher latency


## STT Models

- `scribe_v1` - High-quality transcription (default)
- `scribe_v1_experimental` - Experimental features


## Getting Your API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io)
2. Go to your profile settings
3. Copy your API key


## Finding Voice IDs

You can find voice IDs in the ElevenLabs Voice Library or by using their API.
The default voice ID `JBFqnCBsd6RMkjVDRZzb` is "George".

# Development
During development, clone the COVAS:NEXT repository and place your plugin-project in the plugins folder.  
Install the dependencies to your local .venv virtual environment using `pip`, by running this command in the `cn-plugin-elevenlabs` folder:
```bash
  pip install -r requirements.txt
```

Follow the [COVAS:NEXT Plugin Development Guide](https://ratherrude.github.io/Elite-Dangerous-AI-Integration/plugins/Development/) for more information on developing plugins.

## Packaging
Use the `./pack.ps1` or `./pack.sh` scripts to package the plugin and any Python dependencies in the `deps` folder.

## Releasing
This project includes a GitHub Actions workflow that automatically creates releases. To create a new release:

1. Tag your commit with a version number:
   ```bash
   git tag v1.0.0
   ```
2. Push the tag to GitHub:
   ```bash
   git push origin v1.0.0
   ```

The workflow will automatically build the plugin using the pack script and create a GitHub Release with the zip file attached.
    
## Acknowledgements

 - [COVAS:NEXT](https://github.com/RatherRude/Elite-Dangerous-AI-Integration)
