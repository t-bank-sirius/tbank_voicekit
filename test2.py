from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key="sk-or-vv-d23b1436428e55b996edc7f98976a05e4a7ef80147719183abdf0a252fc254a9", # ваш ключ в VseGPT после регистрации
    base_url="https://api.vsegpt.ru/v1",
)

speech_file_path = Path(__file__).parent / "speech7.mp3"
response = client.audio.speech.create(
    model="tts-openai/tts-1",
    voice="nova", # поддерживаются голоса alloy, echo, fable, onyx, nova и shimmer
    input="Сегодня на улице очень жарко, не так ли?",
    # response_format="wav" # другой формат, при необходимости
)

response.write_to_file(speech_file_path)