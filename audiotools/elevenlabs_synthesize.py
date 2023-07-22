import io
import tempfile
from elevenlabs import generate, Voice, VoiceSettings, set_api_key

from pydub import AudioSegment


def elevenlabs_synthesize(text: str, api_key: str):
    set_api_key(api_key)

    tmpfile = tempfile.NamedTemporaryFile(suffix=".ogg")

    audio = generate(
        text=text,
        voice=Voice(
            voice_id='21m00Tcm4TlvDq8ikWAM',
            name='Rachel',
            category='premade',
            description=None,
            labels=None,
            samples=None,
            settings=VoiceSettings(stability=0, similarity_boost=0),
            design=None,
            preview_url=None
        ),
        model="eleven_monolingual_v1"
    )

    AudioSegment.from_file(io.BytesIO(audio)).export(
        tmpfile.name, format='ogg')

    return tmpfile
