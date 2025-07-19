from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from tempfile import NamedTemporaryFile
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="TTS & STT API",
    description="API для синтеза и распознавания речи через VseGPT",
    version="1.0.0"
)

client = OpenAI(
    api_key="sk-or-vv-d23b1436428e55b996edc7f98976a05e4a7ef80147719183abdf0a252fc254a9",
    base_url="https://api.vsegpt.ru/v1",
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"

# TTS — теперь принимает JSON
@app.post("/tts")
async def tts(request: TTSRequest):
    """
    🗣️ Преобразует текст в речь (TTS).
    - *text*: Текст для озвучивания.
    - *voice*: Голос (alloy, echo, fable, onyx, nova, shimmer).
    """
    with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        response = client.audio.speech.create(
            model="tts-openai/tts-1",
            voice=request.voice,
            input=request.text
        )
        response.write_to_file(tmp.name)
        filename = tmp.name

    return FileResponse(
        filename,
        media_type="audio/mpeg",
        filename="speech.mp3"
    )

@app.post("/stt")
async def stt(
    audio: UploadFile = File(...)
):
    """
    ✍️ Распознаёт речь из mp3-файла (STT).
    - *audio*: Аудиофайл формата mp3.
    """
    with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        contents = await audio.read()
        tmp.write(contents)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="stt-openai/whisper-1",
            response_format="json",
            file=audio_file
        )
    return JSONResponse({"text": transcript.text})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8009, reload=True)
