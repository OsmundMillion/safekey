import customtkinter as ctk

def toast(root, msg="Copied!", ms=1500):
    top = ctk.CTkToplevel(root)
    top.overrideredirect(True); top.attributes("-topmost", True)
    top.configure(fg_color="#222423")
    w,h = 200,40; root.update_idletasks()
    x = root.winfo_x()+(root.winfo_width()//2)-(w//2)
    y = root.winfo_y()+root.winfo_height()-h-40
    top.geometry(f"{w}x{h}+{x}+{y}")
    ctk.CTkLabel(top, text=msg, font=("Segoe UI", 12), text_color="white").pack(expand=True)
    top.after(ms, top.destroy)
