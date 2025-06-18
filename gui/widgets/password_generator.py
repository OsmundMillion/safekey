import customtkinter as ctk
import secrets, string, pyperclip
from ..icons import load as icon            
ACCENT = "#00c9a7"

# icons
refresh_ic = icon("refresh.png", (20, 20))
copy_ic    = icon("copy.png",    (20, 20))
use_ic     = icon("check.png",   (20, 20))

class PasswordGeneratorWindow(ctk.CTkToplevel):
    """Floating dialog that generates random passwords."""
    def __init__(self, master, on_select=None):
        super().__init__(master)
        self._on_select = on_select
        self.title("Password Generator")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a1a", padx=24, pady=24)

        # state
        self.len_var   = ctk.IntVar(value=20)
        self.upper_var = ctk.BooleanVar(value=True)
        self.digits_var= ctk.BooleanVar(value=True)
        self.sym_var   = ctk.BooleanVar(value=True)
        self.out_var   = ctk.StringVar()

        self._build_ui()
        self._generate()

    # User Interface
    def _build_ui(self):
        ctk.CTkLabel(self, text="Password Generator",
                     font=("Segoe UI", 20, "bold"),
                     text_color="white").pack(anchor="center", pady=(0, 16))

        ctk.CTkEntry(self, textvariable=self.out_var, width=440,
                     font=("Segoe UI", 18, "bold"),
                     fg_color="#262626", border_width=2,
                     border_color=ACCENT).pack(pady=4)

        # Button Row
        row = ctk.CTkFrame(self, fg_color="transparent"); row.pack(pady=8)

        ctk.CTkButton(row, image=refresh_ic, text="", width=36, height=32,
                      fg_color=ACCENT, hover_color="#0e9f8d",
                      command=self._generate).pack(side="left", padx=4)

        ctk.CTkButton(row, image=copy_ic, text="", width=36, height=32,
                      fg_color=ACCENT, hover_color="#0e9f8d",
                      command=self._copy).pack(side="left", padx=4)

        if self._on_select:
            ctk.CTkButton(row, image=use_ic, text="", width=60, height=32,
                          fg_color=ACCENT, hover_color="#0e9f8d",
                          command=lambda: (self._on_select(self.out_var.get()),
                                           self.destroy())
                          ).pack(side="left", padx=4)

        # Options Frame
        opts = ctk.CTkFrame(self, fg_color="transparent"); opts.pack(fill="x", pady=12)

        ctk.CTkLabel(opts, text="Length", anchor="w") \
            .grid(row=0, column=0, sticky="w", padx=(12, 0))
        ctk.CTkSlider(opts, from_=6, to=64, number_of_steps=58,
                      variable=self.len_var, command=lambda *_: self._generate(),
                      width=260, progress_color=ACCENT, button_color=ACCENT) \
            .grid(row=0, column=1, padx=10)
        ctk.CTkLabel(opts, textvariable=self.len_var, width=30) \
            .grid(row=0, column=2)

        def add_toggle(r, text, var):
            ctk.CTkLabel(opts, text=text, anchor="w") \
                .grid(row=r, column=0, sticky="w", padx=(12, 0), pady=6)
            ctk.CTkSwitch(opts, text="", variable=var, command=self._generate,
                          fg_color="#444", progress_color=ACCENT,
                          button_color="#e5e5e5",
                          button_hover_color="#cfcfcf").grid(row=r, column=1, sticky="e")

        add_toggle(1, "Use capital letters (A-Z)", self.upper_var)
        add_toggle(2, "Use digits (0-9)",           self.digits_var)
        add_toggle(3, "Use symbols (@!$%&*)",       self.sym_var)

    # Pool and Generation
    def _pool(self) -> str:
        pool = string.ascii_lowercase
        if self.upper_var.get():  pool += string.ascii_uppercase
        if self.digits_var.get(): pool += string.digits
        if self.sym_var.get():    pool += "@!$%&*#?"
        return pool

    def _generate(self, *_):
        pool, length = self._pool(), self.len_var.get()
        self.out_var.set("".join(secrets.choice(pool) for _ in range(length)) if pool else "")

    def _copy(self):
        pyperclip.copy(self.out_var.get())
