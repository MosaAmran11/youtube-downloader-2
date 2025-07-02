#!/usr/bin/env python3
"""
Port Checker Script
Check what's using a specific port and help troubleshoot binding issues
"""

import socket
import subprocess
import platform
import sys


def check_port(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


def find_process_using_port(port: int) -> str:
    """Find which process is using a specific port"""
    system = platform.system()

    try:
        if system == "Windows":
            # Use netstat on Windows
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.split('\n'):
                if f':{port} ' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        # Try to get process name
                        try:
                            task_result = subprocess.run(
                                ['tasklist', '/FI', f'PID eq {pid}'],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            for task_line in task_result.stdout.split('\n'):
                                if pid in task_line and 'PID' not in task_line:
                                    return f"PID {pid}: {task_line.split()[0]}"
                        except:
                            pass
                        return f"PID {pid}"

        else:
            # Use lsof on Unix systems
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header line
                    process_info = lines[1].split()
                    if len(process_info) >= 9:
                        return f"PID {process_info[1]}: {process_info[0]}"
                    elif len(process_info) >= 2:
                        return f"PID {process_info[1]}"

    except Exception as e:
        return f"Error checking process: {e}"

    return "Unknown process"


def main():
    """Main function"""
    port = 5000

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    print(f"🔍 Checking port {port}...")

    if check_port(port):
        print(f"✅ Port {port} is available")
    else:
        print(f"❌ Port {port} is in use")
        process = find_process_using_port(port)
        print(f"   Process using port: {process}")

        print("\n💡 Solutions:")
        print("1. Close the application using the port")
        print("2. Use a different port:")
        print(f"   set FLASK_PORT={port + 1} && python main.py")
        print("3. Kill the process (if safe to do so)")

        if platform.system() == "Windows":
            print("4. Run as administrator if it's a system service")


if __name__ == '__main__':
    main()
