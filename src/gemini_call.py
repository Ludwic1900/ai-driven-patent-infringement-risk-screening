from google import genai
import os

client = genai.Client(api_key="你的key")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="能帮我用Python写一个 hello world 程序么？",
)
os.makedirs("logs", exist_ok=True)

with open("logs/response.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print(response.text)
