import os
import customtkinter as ctk
from gui.screens.setup_screen   import SetupScreen
from gui.screens.login_screen   import LoginScreen
from gui.screens.dashboard      import DashboardScreen

KEY_FILE = os.path.join("data", "master.key")

ctk.set_appearance_mode("dark")

class SafeKeyApp:
    def __init__(self):
        self.key = None
        self.start_app()

    # Decide whether to run setup or login
    def start_app(self):
        if not os.path.exists(KEY_FILE):
            self.show_setup()
        else:
            self.show_login()

    # First‐time setup screen
    def show_setup(self):
        SetupScreen(on_success=self.show_login).mainloop()

    # Login screen
    def show_login(self):
        LoginScreen(on_success=self.set_key_and_open_dashboard).mainloop()

    # After login, open the vault dashboard
    def set_key_and_open_dashboard(self, key: bytes):
        self.key = key
        DashboardScreen(master_key=self.key).mainloop()

if __name__ == "__main__":
    SafeKeyApp()
