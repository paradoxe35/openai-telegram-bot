
import openai


def openai_transcribe(file, api_key: str):
    openai.api_key = api_key

    transcript2 = openai.Audio.transcribe(
        file=file,
        model="whisper-1",
        response_format="text",
        language="en"
    )

    return transcript2
