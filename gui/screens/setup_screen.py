import customtkinter as ctk
from PIL import Image
from customtkinter import CTkImage
import os
import json
from encryption.key_derivation import hash_master_password
from gui.constants import APP_ICON

ASSETS_DIR = "assets"
DATA_PATH = "data"
KEY_FILE = os.path.join(DATA_PATH, "master.key")
os.makedirs(DATA_PATH, exist_ok=True)

class SetupScreen(ctk.CTk):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success

        ctk.set_appearance_mode("dark")
        self.title("SafeKey - Setup")
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
        form_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
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
            text="Enter Your Master Password",
            font=("Segoe UI", 20, "bold"),
            text_color="#00c9a7",
            wraplength=360,
            justify="center"
        )
        heading.grid(row=1, column=0, pady=(5, 20), padx=20)


        self.password_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Enter Password", width=300, height=40, show="●"
        )
        self.password_entry.grid(row=2, column=0, pady=(0, 10))

        self.confirm_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Confirm Password", width=300, height=40, show="●"
        )
        self.confirm_entry.grid(row=3, column=0, pady=(0, 20))

        self.message_label = ctk.CTkLabel(form_frame, text="", font=("Segoe UI", 12))
        self.message_label.grid(row=4, column=0, pady=(0, 10))

        self.submit_button = ctk.CTkButton(
            form_frame,
            text="Save & Continue",
            text_color="black",
            command=self.save_master_password,
            width=300,
            height=40,
            fg_color="#c4435b",
            hover_color="#338e8f",
            corner_radius=10,
        )
        self.submit_button.grid(row=5, column=0, pady=(10, 20))

    def save_master_password(self):
        pw = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not pw or not confirm:
            self.message_label.configure(text="Both fields are required.", text_color="red")
            return

        if pw != confirm:
            self.message_label.configure(text="Passwords do not match.", text_color="red")
            return

        salt, key_hash = hash_master_password(pw)

        with open(KEY_FILE, "w") as f:
            json.dump({"salt": salt, "hash": key_hash}, f)

        self.message_label.configure(text="Master password saved!", text_color="green")

        if self.on_success:
            self.after(800, self._safe_continue)
        else:
            self.after(800, self.destroy)

    def _safe_continue(self):
        if self.winfo_exists():
            self.destroy()
            self.on_success()
