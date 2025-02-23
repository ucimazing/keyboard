# MacBook Client (mac_keyboard_client.py)
from pynput import keyboard
import socket
import time


class KeyboardClient:
    def __init__(self):
        self.host = '192.168.0.62'
        self.port = 65432
        self.enabled = False
        self.socket = None
        self.holding_keys = set()
        self.setup_connection()

    def setup_connection(self):
        while True:
            try:
                if self.socket:
                    self.socket.close()
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                print("✅ Connected to Windows PC")
                break
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)

    def send_key(self, key_str):
        try:
            if not key_str:
                return
            self.socket.send(f"{key_str}\n".encode())
            print(f"Sent: {key_str}")
            return True
        except Exception as e:
            print(f"Error sending key, reconnecting... ({e})")
            self.setup_connection()
            return False

    def run_listener(self):
        def on_press(key):
            # Add key to holding keys
            key_str = str(key)
            self.holding_keys.add(key_str)

            # Check for toggle combination (Command + Shift + Space)
            if ("Key.cmd" in self.holding_keys and
                    "Key.shift" in self.holding_keys and
                    "Key.space" in self.holding_keys):
                self.enabled = not self.enabled
                print(f"Keyboard sharing: {'ON' if self.enabled else 'OFF'}")
                self.holding_keys.clear()  # Clear held keys after toggle
                return True

            # If sharing is enabled, send key to Windows
            if self.enabled:
                try:
                    # Convert key to sendable format
                    if hasattr(key, 'char'):
                        key_str = key.char
                    else:
                        key_str = str(key).replace('Key.', '')

                    self.send_key(key_str)
                    return False  # Block on Mac when enabled
                except Exception as e:
                    print(f"Error handling key: {e}")
                    return False  # Still block on Mac if error

            return True  # Allow normal operation when disabled

        def on_release(key):
            # Remove from holding keys
            key_str = str(key)
            self.holding_keys.discard(key_str)

            if self.enabled:
                return False  # Block key releases when enabled
            return True  # Allow normal operation when disabled

        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release
        ) as listener:
            listener.join()

    def run(self):
        print("Starting keyboard client...")
        print("Press Command + Shift + Space to toggle keyboard sharing")
        print("Current status: OFF")

        while True:  # Keep the program running if the listener stops
            try:
                self.run_listener()
            except Exception as e:
                print(f"Error in listener: {e}")
                print("Restarting listener...")
                time.sleep(1)


if __name__ == "__main__":
    while True:  # Keep the entire program running
        try:
            client = KeyboardClient()
            client.run()
        except Exception as e:
            print(f"Program error: {e}")
            print("Restarting program...")
            time.sleep(3)
