import io
import logging
import tempfile
import traceback

import requests
from pydub import AudioSegment


logger = logging.getLogger("synthesize")


class WitSynthesizer:
    speech_url = "https://api.wit.ai/synthesize?v=20230215"

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": "Bearer " + api_key,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json"
            }
        )

    def synthesize(self, text):
        content: bytes | None
        try:
            response = self.session.post(
                self.speech_url,
                json={
                    "q": text,
                    "voice": "Rosie",
                    "style": "soft",
                    "speed": 95,
                    "pitch": 100
                }
            )
            content = response.content

        except requests.exceptions.RequestException as e:
            logger.error("Could not synthesize chunk: %s",
                         traceback.format_exc())

        return content

    def close(self):
        self.session.close()


def witai_synthesize(text: str, api_key: str):
    tmpfile = tempfile.NamedTemporaryFile(suffix=".ogg")

    transcriber = WitSynthesizer(api_key)
    content = transcriber.synthesize(text)

    AudioSegment.from_file(io.BytesIO(content)).export(
        tmpfile.name, format='ogg')

    transcriber.close()

    return tmpfile
