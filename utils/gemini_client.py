import json
from pathlib import Path

from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"


def get_gemini_client():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.json not found in project root."
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    api_key = config.get("GEMINI_API_KEY")

    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError(
            "Please configure your Gemini API key in config.json."
        )

    return genai.Client(api_key=api_key)


client = get_gemini_client()

MODEL = "gemini-3.8-flash"


def generate_response(prompt, system_instruction=None):

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text