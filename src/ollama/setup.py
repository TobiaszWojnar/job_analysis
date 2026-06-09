import os
import sys
import subprocess
import time
import requests
import builtins
from dotenv import load_dotenv


# Force all print statements to flush immediately, preventing log buffering issues with subprocesses
def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    builtins.print(*args, **kwargs)


load_dotenv()

OLLAMA_API_URL = "http://localhost:11434"


def get_ollama_command():
    """Finds the ollama executable command or path."""
    # Check if 'ollama' is in the system PATH
    try:
        subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return "ollama"
    except FileNotFoundError:
        pass

    # Check typical Windows installation path if not in PATH
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        fallback_path = os.path.join(local_app_data, "Programs", "Ollama", "Ollama.exe")
        if os.path.exists(fallback_path):
            return fallback_path

    return None


def is_ollama_running():
    """Checks if Ollama server is responding to API requests."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def wait_for_ollama(timeout=60):
    """Polls the Ollama API until it becomes available."""
    print("Waiting for Ollama to respond...", end="", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_ollama_running():
            print(" Connected!")
            return True
        print(".", end="", flush=True)
        time.sleep(1)
    print("\nError: Timeout waiting for Ollama to start.")
    return False

def check_model_exists(model_name):
    """Checks if the specified model is already pulled in Ollama."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            for m in models_data:
                name = m.get("name", "")
                # Normalize names (e.g. handle tags like ':latest')
                if name.lower() == model_name.lower():
                    return True
                if name.lower().startswith(model_name.lower() + ":"):
                    return True
                if model_name.lower().startswith(name.lower() + ":"):
                    return True
    except Exception as e:
        print(f"\nWarning: Failed to retrieve model list from Ollama API: {e}")
    return False


def ensure_ollama_ready(model_name):
    """Ensures Ollama is running and has the specified model pulled."""
    # 1. Check if Ollama is running, start it if not
    print("Checking Ollama status...")
    if not is_ollama_running():
        print("Ollama is not running. Attempting to start it...")
        ollama_cmd = get_ollama_command()
        if not ollama_cmd:
            print(
                "Error: 'ollama' command not found in PATH or standard installation directory.",
                file=sys.stderr,
            )
            print("Please make sure Ollama is installed and running.", file=sys.stderr)
            sys.exit(1)

        try:
            # Launch ollama serve in the background
            subprocess.Popen(
                [ollama_cmd, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f"Error starting Ollama: {e}", file=sys.stderr)
            sys.exit(1)

        # Wait for Ollama to become available
        if not wait_for_ollama():
            sys.exit(1)
    else:
        print("Ollama is already running.")

    # 2. Verify that the specified model is present
    print(f"Verifying presence of model: {model_name}")
    if check_model_exists(model_name):
        print(f"Model '{model_name}' is ready.")
    else:
        print(f"Model '{model_name}' not found locally. Attempting to pull it...")
        ollama_cmd = get_ollama_command() or "ollama"
        try:
            # Use subprocess.run to stream the pull progress to the terminal
            subprocess.run([ollama_cmd, "pull", model_name], check=True)
            print(f"Model '{model_name}' pulled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to pull model '{model_name}': {e}", file=sys.stderr)
            sys.exit(1)
