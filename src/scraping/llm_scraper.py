import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")



def get_property_list_with_llm(
    page_text: str, first_parameter: str, second_parameter: str
) -> str:
    """Extracts job property using a local LLM via Ollama."""
    if not page_text or not first_parameter or not second_parameter:
        return ""
    try:
        # Limit the text length to avoid giant payloads or context limit issues just in case
        page_text = page_text[:10000]

        prompt = (
            f"Extract {first_parameter} from the following job offer text. "
            f"Return ONLY a comma-separated list of the {second_parameter}. If you cannot find any, return an empty string. "
            "Do not include any introductions, explanations, or extra text.\n\n"
            f"Job offer text:\n{page_text}"
        )

        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()

        result = response.json().get("response", "").strip()
        return result
    except Exception as e:
        print(f"Failed to get {second_parameter} from Ollama: {e}")
        return ""


def get_property_with_llm(
    page_text: str, property_name: str, list_of_options: str
) -> str:
    """Extracts job property using a local LLM via Ollama."""
    if not page_text or not property_name or not list_of_options:
        return ""
    try:
        # Limit the text length to avoid giant payloads or context limit issues just in case
        page_text = page_text[:10000]

        prompt = (
            f"Extract {property_name} from the following job offer text. "
            f"Return ONLY one option from following list {list_of_options}. If you cannot find any, return an empty string. "
            "Do not include any introductions, explanations, or extra text.\n\n"
            f"Job offer text:\n{page_text}"
        )

        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()

        result = response.json().get("response", "").strip()
        return result
    except Exception as e:
        print(f"Failed to get {property_name} from Ollama: {e}")
        return ""


def get_responsibilities_with_llm(page_text: str) -> str:
    """Extracts job responsibilities using a local LLM via Ollama."""
    first_parameter = "the key responsibilities (daily tasks, duties, expectations)"
    second_parameter = "the responsibilities"
    return get_property_list_with_llm(page_text, first_parameter, second_parameter)


def get_requirements_with_llm(page_text: str) -> str:
    """Extracts job requirements using a local LLM via Ollama."""
    first_parameter = (
        "the key requirements (technologies, tools, frameworks, experience, etc.)"
    )
    second_parameter = "the requirements"
    return get_property_list_with_llm(page_text, first_parameter, second_parameter)


def get_benefits_with_llm(page_text: str) -> str:
    """Extracts job benefits using a local LLM via Ollama."""
    first_parameter = "the benefits"
    second_parameter = "the benefits. Don't include the salary range"
    return get_property_list_with_llm(page_text, first_parameter, second_parameter)


def get_location_type_with_llm(page_text: str) -> str:
    """Extracts job location type using a local LLM via Ollama."""

    property_name = "the location type (office, remote, hybrid)"
    list_of_options = "office, remote, hybrid"

    return get_property_with_llm(page_text, property_name, list_of_options)

def get_location_type_with_llm(page_text: str) -> str:
    """Extracts job location type using a local LLM via Ollama."""

    property_name = "the location type (office, remote, hybrid)"
    list_of_options = "office, remote, hybrid"

    return get_property_with_llm(page_text, property_name, list_of_options)
