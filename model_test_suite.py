import os
import json
import csv
import base64
import time
from datetime import datetime
import google.generativeai as genai
from mistralai.client import MistralClient
from groq import Groq
from PIL import Image

# --- Konfiguration ---
SETTINGS_FILE = "settings.json"
IMAGE_PATH = "test_images/image.png"
PROMPT = "Extrahiere den gesamten Text aus diesem Bild. Gib ausschließlich den transkribierten Text zurück, ohne zusätzliche Kommentare oder Formatierungen."
CSV_OUTPUT_FILE = "model_test_results.csv"
REQUEST_PAUSE_SECONDS = 20

# --- Hilfsfunktionen ---

def load_api_keys():
    """Lädt die API-Schlüssel aus der Einstellungsdatei."""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return {
                "gemini": config.get("gemini_api_key"),
                "mistral": config.get("mistral_api_key"),
                "groq": config.get("groq_api_key"),
            }
    except FileNotFoundError:
        print(f"FEHLER: Die Einstellungsdatei '{SETTINGS_FILE}' wurde nicht gefunden.")
        return None

def encode_image_to_base64(image_path):
    """Kodiert ein Bild in einen Base64-String."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"FEHLER: Die Bilddatei '{image_path}' wurde nicht gefunden.")
        return None

def write_to_csv(writer, provider, model, prompt, response):
    """Schreibt eine Ergebniszeile in die CSV-Datei."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_prompt = f"{prompt} (Bild: {os.path.basename(IMAGE_PATH)})"
    cleaned_response = ' '.join(str(response).splitlines())
    writer.writerow([timestamp, provider, model, full_prompt, cleaned_response])
    print(f"  - Ergebnis für {model} gespeichert.")

# --- Intelligente Filterfunktionen ---

def get_gemini_models(client):
    """Ruft alle Modelle ab, die generateContent unterstützen."""
    all_models = client.list_models()
    return [model.name for model in all_models if 'generateContent' in model.supported_generation_methods]

def get_mistral_models(client):
    """Ruft alle verfügbaren Mistral-Modelle ab."""
    response = client.models.list()
    return [model.id for model in response.data]

def get_groq_models(client):
    """Ruft alle verfügbaren Groq-Modelle ab."""
    response = client.models.list()
    return [model.id for model in response.data]


# --- Hauptlogik ---

def main():
    """Führt den Modell-Test-Suite aus."""
    print("Starte den Modell-Test-Suite...")

    api_keys = load_api_keys()
    if not api_keys:
        return

    all_models_to_test = {}

    # --- Modelle abrufen und filtern ---
    print("\n--- Rufe verfügbare Modelle von den APIs ab... ---")

    # Gemini
    gemini_api_key = api_keys.get("gemini")
    if gemini_api_key and "YOUR_API_KEY_HERE" not in gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            all_models_to_test["Gemini"] = get_gemini_models(genai)
        except Exception as e:
            print(f"FEHLER beim Abrufen der Gemini-Modelle: {e}")

    # Mistral
    mistral_api_key = api_keys.get("mistral")
    if mistral_api_key and "YOUR_API_KEY_HERE" not in mistral_api_key:
        try:
            mistral_client = MistralClient(api_key=mistral_api_key)
            all_models_to_test["Mistral"] = get_mistral_models(mistral_client)
        except Exception as e:
            print(f"FEHLER beim Abrufen der Mistral-Modelle: {e}")

    # Groq
    groq_api_key = api_keys.get("groq")
    if groq_api_key and "YOUR_API_KEY_HERE" not in groq_api_key:
        try:
            groq_client = Groq(api_key=groq_api_key)
            all_models_to_test["Groq"] = get_groq_models(groq_client)
        except Exception as e:
            print(f"FEHLER beim Abrufen der Groq-Modelle: {e}")

    # --- Verifikations-Ausgabe ---
    print("\n--- Folgende Modelle werden getestet: ---")
    for provider, models in all_models_to_test.items():
        if models:
            print(f"  - {provider}: {', '.join(models)}")
        else:
            print(f"  - {provider}: Keine passenden Modelle gefunden oder API-Schlüssel fehlt.")
    print("-" * 40)


    with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Zeitstempel", "Anbieter", "Modell", "Prompt", "Antwort"])

        # --- Gemini-Tests ---
        if "Gemini" in all_models_to_test:
            print("\n--- Teste Gemini-Modelle ---")
            try:
                image = Image.open(IMAGE_PATH)
                for model_name in all_models_to_test["Gemini"]:
                    print(f"Teste Modell: {model_name}...")
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([PROMPT, image])
                        result = response.text.strip()
                    except Exception as e:
                        result = f"FEHLER: {e}"
                    write_to_csv(csv_writer, "Gemini", model_name, PROMPT, result)
                    print(f"Warte {REQUEST_PAUSE_SECONDS} Sekunden...")
                    time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER während der Gemini-Tests: {e}")

        # --- Mistral-Tests ---
        if "Mistral" in all_models_to_test:
            print("\n--- Teste Mistral-Modelle ---")
            try:
                mistral_client = MistralClient(api_key=mistral_api_key)
                base64_image = encode_image_to_base64(IMAGE_PATH)
                for model_name in all_models_to_test["Mistral"]:
                    print(f"Teste Modell: {model_name}...")
                    try:
                        messages = [{"role": "user", "content": [{"type": "text", "text": PROMPT}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}]
                        response = mistral_client.chat.completions.create(model=model_name, messages=messages)
                        result = response.choices[0].message.content.strip()
                    except Exception as e:
                        result = f"FEHLER: {e}"
                    write_to_csv(csv_writer, "Mistral", model_name, PROMPT, result)
                    print(f"Warte {REQUEST_PAUSE_SECONDS} Sekunden...")
                    time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER während der Mistral-Tests: {e}")

        # --- Groq-Tests ---
        if "Groq" in all_models_to_test:
            print("\n--- Teste Groq-Modelle ---")
            try:
                groq_client = Groq(api_key=groq_api_key)
                base64_image = encode_image_to_base64(IMAGE_PATH)
                for model_name in all_models_to_test["Groq"]:
                    print(f"Teste Modell: {model_name}...")
                    try:
                        chat_completion = groq_client.chat.completions.create(messages=[{"role": "user", "content": [{"type": "text", "text": PROMPT}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}], model=model_name)
                        result = chat_completion.choices[0].message.content.strip()
                    except Exception as e:
                        result = f"FEHLER: {e}"
                    write_to_csv(csv_writer, "Groq", model_name, PROMPT, result)
                    print(f"Warte {REQUEST_PAUSE_SECONDS} Sekunden...")
                    time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER während der Groq-Tests: {e}")

    print(f"\nTest-Suite abgeschlossen. Ergebnisse wurden in '{CSV_OUTPUT_FILE}' gespeichert.")

if __name__ == "__main__":
    main()
