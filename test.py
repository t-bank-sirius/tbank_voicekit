from openai import OpenAI
client = OpenAI(
  api_key="sk-or-vv-d23b1436428e55b996edc7f98976a05e4a7ef80147719183abdf0a252fc254a9", # ваш ключ в VseGPT после регистрации
  base_url="https://api.vsegpt.ru/v1",
)

audio_file = open("speech4.m4a", "rb")
transcript = client.audio.transcriptions.create(
  model = "stt-openai/whisper-1",
  response_format="json",
  file=audio_file
)
print(transcript.text)