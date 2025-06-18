import customtkinter as ctk, pyperclip
from typing import Callable
from ..icons      import load as icon
from ..constants  import ACCENT_COLOR

class CredentialRow(ctk.CTkFrame):
    """
    One credential row.
    Emits callbacks (if supplied):
        on_copy(password)
        on_edit(cred_dict)
        on_delete(cred_id)
    """
    def __init__(self,
                 master,
                 data: dict,
                 on_copy:   Callable[[str], None],
                 on_edit:   Callable[[dict], None] | None = None,
                 on_delete: Callable[[int], None]  | None = None,
                 **kw):
        super().__init__(master, fg_color="#222", corner_radius=8, **kw)

        # fresh icons valid for the *current* Tk root
        self.ic_copy   = icon("copy.png",   (20, 20))
        self.ic_eye    = icon("eye.png",    (20, 20))
        self.ic_eye_off= icon("eye_off.png",(20, 20))
        self.ic_edit   = icon("edit.png",   (20, 20))
        self.ic_delete = icon("delete.png", (20, 20))

        self.data       = data
        self._pw        = data["password"]
        self._on_copy   = on_copy
        self._on_edit   = on_edit
        self._on_delete = on_delete
        self._build()

    # UI
    def _build(self):
        ctk.CTkLabel(self, text=self.data["title"],
                     width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(self, text=self.data["username"],
                     width=200, anchor="w").pack(side="left")

        self._pw_var = ctk.StringVar(value="●●●●●●●")
        ctk.CTkLabel(self, textvariable=self._pw_var,
                     width=100, anchor="w").pack(side="left")

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(side="right")

        # delete
        if self._on_delete:
            ctk.CTkButton(btns, image=self.ic_delete, text="",
                          width=36, height=32,
                          fg_color="#ef4444", hover_color="#c53030",
                          command=lambda: self._on_delete(self.data["id"])) \
                .pack(side="right", padx=4)

        # edit
        if self._on_edit:
            ctk.CTkButton(btns, image=self.ic_edit, text="",
                          width=36, height=32,
                          fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                          command=lambda: self._on_edit(self.data)) \
                .pack(side="right", padx=4)

        # copy
        ctk.CTkButton(btns, image=self.ic_copy, text="",
                      width=36, height=32,
                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                      command=self._handle_copy) \
            .pack(side="right", padx=4)

        # eye
        self._eye_btn = ctk.CTkButton(btns, image=self.ic_eye, text="",
                                      width=36, height=32,
                                      fg_color=ACCENT_COLOR, hover_color="#0e9f8d",
                                      command=self._toggle_pw)
        self._eye_btn.pack(side="right", padx=4)

    # Helper Methods
    def _toggle_pw(self):
        hidden = self._pw_var.get() == "●●●●●●●"
        self._pw_var.set(self._pw if hidden else "●●●●●●●")
        self._eye_btn.configure(
            image=self.ic_eye_off if hidden else self.ic_eye
        )

    def _handle_copy(self):
        pyperclip.copy(self._pw)
        if self._on_copy:
            self._on_copy(self._pw)
