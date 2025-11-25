"""
Groq Vision API Test-Skript
Extrahiert Text aus Bildern mittels Groq Vision-Modell.
"""

import os
import base64
from dotenv import load_dotenv
from groq import Groq

# .env-Datei laden
load_dotenv()

API_KEY = os.getenv("groq_api_key")
if not API_KEY:
    print("Fehler: Groq API-Schlüssel in .env nicht konfiguriert")
    exit(1)

client = Groq(api_key=API_KEY)
MODEL_NAME = "llava-1.5-7b-4096-preview"

def image_to_text(image_path: str) -> str:
    """Extrahiert Text aus einem Bild mittels Groq Vision API"""
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    
    # Bild zu Base64 enkodieren
    img_base64 = base64.standard_b64encode(img_bytes).decode("utf-8")

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Lies NUR den Text im Bild aus und gib ihn als reinen Text zurück in folgenden Format: !!! Dein erkannter Text: <Text>"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ],
            }
        ],
        temperature=0.0,
    )

    return completion.choices[0].message.content[0].text

if __name__ == "__main__":
    screenshot_path = "test_images/image.png"
    text = image_to_text(screenshot_path)
    print(text)
