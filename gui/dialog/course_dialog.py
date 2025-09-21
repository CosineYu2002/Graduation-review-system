import tkinter as tk
from tkinter import ttk, messagebox


class CourseEditDialog:
    def __init__(self, parent: tk.Tk | tk.Toplevel, initial: dict | None = None):
        self.result: dict | None = None
        win = tk.Toplevel(parent)
        self._win = win
        win.title("課程編輯")
        win.transient(parent)
        win.resizable(False, False)

        init = initial or {}

        # 欄位
        self.var_name = tk.StringVar(value=str(init.get("course_name", "")))
        self.var_codes = tk.StringVar(
            value=(
                "、".join(init.get("course_codes", []))
                if isinstance(init.get("course_codes"), list)
                else str(init.get("course_codes", ""))
            )
        )
        self.var_credit = tk.StringVar(value=str(init.get("credit", "")))
        self.var_grade = tk.StringVar(value=str(init.get("grade", "")))
        self.var_type = tk.StringVar(value=str(init.get("course_type", "")))
        self.var_tag = tk.StringVar(
            value=(
                "、".join(init.get("tag", []))
                if isinstance(init.get("tag"), list)
                else str(init.get("tag", ""))
            )
        )
        _cat = init.get("category", None)
        if not _cat:
            _cat = " "
        self.var_category = tk.StringVar(value=str(_cat))
        self.var_year_taken = tk.StringVar(value=str(init.get("year_taken", "")))
        self.var_semester_taken = tk.StringVar(
            value=str(init.get("semester_taken", ""))
        )
        self.var_recognized = tk.BooleanVar(value=bool(init.get("recognized", False)))

        frm = ttk.Frame(win, padding=12)
        frm.grid(sticky="nsew")
        for r in range(10):
            frm.rowconfigure(r, weight=0)
        frm.columnconfigure(1, weight=1)

        def add_row(r: int, label: str, widget: tk.Widget):
            ttk.Label(frm, text=label + "：").grid(
                row=r, column=0, sticky="e", padx=(0, 6), pady=4
            )
            widget.grid(row=r, column=1, sticky="ew", pady=4)

        add_row(0, "課程名稱", ttk.Entry(frm, textvariable=self.var_name))
        add_row(
            1,
            "課程序號（多個以、或, 分隔）",
            ttk.Entry(frm, textvariable=self.var_codes),
        )
        add_row(2, "學分", ttk.Entry(frm, textvariable=self.var_credit))
        add_row(3, "成績", ttk.Entry(frm, textvariable=self.var_grade))
        add_row(4, "選必修", ttk.Entry(frm, textvariable=self.var_type))
        add_row(
            5, "標籤（多個以、或, 分隔）", ttk.Entry(frm, textvariable=self.var_tag)
        )
        add_row(6, "課程類別", ttk.Entry(frm, textvariable=self.var_category))
        add_row(7, "修課學年", ttk.Entry(frm, textvariable=self.var_year_taken))
        add_row(8, "修課學期", ttk.Entry(frm, textvariable=self.var_semester_taken))

        btns = ttk.Frame(frm)
        btns.grid(row=10, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(btns, text="取消", command=win.destroy).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(btns, text="確定", command=self._ok).grid(row=0, column=1)

        win.bind("<Return>", lambda _e: self._ok())
        win.bind("<Escape>", lambda _e: win.destroy())

        win.wait_window()

    def _split_to_list(self, s: str) -> list[str]:
        s = s.replace("，", ",").replace("、", ",")
        items = [x.strip() for x in s.split(",") if x.strip()]
        return items

    def _ok(self) -> None:
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("提示", "請輸入課程名稱", parent=self._win)
            return

        def to_int(x: str) -> int | None:
            x = x.strip()
            return int(x) if x else None

        def to_float(x: str) -> float | None:
            x = x.strip()
            return float(x) if x else None

        def to_grade(x: str) -> int | str | None:
            x = x.strip()
            if not x:
                return None
            try:
                return int(x)
            except ValueError:
                return x

        category_val = self.var_category.get().strip()
        if not category_val:
            category_val = " "
        self.result = {
            "course_name": name,
            "course_codes": self._split_to_list(self.var_codes.get()),
            "credit": to_float(self.var_credit.get()),
            "grade": to_grade(self.var_grade.get()),
            "course_type": to_int(self.var_type.get()),
            "tag": self._split_to_list(self.var_tag.get()),
            "category": category_val,
            "year_taken": to_int(self.var_year_taken.get()),
            "semester_taken": to_int(self.var_semester_taken.get()),
            "recognized": False,
        }
        self._win.destroy()
