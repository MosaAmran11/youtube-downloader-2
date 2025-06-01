import platform
import subprocess
import sys


def install_requirements():
    """Install the required packages using pip."""
    system = platform.system()

    # Install system dependencies on Linux
    if system == "Linux":
        subprocess.run("sudo apt update".split())
        subprocess.run(
            "sudo apt install python3-pip python3-venv".split())

    # Create a virtual environment and install requirements
    subprocess.run(f"{sys.executable} -m venv venv".split(),
                   capture_output=True)
    subprocess.run(
        f"venv/{'bin/python3' if platform.system() == 'Linux' else
                'Scripts/python.exe'} -m pip install -r requirements.txt".split())


if __name__ == "__main__":
    install_requirements()
