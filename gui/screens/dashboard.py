import customtkinter as ctk
import csv, datetime, pyperclip
from tkinter import filedialog as fd
from CTkMessagebox import CTkMessagebox
from database.db_manager          import DatabaseManager
from encryption.crypto            import decrypt_password
from ..constants                  import ACCENT_COLOR
from ..constants                  import APP_ICON
from ..widgets.sidebar            import Sidebar
from ..widgets.cred_row           import CredentialRow
from ..widgets.toast              import toast
from ..widgets.password_generator import PasswordGeneratorWindow
from ..widgets.add_credential     import AddCredentialWindow
from ..widgets.edit_credential    import EditCredentialWindow
from ..screens.login_screen       import LoginScreen          

class DashboardScreen(ctk.CTk):
    def __init__(self, master_key: bytes):
        super().__init__()
        self.master_key = master_key

        # Window and Theme Setup
        self.title("SafeKey – Vault")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        self.configure(bg="#121212")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.iconbitmap(str(APP_ICON))

        # Sidebar Setup
        self.sidebar = Sidebar(self, on_select=self._route)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")

        # Header
        header = ctk.CTkFrame(self, fg_color="#1f1f1f", height=60)
        header.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="My Vault",
                     font=("Segoe UI", 20, "bold"),
                     text_color=ACCENT_COLOR).grid(row=0, column=0,
                                                   padx=20, pady=10, sticky="w")

        self.search = ctk.CTkEntry(header, placeholder_text="Search…", width=200)
        self.search.grid(row=0, column=1, padx=20)
        self.search.bind("<KeyRelease>", self._filter)

        # Scroll Content
        self.content = ctk.CTkScrollableFrame(self, fg_color="#1a1a1a")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="#1f1f1f", height=40)
        footer.grid(row=2, column=1, sticky="ew", padx=10, pady=(0, 10))
        ctk.CTkLabel(footer, text="© 2025 SafeKey | Osmund Million",
                     text_color="#666").pack(pady=5)

        # Initial render
        self._refresh()

    # Sidebar Routing
    def _route(self, key: str):
        match key:
            case "vault":
                self.sidebar.highlight("vault")
            case "add":
                AddCredentialWindow(self,
                                    master_key=self.master_key,
                                    on_saved=self._refresh)
            case "gen":
                PasswordGeneratorWindow(self)
            case "export":
                self._export_visible()
            case "logout":
                self._logout()

    # Row Callbacks
    def _copy_pw(self, pw: str):
        pyperclip.copy(pw)
        toast(self, "Password copied!")

    def _open_edit(self, cred: dict):
        EditCredentialWindow(self, cred,
                             master_key=self.master_key,
                             on_saved=self._refresh)

    def _delete_cred(self, cred_id: int):
        if CTkMessagebox(title="Delete?",
                         message="Really delete this credential?",
                         icon="warning",
                         option_1="Cancel", option_2="Delete").get() == "Delete":
            DatabaseManager().delete_credential(cred_id)
            toast(self, "Deleted!")
            self._refresh()

    # Data Helpers
    def _load_credentials(self):
        db = DatabaseManager()
        self.creds = []
        for row in db.get_all_credentials():
            try:
                enc   = row["password"]
                blob  = enc.decode() if isinstance(enc, (bytes, bytearray)) else enc
                plain = decrypt_password(blob, self.master_key)
            except Exception:
                continue
            self.creds.append({
                "id":       row["id"],
                "title":    row["title"],
                "username": row["username"],
                "password": plain,
                "notes":    row["notes"],
            })

    # Export Helpers
    def _export_visible(self):
        query = self.search.get().lower()
        rows  = [c for c in self.creds if query in c["title"].lower()]

        if not rows:
            toast(self, "Nothing to export")
            return

        default = f"vault-{datetime.date.today()}.csv"
        path = fd.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default,
            title="Export visible credentials")
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Title", "Username", "Password", "Notes"])
            for r in rows:
                w.writerow([r["title"], r["username"], r["password"], r["notes"]])

        toast(self, "Exported ✓")

    def _render_credentials(self, items):
        for w in self.content.winfo_children():
            w.destroy()
        for cred in items:
            CredentialRow(
                self.content, cred,
                on_copy   = self._copy_pw,
                on_edit   = self._open_edit,
                on_delete = self._delete_cred
            ).pack(fill="x", pady=5, padx=5)

    def _filter(self, _):
        q = self.search.get().lower()
        self._render_credentials([c for c in self.creds if q in c["title"].lower()])

    # Utilities
    def _refresh(self):
        self._load_credentials()
        self._render_credentials(self.creds)

    def _logout(self):
        self.destroy()

        def _after_login(key: bytes):
            DashboardScreen(master_key=key).mainloop()

        LoginScreen(on_success=_after_login).mainloop()
