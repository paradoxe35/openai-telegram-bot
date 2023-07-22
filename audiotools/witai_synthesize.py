import io
import logging
import tempfile
import traceback

import requests
from pydub import AudioSegment


logger = logging.getLogger("synthesize")


class WitSynthesizer:
    speech_url = "https://api.wit.ai/synthesize"

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
                    "speed": 110,
                    "pitch": 110
                }
            )
            content = response.content

        except requests.exceptions.RequestException as e:
            logger.error("Could not synthesize chunk: %s",
                         traceback.format_exc())

        return content

    def close(self):
        self.session.close()


def chunk_text_message(text: str):
    messages = []
    message = ""
    chunks = text.split(" ")

    for chunk in chunks:
        if len(message) + len(chunk) > 280:
            messages.append(message)
            message = ""
        message += f" {chunk}" if len(message) > 0 else chunk

    messages.append(message)

    return messages


def witai_synthesize(text: str, api_key: str):
    chuncked_message = chunk_text_message(text)
    tmpfile = tempfile.NamedTemporaryFile(suffix=".ogg")

    transcriber = WitSynthesizer(api_key)

    lists = []
    for chunk in chuncked_message:
        lists.append(transcriber.synthesize(chunk))

    AudioSegment.from_file(io.BytesIO(b"".join(lists))).export(
        tmpfile.name,
        format='ogg'
    )

    transcriber.close()

    return tmpfile
