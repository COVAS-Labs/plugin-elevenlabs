"""ElevenLabs Plugin for COVAS:NEXT
Provides ElevenLabs Text-to-Speech and Speech-to-Text capabilities.
"""

from typing import override, Iterable, Any
import io
import speech_recognition as sr

from lib.PluginHelper import PluginHelper, TTSModel, STTModel
from lib.PluginSettingDefinitions import (
    PluginSettings,
    SettingsGrid,
    TextSetting,
    NumericalSetting,
    ModelProviderDefinition,
    ParagraphSetting,
)
from lib.PluginBase import PluginBase, PluginManifest
from lib.Logger import log


class ElevenLabsSTTModel(STTModel):
    """ElevenLabs Speech-to-Text model implementation using Scribe."""
    
    def __init__(
        self,
        api_key: str,
        model_id: str = "scribe_v1",
        language_code: str | None = None,
    ):
        super().__init__("elevenlabs-stt")
        self.api_key = api_key
        self.model_id = model_id
        self.language_code = language_code
        self._client: Any = None
    
    def _get_client(self) -> Any:
        """Lazily initialize the ElevenLabs client."""
        if self._client is None:
            try:
                from elevenlabs.client import ElevenLabs
                
                self._client = ElevenLabs(api_key=self.api_key)
            except ImportError:
                raise ImportError("elevenlabs is not installed. Install it with: pip install elevenlabs")
            except Exception as e:
                log('error', f"Failed to initialize ElevenLabs client: {e}")
                raise
        return self._client
    
    def transcribe(self, audio: sr.AudioData) -> str:
        """Transcribe audio using ElevenLabs Scribe speech-to-text."""
        client = self._get_client()
        
        try:
            # Convert audio to WAV format for the API
            # ElevenLabs accepts various formats including WAV
            wav_data = audio.get_wav_data(convert_rate=16000, convert_width=2)
            audio_file = io.BytesIO(wav_data)
            audio_file.name = "audio.wav"
            
            # Call the speech-to-text API
            kwargs: dict[str, Any] = {
                "file": audio_file,
                "model_id": self.model_id,
            }
            
            if self.language_code:
                kwargs["language_code"] = self.language_code
            
            result = client.speech_to_text.convert(**kwargs)
            
            return result.text.strip() if result.text else ""
            
        except Exception as e:
            log('error', f"ElevenLabs STT transcription failed: {e}")
            raise


class ElevenLabsTTSModel(TTSModel):
    """ElevenLabs Text-to-Speech model implementation with low-latency streaming."""
    
    def __init__(
        self,
        api_key: str,
        model_id: str = "eleven_flash_v2_5",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ):
        super().__init__("elevenlabs-tts")
        self.api_key = api_key
        self.model_id = model_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.style = style
        self.use_speaker_boost = use_speaker_boost
        self._client: Any = None
    
    def _get_client(self) -> Any:
        """Lazily initialize the ElevenLabs client."""
        if self._client is None:
            try:
                from elevenlabs.client import ElevenLabs
                
                self._client = ElevenLabs(api_key=self.api_key)
            except ImportError:
                raise ImportError("elevenlabs is not installed. Install it with: pip install elevenlabs")
            except Exception as e:
                log('error', f"Failed to initialize ElevenLabs client: {e}")
                raise
        return self._client
    
    def synthesize(self, text: str, voice: str) -> Iterable[bytes]:
        """
        Synthesize speech using ElevenLabs Text-to-Speech with low-latency streaming.
        
        Returns PCM audio at 24kHz 16-bit for optimal playback compatibility.
        """
        client = self._get_client()
        
        try:
            # Use streaming TTS with PCM 24kHz output for low latency
            # The pcm_24000 format outputs 16-bit signed little-endian PCM at 24kHz
            audio_stream = client.text_to_speech.stream(
                text=text,
                voice_id=voice,
                model_id=self.model_id,
                output_format="pcm_24000",  # 24kHz 16-bit PCM for low latency
                voice_settings={
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost,
                    "style": self.style,
                    "use_speaker_boost": self.use_speaker_boost,
                },
            )
            
            # Yield audio chunks as they arrive for real-time playback
            for chunk in audio_stream:
                if isinstance(chunk, bytes) and chunk:
                    yield chunk
                    
        except Exception as e:
            log('error', f"ElevenLabs TTS synthesis failed: {e}")
            raise


