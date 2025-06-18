import customtkinter as ctk, base64, re, pyperclip
from CTkMessagebox import CTkMessagebox
from encryption.crypto   import encrypt_password
from database.db_manager import DatabaseManager
from ..constants         import ACCENT_COLOR
from ..icons             import load
from ..widgets.toast     import toast
from ..widgets.password_generator import PasswordGeneratorWindow


copy_ic  = load("copy.png",   (18, 18))
eye_ic   = load("eye.png",    (18, 18))
eye_off  = load("eye_off.png",(18, 18))
gen_ic   = load("plus.png",   (18, 18))
del_ic   = load("delete.png", (18, 18))

class EditCredentialWindow(ctk.CTkToplevel):
    """Dialog to edit (or delete) an existing credential."""
    def __init__(self, master, cred: dict, master_key: bytes, on_saved):
        super().__init__(master)
        self.cred       = cred
        self.master_key = master_key
        self._on_saved  = on_saved

        self.title(f"Edit – {cred['title']}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a1a", padx=28, pady=24)

        # pre-filled vars
        self.title_var = ctk.StringVar(value=cred["title"])
        self.user_var  = ctk.StringVar(value=cred["username"])
        self.pass_var  = ctk.StringVar(value=cred["password"])
        self.notes_var = ctk.StringVar(value=cred.get("notes", ""))

        self._build_ui()
        self._update_strength()

    # UI (mostly identical to Add window)
    def _build_ui(self):
        ctk.CTkLabel(self, text="Edit Credential",
                     font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="center", pady=(0, 16))

        form = ctk.CTkFrame(self, fg_color="transparent"); form.pack()

        def lbl(row, text):
            ctk.CTkLabel(form, text=text, anchor="w", text_color="white") \
                .grid(row=row, column=0, sticky="w", padx=(12, 0), pady=4)

        def entry(row, var, show=""):
            ent = ctk.CTkEntry(form, textvariable=var, width=320, show=show,
                               fg_color="#262626", border_width=2,
                               border_color=ACCENT_COLOR)
            ent.grid(row=row, column=1, padx=8, pady=4, sticky="w")
            return ent

        lbl(0, "Title / Site");     entry(0, self.title_var)
        lbl(1, "Username / Email"); entry(1, self.user_var)

        # password row
        lbl(2, "Password")
        pw_entry = entry(2, self.pass_var, show="*")

        def toggle():
            if pw_entry.cget("show") == "":
                pw_entry.configure(show="*"); eye.configure(image=eye_ic)
            else:
                pw_entry.configure(show="");  eye.configure(image=eye_off)

        eye = ctk.CTkButton(form, image=eye_ic, text="", width=36, height=32,
                            fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                            command=toggle)
        eye.grid(row=2, column=2, padx=4)

        ctk.CTkButton(form, image=copy_ic, text="", width=36, height=32,
                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                      command=lambda: pyperclip.copy(self.pass_var.get())) \
            .grid(row=2, column=3, padx=4)

        ctk.CTkButton(form, image=gen_ic, text="", width=36, height=32,
                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                      command=lambda: PasswordGeneratorWindow(
                          self, on_select=self._set_generated_pw)) \
            .grid(row=2, column=4, padx=(12, 8))

        # notes
        lbl(3, "Notes (optional)")
        notes_box = ctk.CTkTextbox(form, width=320, height=80,
                                   fg_color="#262626", border_width=2,
                                   border_color=ACCENT_COLOR)
        notes_box.grid(row=3, column=1, columnspan=4, padx=8, pady=4, sticky="w")
        notes_box.insert("1.0", self.notes_var.get())
        notes_box.bind("<<Modified>>",
                       lambda *_: self.notes_var.set(notes_box.get("1.0", "end").strip()))

        # strength meter
        meter = ctk.CTkFrame(self, fg_color="transparent"); meter.pack(pady=10)
        self.str_label = ctk.CTkLabel(meter, text="", text_color="red"); self.str_label.pack(side="left")
        self.str_bar = ctk.CTkProgressBar(meter, width=260, height=10,
                                          progress_color=ACCENT_COLOR)
        self.str_bar.pack(side="left", padx=10)
        self.pass_var.trace_add("write", lambda *_: self._update_strength())

        # action buttons
        row = ctk.CTkFrame(self, fg_color="transparent"); row.pack(pady=12)

        ctk.CTkButton(row, image=del_ic, text="Delete", width=120,
                      fg_color="#ef4444", hover_color="#c53030",
                      command=self._delete).pack(side="left", padx=6)

        self.save_btn = ctk.CTkButton(row, text="Update", width=160,
                                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                                      command=self._save)
        self.save_btn.pack(side="left", padx=6)

    # strength bar logic
    def _strength_score(self, pw: str):
        if not pw:
            return 0, ""
        classes = sum(bool(re.search(r, pw)) for r in
                      (r"[a-z]", r"[A-Z]", r"\d", r"[^\w\s]"))
        score  = min(1.0, (classes * 0.2 + len(pw) / 40))
        label  = ("Weak", "Fair", "Good", "Strong", "Very strong")[int(score*4)]
        return score, label

    def _update_strength(self):
        s, lbl = self._strength_score(self.pass_var.get())
        self.str_bar.set(s)
        colour = "red" if s < .3 else "orange" if s < .5 else "#f0ad4e" if s < .7 else ACCENT_COLOR
        self.str_label.configure(text=lbl, text_color=colour)

    # callbacks
    def _set_generated_pw(self, pw:str):
        self.pass_var.set(pw); self._update_strength()

    def _save(self):
        enc_pw = encrypt_password(self.pass_var.get(), self.master_key)
        if isinstance(enc_pw, (bytes, bytearray)):
            enc_pw = base64.b64encode(enc_pw).decode()

        DatabaseManager().update_credential(
            cred_id      = self.cred["id"],
            title        = self.title_var.get().strip(),
            username     = self.user_var.get().strip(),
            encrypted_pw = enc_pw,
            notes        = self.notes_var.get()
        )
        toast(self, "Updated!")
        self.destroy(); self._on_saved()

    def _delete(self):
        result = CTkMessagebox(
                    title="Delete?",
                    message="Really delete this entry?",
                    icon="warning",
                    option_1="Cancel",
                    option_2="Delete").get()

        if result == "Delete":
            DatabaseManager().delete_credential(self.cred["id"])
            toast(self, "Deleted!")
            self.destroy()
            self._on_saved()