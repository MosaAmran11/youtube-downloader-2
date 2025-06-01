import platform
import subprocess
import sys


def install_requirements():
    """Install the required packages using pip."""
    system = platform.system()

    # Install system dependencies on Linux
    if system == "Linux":
        subprocess.call("sudo apt update".split(), shell=True)
        subprocess.call(
            "sudo apt install python3-pip python3-venv".split(), shell=True)

    # Create a virtual environment and install requirements
    subprocess.call(f"{sys.executable} -m venv venv".split(), shell=True)
    subprocess.call("source ./venv/bin/activate".split(), shell=True)
    subprocess.call(
        f"{sys.executable} -m pip install -r requirements.txt".split(), shell=True)


if __name__ == "__main__":
    install_requirements()