class ElevenLabsPlugin(PluginBase):
    """
    Plugin providing ElevenLabs Text-to-Speech and Speech-to-Text services for COVAS:NEXT.
    Supports low-latency streaming TTS and Scribe STT with configurable settings.
    """
    
    def __init__(self, plugin_manifest: PluginManifest):
        super().__init__(plugin_manifest)
        
        
        self.settings_config = PluginSettings(
            key="ElevenLabs",
            label="ElevenLabs",
            icon="mic",
            grids=[
                SettingsGrid(
                    key="setup",
                    label="Setup",
                    fields=[
                        ParagraphSetting(
                            key="info_text",
                            label=None,
                            type="paragraph",
                            readonly=False,
                            placeholder=None,
                            
                            content='To use ElevenLabs STT, select it as your "STT provider" in "Advanced" → "STT Settings".',
                        ),
                        ParagraphSetting(
                            key="info_text_tts",
                            label=None,
                            type="paragraph",
                            readonly=False,
                            placeholder=None,
                            
                            content='To use ElevenLabs TTS, select it as your "TTS provider" in "Advanced" → "TTS Settings".',
                        ),
                        ParagraphSetting(
                            key="more_info",
                            label=None,
                            type="paragraph",
                            readonly=False,
                            placeholder=None,
                            
                            content='Make sure to obtain an API key from <a href="https://elevenlabs.io" target="_blank">ElevenLabs</a> and configure the necessary settings for each model provider.',
                        ),
                    ]
                ),
            ]
        )
        
        # Define model providers for STT and TTS
        self.model_providers: list[ModelProviderDefinition] | None = [
            ModelProviderDefinition(
                kind='stt',
                id='elevenlabs-stt',
                label='ElevenLabs STT',
                settings_config=[
                    SettingsGrid(
                        key='credentials',
                        label='Credentials',
                        fields=[
                            TextSetting(
                                key='elevenlabs_api_key',
                                label='API Key',
                                type='text',
                                readonly=False,
                                placeholder='Enter your ElevenLabs API key',
                                default_value='',
                                max_length=None,
                                min_length=None,
                                hidden=True,
                            ),
                        ]
                    ),
                    SettingsGrid(
                        key='settings',
                        label='Settings',
                        fields=[
                            TextSetting(
                                key='elevenlabs_stt_model_id',
                                label='Model ID',
                                type='text',
                                readonly=False,
                                placeholder='scribe_v1',
                                default_value='scribe_v1',
                                max_length=None,
                                min_length=None,
                                hidden=False,
                            ),
                            TextSetting(
                                key='elevenlabs_stt_language',
                                label='Language Code (optional)',
                                type='text',
                                readonly=False,
                                placeholder='en',
                                default_value='',
                                max_length=None,
                                min_length=None,
                                hidden=False,
                            ),
                        ]
                    ),
                ],
            ),
            ModelProviderDefinition(
                kind='tts',
                id='elevenlabs-tts',
                label='ElevenLabs TTS',
                settings_config=[
                    SettingsGrid(
                        key='credentials',
                        label='Credentials',
                        fields=[
                            TextSetting(
                                key='elevenlabs_api_key',
                                label='API Key',
                                type='text',
                                readonly=False,
                                placeholder='Enter your ElevenLabs API key',
                                default_value='',
                                max_length=None,
                                min_length=None,
                                hidden=True,
                            ),
                        ]
                    ),
                    SettingsGrid(
                        key='settings',
                        label='Settings',
                        fields=[
                            TextSetting(
                                key='elevenlabs_model_id',
                                label='Model ID',
                                type='text',
                                readonly=False,
                                placeholder='eleven_flash_v2_5',
                                default_value='eleven_flash_v2_5',
                                max_length=None,
                                min_length=None,
                                hidden=False,
                            ),
                            TextSetting(
                                key='elevenlabs_voice_id',
                                label='Voice ID',
                                type='text',
                                readonly=False,
                                placeholder='JBFqnCBsd6RMkjVDRZzb',
                                default_value='JBFqnCBsd6RMkjVDRZzb',
                                max_length=None,
                                min_length=None,
                                hidden=False,
                            ),
                            NumericalSetting(
                                key='elevenlabs_stability',
                                label='Stability',
                                type='number',
                                readonly=False,
                                placeholder='0.5',
                                default_value=0.5,
                                min_value=0.0,
                                max_value=1.0,
                                step=0.05,
                            ),
                            NumericalSetting(
                                key='elevenlabs_similarity_boost',
                                label='Similarity Boost',
                                type='number',
                                readonly=False,
                                placeholder='0.75',
                                default_value=0.75,
                                min_value=0.0,
                                max_value=1.0,
                                step=0.05,
                            ),
                            NumericalSetting(
                                key='elevenlabs_style',
                                label='Style',
                                type='number',
                                readonly=False,
                                placeholder='0.0',
                                default_value=0.0,
                                min_value=0.0,
                                max_value=1.0,
                                step=0.05,
                            ),
                        ]
                    ),
                ],
            ),
        ]
    
    @override
    def create_model(self, provider_id: str, settings: dict[str, Any]) -> TTSModel | STTModel:
        """Create a model instance for the given provider."""
        
        if provider_id == 'elevenlabs-stt':
            api_key = settings.get('elevenlabs_api_key', '')
            if not api_key:
                raise ValueError('ElevenLabs STT: No API key provided')
            
            model_id = settings.get('elevenlabs_stt_model_id', 'scribe_v1')
            language_code = settings.get('elevenlabs_stt_language', '') or None
            
            return ElevenLabsSTTModel(
                api_key=api_key,
                model_id=model_id,
                language_code=language_code,
            )
        
        elif provider_id == 'elevenlabs-tts':
            api_key = settings.get('elevenlabs_api_key', '')
            if not api_key:
                raise ValueError('ElevenLabs TTS: No API key provided')
            
            model_id = settings.get('elevenlabs_model_id', 'eleven_flash_v2_5')
            stability = float(settings.get('elevenlabs_stability', 0.5))
            similarity_boost = float(settings.get('elevenlabs_similarity_boost', 0.75))
            style = float(settings.get('elevenlabs_style', 0.0))
            
            return ElevenLabsTTSModel(
                api_key=api_key,
                model_id=model_id,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
            )
        
        raise ValueError(f'Unknown ElevenLabs provider: {provider_id}')