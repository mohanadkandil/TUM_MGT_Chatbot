import json
from urllib.parse import quote
import requests


message_content = "How do I hand my thesis in?"  # Example content, adjust as needed

url = "http://localhost:8000/chat_stream?question=" + quote(message_content)
data = {
    "conversation": [
        {
            "role": "user",  # Assuming 'user' or 'system' roles, adjust as needed
            "content": "test",
        }
    ],
    "uuid": "test",
    "study_program": "BMT",
}

headers = {"Accept": "application/json", "Content-Type": "application/json"}


with requests.post(url, data=json.dumps(data), headers=headers, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)
