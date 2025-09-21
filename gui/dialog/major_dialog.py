import tkinter as tk
from tkinter import ttk, messagebox


class MajorDialog:
    def __init__(self, parent: tk.Tk | tk.Toplevel):
        self.result: str | None = None
        win = tk.Toplevel(parent)
        self._win = win
        win.title("輸入主修科系")
        win.transient(parent)
        win.grab_set()
        win.resizable(False, False)

        frm = ttk.Frame(win, padding=14)
        frm.grid(sticky="nsew")
        ttk.Label(frm, text="請輸入主修科系代號（例如 AN）", style="Bold.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.var = tk.StringVar()
        ent = ttk.Entry(frm, textvariable=self.var, width=20)
        ent.grid(row=1, column=0, sticky="ew", pady=(8, 12))
        ent.focus()
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, sticky="e")
        ttk.Button(btns, text="確定", command=self._ok).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(btns, text="取消", command=win.destroy).grid(row=0, column=1)
        win.bind("<Return>", lambda _e: self._ok())

        win.wait_window()

    def _ok(self) -> None:
        val = self.var.get().strip().upper()
        if not val:
            messagebox.showwarning("提示", "請輸入主修代號", parent=self._win)
            return
        self.result = val
        self._win.destroy()
