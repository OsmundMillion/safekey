import customtkinter as ctk
from typing import Callable
from ..constants import SIDEBAR_BG, HOVER_BG, ACCENT_COLOR, FONT_M
from ..icons import load as icon

class Sidebar(ctk.CTkFrame):
    """
    A vertical navigation rail. Emits a callback with the selected key.
    """
    def __init__(self, master, on_select: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color=SIDEBAR_BG, width=200, corner_radius=0, **kwargs)
        self._on_select = on_select
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="  Menu", font=("Segoe UI", 22, "bold"),
                     text_color="white").pack(anchor="w", pady=(24, 12), padx=14)

        body = ctk.CTkFrame(self, fg_color=SIDEBAR_BG)
        body.pack(fill="both", expand=True)

        for key, text, file in [
            ("vault",  "Vault",              "vault.png"),
            ("add",    "Add New",            "add.png"),
            ("export", "Export",             "download.png"),
            ("gen",    "Password Generator", "key.png"),
            ("sep",    "",                   ""),                   
            ("logout", "Logout",             "lock.png"),
        ]:
            if key == "sep":
                ctk.CTkLabel(body, text="", height=1,
                             fg_color="#2e2e2e").pack(fill="x", pady=8)
                continue

            btn = ctk.CTkButton(
                body, text=text, image=icon(file), compound="left", anchor="w",
                width=190, height=38, fg_color=SIDEBAR_BG, hover_color=HOVER_BG,
                corner_radius=6, font=FONT_M,
                command=lambda k=key: self._select(k)
            )
            btn.pack(fill="x", pady=2)
            self._buttons[key] = btn

        self._select("vault", invoke=False)          

    # highlight programmatically
    def highlight(self, key: str): self._select(key, invoke=False)

    def _select(self, key: str, invoke=True):
        for k, btn in self._buttons.items():
            btn.configure(fg_color=ACCENT_COLOR if k == key else SIDEBAR_BG)
        if invoke and self._on_select:
            self._on_select(key)
