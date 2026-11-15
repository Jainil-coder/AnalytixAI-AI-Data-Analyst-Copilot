import json
from pathlib import Path
from google import genai
from google.genai import types
from google.genai import errors


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"


def get_gemini_client():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "config.json not found in project root."
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    api_key = config.get("API_KEY")

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Please configure your API key in config.json."
        )

    return genai.Client(api_key=api_key)


client = get_gemini_client()

MODEL = "gemini-3.8-flash"


def generate_response(prompt, system_instruction=None):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text

    except errors.APIError as e:

        if getattr(e, "code", None) == 503:
            raise RuntimeError(
                "InsightOS is temporarily experiencing high demand. "
                "Please try again in a few moments."
            ) from e

        elif getattr(e, "code", None) == 429:
            raise RuntimeError(
                "InsightOS request limit reached. Please wait before trying again."
            ) from e

        else:
            raise
