from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox

from rule_engine.factory import RuleFactory
from rule_engine.utils import UtilFunctions
from rule_engine.models.rule import Rule


class MinorRuleDialog:
    def __init__(self, parent: tk.Tk | tk.Toplevel, rules_dir: Path):
        self.result: tuple[Rule, list[str]] | None = None
        self.rules_dir = rules_dir

        win = tk.Toplevel(parent)
        self._win = win
        win.title("選擇輔系規則")
        win.transient(parent)
        win.grab_set()

        frm = ttk.Frame(win, padding=10)
        frm.grid(sticky="nsew")
        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)

        ttk.Label(frm, text="請選擇輔系規則：", style="Bold.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        cols = ("dept", "file")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=12)
        self.tree.heading("dept", text="科系")
        self.tree.heading("file", text="檔案")
        self.tree.column("dept", width=80, anchor="center")
        self.tree.column("file", width=260, anchor="w")
        vsb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        frm.rowconfigure(1, weight=1)
        frm.columnconfigure(0, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, sticky="e", pady=(8, 0))
        ttk.Button(btns, text="確定", command=self._ok).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(btns, text="取消", command=win.destroy).grid(row=0, column=1)

        self.tree.bind("<Double-1>", lambda _e: self._ok())
        self._load_rules()

        win.wait_window()

    def _load_rules(self) -> None:
        if not self.rules_dir.exists():
            return
        for dept in self.rules_dir.iterdir():
            if not dept.is_dir():
                continue
            for jf in dept.glob("*.json"):
                if "_" in jf.stem:
                    self.tree.insert("", "end", values=(dept.name, jf.name))

    def _ok(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "請選擇規則", parent=self._win)
            return
        dept, filename = self.tree.item(sel[0], "values")
        path = self.rules_dir / dept / filename
        try:
            rule = RuleFactory.from_json_file(path)
            dept_codes = UtilFunctions().get_department_code(dept)
            self.result = (rule, dept_codes)
            self._win.destroy()
        except Exception as e:
            messagebox.showerror("錯誤", f"載入規則失敗：{e}", parent=self._win)
