import os
import sys
import subprocess
import time
import socket
import builtins
from dotenv import load_dotenv

# Force all print statements to flush immediately, preventing log buffering issues with subprocesses
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    builtins.print(*args, **kwargs)

load_dotenv()

def is_docker_installed():
    """Checks if the docker CLI command is available on the system."""
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def is_docker_running():
    """Checks if the Docker daemon is running."""
    try:
        # 'docker info' returns 0 exit code if daemon is running
        res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False

def start_docker_desktop(timeout=90):
    """Attempts to launch Docker Desktop and waits for it to become ready."""
    docker_desktop_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if not os.path.exists(docker_desktop_path):
        print(f"Error: Docker Desktop not found at '{docker_desktop_path}'. Please start Docker manually.", file=sys.stderr)
        return False

    print("Docker daemon is not running. Launching Docker Desktop...")
    try:
        subprocess.Popen([docker_desktop_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error launching Docker Desktop: {e}", file=sys.stderr)
        return False

    print("Waiting for Docker daemon to start...", end="", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_docker_running():
            print(" Connected!")
            return True
        print(".", end="", flush=True)
        time.sleep(3)
    print("\nError: Timeout waiting for Docker daemon to start.")
    return False

def rabbitmq_container_exists():
    """Checks if a Docker container named 'rabbitmq' exists (running or stopped)."""
    try:
        res = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=^/rabbitmq$", "-q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return bool(res.stdout.strip())
    except Exception:
        return False

def is_rabbitmq_container_running():
    """Checks if the 'rabbitmq' Docker container is currently running."""
    try:
        res = subprocess.run(
            ["docker", "ps", "--filter", "name=^/rabbitmq$", "--filter", "status=running", "-q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return bool(res.stdout.strip())
    except Exception:
        return False

def start_rabbitmq_container():
    """Starts the existing stopped 'rabbitmq' container."""
    print("Starting stopped 'rabbitmq' container...")
    try:
        res = subprocess.run(["docker", "start", "rabbitmq"], stdout=subprocess.DEVNULL, stderr=sys.stderr)
        return res.returncode == 0
    except Exception as e:
        print(f"Error starting 'rabbitmq' container: {e}", file=sys.stderr)
        return False

def create_rabbitmq_container():
    """Creates and starts a new 'rabbitmq' container."""
    print("Creating and starting a new 'rabbitmq' container from 'rabbitmq:3-management'...")
    try:
        res = subprocess.run(
            ["docker", "run", "-d", "--name", "rabbitmq", "-p", "5672:5672", "-p", "15672:15672", "rabbitmq:3-management"],
            stdout=subprocess.DEVNULL,
            stderr=sys.stderr
        )
        return res.returncode == 0
    except Exception as e:
        print(f"Error creating 'rabbitmq' container: {e}", file=sys.stderr)
        return False

def wait_for_rabbitmq_port(host, port, timeout=45):
    """Polls the RabbitMQ port until it starts accepting TCP connections."""
    print(f"Waiting for RabbitMQ at {host}:{port} to accept connections...", end="", flush=True)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(" Connected!")
                # Give it a tiny bit of extra time to finish AMQP protocol startup
                time.sleep(2)
                return True
        except (socket.timeout, ConnectionRefusedError):
            pass
        print(".", end="", flush=True)
        time.sleep(2)
    print("\nError: Timeout waiting for RabbitMQ connection.")
    return False

def ensure_rabbitmq_ready():
    """Ensures Docker is running and RabbitMQ container is up and listening."""
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", 5672))

    # 1. Verify Docker installation
    if not is_docker_installed():
        print("Error: 'docker' CLI is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)

    # 2. Ensure Docker daemon is running
    if not is_docker_running():
        if not start_docker_desktop():
            sys.exit(1)

    # 3. Ensure 'rabbitmq' container is running
    if not is_rabbitmq_container_running():
        if rabbitmq_container_exists():
            if not start_rabbitmq_container():
                sys.exit(1)
        else:
            if not create_rabbitmq_container():
                sys.exit(1)
    else:
        print("RabbitMQ container is already running.")

    # 4. Wait for RabbitMQ port to be active
    if not wait_for_rabbitmq_port(host, port):
        sys.exit(1)

if __name__ == "__main__":
    ensure_rabbitmq_ready()
