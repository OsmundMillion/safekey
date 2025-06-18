import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import os
import json
import base64
from encryption.key_derivation import verify_password
from gui.constants import APP_ICON

# Paths
ASSETS_DIR = "assets"
DATA_PATH = "data"
KEY_FILE = os.path.join(DATA_PATH, "master.key")

# User Interface for the login screen
class LoginScreen(ctk.CTk):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success

        ctk.set_appearance_mode("dark")
        self.title("SafeKey - Login")
        self.geometry("880x520")
        self.configure(bg="#121212")
        self.resizable(False, False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.iconbitmap(str(APP_ICON))

        image_path = os.path.join(ASSETS_DIR, "card_passwords.png")
        image = Image.open(image_path)
        img = CTkImage(light_image=image, dark_image=image, size=(400, 480))

        image_label = ctk.CTkLabel(self, image=img, text="")
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")


        wrapper = ctk.CTkFrame(
            self,
            fg_color="#1e1e1e",
            corner_radius=12,
            border_width=3,
            border_color="#00c9a7"
        )
        wrapper.grid(row=0, column=1, padx=40, pady=40, sticky="nsew")
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(wrapper, fg_color="transparent", width=400, height=440)
        form_frame.grid(row=0, column=0, padx=15, pady=15)
        form_frame.grid_propagate(False)
        form_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        form_frame.grid_columnconfigure(0, weight=1)

        app_label = ctk.CTkLabel(
            form_frame,
            text="SafeKey",
            font=("Segoe UI", 26, "bold"),
            text_color="#00c9a7"
        )
        app_label.grid(row=0, column=0, pady=(20, 10), padx=20)

        heading = ctk.CTkLabel(
            form_frame,
            text="Unlock Your Vault",
            font=("Segoe UI", 20, "bold"),
            text_color="#00c9a7",
            wraplength=360,
            justify="center"
        )
        heading.grid(row=1, column=0, pady=(5, 20), padx=20)

        self.password_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Enter Master Password", width=300, height=40, show="●"
        )
        self.password_entry.grid(row=2, column=0, pady=(0, 10))

        self.message_label = ctk.CTkLabel(form_frame, text="", font=("Segoe UI", 12))
        self.message_label.grid(row=3, column=0, pady=(0, 10))

        self.login_button = ctk.CTkButton(
            form_frame,
            text="Login",
            text_color="black",
            command=self.verify_login,
            width=300,
            height=40,
            fg_color="#00c9a7",
            hover_color="#338e8f",
            corner_radius=10,
        )
        self.login_button.grid(row=4, column=0, pady=(5, 20))

    # Verify login credentials
    def verify_login(self):
        entered_pw = self.password_entry.get()

        try:
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
                stored_salt = data["salt"]
                stored_hash = data["hash"]
        except FileNotFoundError:
            self.message_label.configure(text="Master key file not found.", text_color="red")
            return

        if verify_password(entered_pw, stored_salt, stored_hash):
            key = base64.b64decode(stored_hash)
            self.message_label.configure(text="Access granted!", text_color="green")
            self.key = key
            if self.on_success:
                self.after(800, self._safe_close_and_continue)
            else:
                self.after(800, self.destroy)
        else:
            self.message_label.configure(text="Incorrect password. Try again.", text_color="red")

    # Safely close the window
    def _safe_close_and_continue(self):
        if self.winfo_exists():
            self.destroy()
            self.on_success(self.key)
