import customtkinter as ctk
from datetime import datetime
import pyperclip, re, base64
from encryption.crypto          import encrypt_password
from database.db_manager        import DatabaseManager
from ..constants                import ACCENT_COLOR
from ..constants                import APP_ICON
from ..icons                    import load
from ..widgets.toast            import toast
from ..widgets.password_generator import PasswordGeneratorWindow

# icons
copy_icon = load("copy.png",   (18, 18))
eye_icon  = load("eye.png",    (18, 18))
eye_off   = load("eye_off.png",(18, 18))
plus_icon = load("plus.png",   (18, 18))

class AddCredentialWindow(ctk.CTkToplevel):
    """Dialog to create a new credential."""
    def __init__(self, master, master_key: bytes, on_saved):
        super().__init__(master)
        self.master_key = master_key
        self._on_saved  = on_saved
        self.title("Add New Credential")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a1a", padx=28, pady=24)
        self.iconbitmap(str(APP_ICON))

        self._build_ui()
        self._update_strength()

    # User Interface
    def _build_ui(self):
        ctk.CTkLabel(self, text="Add New",
                     font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="center", pady=(0, 16))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack()

        def make_entry(label, var, row, show=""):
            ctk.CTkLabel(form, text=label, anchor="w", text_color="white") \
                .grid(row=row, column=0, sticky="w", padx=(12, 0), pady=4)
            ent = ctk.CTkEntry(form, textvariable=var, width=320, show=show,
                               fg_color="#262626", border_width=2, border_color=ACCENT_COLOR)
            ent.grid(row=row, column=1, padx=8, pady=4, sticky="w")
            return ent

        self.title_var = ctk.StringVar()
        self.user_var  = ctk.StringVar()
        self.pass_var  = ctk.StringVar()
        self.notes_var = ctk.StringVar()

        make_entry("Title / Site",     self.title_var, 0)
        make_entry("Username / Email", self.user_var,  1)

        # Password Row
        ctk.CTkLabel(form, text="Password", anchor="w", text_color="white") \
            .grid(row=2, column=0, sticky="w", padx=(12, 0), pady=4)
        pw_entry = ctk.CTkEntry(form, textvariable=self.pass_var, width=320, show="*",
                                fg_color="#262626", border_width=2, border_color=ACCENT_COLOR)
        pw_entry.grid(row=2, column=1, padx=8, sticky="w", pady=4)

        def toggle():
            if pw_entry.cget("show") == "":
                pw_entry.configure(show="*"); eye_btn.configure(image=eye_icon)
            else:
                pw_entry.configure(show="");  eye_btn.configure(image=eye_off)

        eye_btn = ctk.CTkButton(form, image=eye_icon, text="", width=36, height=32,
                                command=toggle, fg_color=ACCENT_COLOR, hover_color="#0e9f8d")
        eye_btn.grid(row=2, column=2, padx=4)

        ctk.CTkButton(form, image=copy_icon, text="", width=36, height=32,
                      command=lambda: pyperclip.copy(self.pass_var.get()),
                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d") \
            .grid(row=2, column=3, padx=4)

        ctk.CTkButton(form, image=plus_icon, text="", width=36, height=32,
                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                      command=lambda: PasswordGeneratorWindow(
                          self, on_select=self._set_generated_pw)) \
            .grid(row=2, column=4, padx=(12, 8))

        # Notes Box
        ctk.CTkLabel(form, text="Notes (optional)", anchor="w", text_color="white") \
            .grid(row=3, column=0, sticky="w", padx=(12, 0), pady=4)
        notes_box = ctk.CTkTextbox(form, width=320, height=80,
                                   fg_color="#262626", border_width=2,
                                   border_color=ACCENT_COLOR)
        notes_box.grid(row=3, column=1, columnspan=4, padx=8, pady=4, sticky="w")
        notes_box.bind("<<Modified>>",
                       lambda *_: self.notes_var.set(notes_box.get("1.0", "end").strip()))

        # Strength Meter
        meter = ctk.CTkFrame(self, fg_color="transparent")
        meter.pack(pady=10, fill="x")
        self.str_label = ctk.CTkLabel(meter, text="Weak", text_color="red")
        self.str_label.pack(side="left")
        self.str_bar = ctk.CTkProgressBar(meter, width=260, height=10,
                                          progress_color=ACCENT_COLOR)
        self.str_bar.pack(side="left", padx=10)
        self.pass_var.trace_add("write", lambda *_: self._update_strength())

        # Action Buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=12)

        ctk.CTkButton(btns, text="Cancel", width=100,
                      fg_color="#444", hover_color="#666",
                      command=self.destroy).pack(side="left", padx=6)

        self.save_btn = ctk.CTkButton(btns, text="Save", width=160,
                                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                                      state="disabled", command=self._save)
        self.save_btn.pack(side="left", padx=6)

        for var in (self.title_var, self.user_var, self.pass_var):
            var.trace_add("write", lambda *_: self._check_ready())

    # Strength Logic
    def _strength_score(self, pw: str) -> tuple[int, str]:
        if not pw:
            return 0, ""
        classes = sum(bool(re.search(p, pw)) for p in
                      (r"[a-z]", r"[A-Z]", r"\d", r"[^\w\s]"))
        score = min(1.0, (classes * 0.2 + len(pw) / 40))
        label = ("Weak", "Fair", "Good", "Strong", "Very strong")[int(score*4)]
        return score, label

    def _update_strength(self):
        score, label = self._strength_score(self.pass_var.get())
        self.str_bar.set(score)
        colour = ("red" if score < .3 else
                  "orange" if score < .5 else
                  "#f0ad4e" if score < .7 else ACCENT_COLOR)
        self.str_label.configure(text=label, text_color=colour)

    def _set_generated_pw(self, pw: str):
        self.pass_var.set(pw)
        self._update_strength()

    # Validation and Saving
    def _check_ready(self):
        ready = all(v.get().strip()
                    for v in (self.title_var, self.user_var, self.pass_var))
        self.save_btn.configure(state="normal" if ready else "disabled")

    def _save(self):
        enc_pw = encrypt_password(self.pass_var.get(), self.master_key)
        if isinstance(enc_pw, (bytes, bytearray)):
            enc_pw = base64.b64encode(enc_pw).decode()

        DatabaseManager().add_credential(
            title=self.title_var.get().strip(),
            username=self.user_var.get().strip(),
            encrypted_pw=enc_pw,
            notes=self.notes_var.get()
        )
        toast(self, "Saved!")
        self.destroy()
        self._on_saved()
