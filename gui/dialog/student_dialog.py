import tkinter as tk
from tkinter import ttk, messagebox


from rule_engine.models.student import Student
from rule_engine.models.course import StudentCourse

from gui.utils import UtilityFunctions
from gui.dialog.course_dialog import CourseEditDialog


class StudentDetailDialog:
    def __init__(self, parent: tk.Tk | tk.Toplevel, stu: Student):
        win = tk.Toplevel(parent)
        win.title("學生詳情")
        win.transient(parent)
        win.resizable(True, True)

        top = ttk.Frame(win, padding=12)
        top.grid(row=0, column=0, sticky="nsew")
        win.rowconfigure(1, weight=1)
        win.columnconfigure(0, weight=1)

        rows = [
            ("學號", stu.id),
            ("姓名", stu.name),
            ("主修", stu.major),
            ("入學年度", str(stu.admission_year)),
            ("課程數量", str(len(getattr(stu, "courses", []) or []))),
        ]
        for i, (k, v) in enumerate(rows):
            ttk.Label(top, text=f"{k}：", style="Bold.TLabel").grid(
                row=i, column=0, sticky="e", padx=(0, 6), pady=3
            )
            ttk.Label(top, text=v).grid(row=i, column=1, sticky="w", pady=3)

        box = ttk.LabelFrame(win, text="課程列表", padding=8)
        box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        cols = ("course_name", "course_codes", "grade")
        tree = ttk.Treeview(box, columns=cols, show="headings")
        for cid, title in zip(cols, ("課程名稱", "課程序號", "成績")):
            tree.heading(cid, text=title)
        tree.column("course_name", width=120, anchor="w")
        tree.column("course_codes", width=80, anchor="center")
        tree.column("grade", width=80, anchor="center")
        vsb = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        UtilityFunctions._populate_course_tree(tree, getattr(stu, "courses", []) or [])
        ttk.Button(win, text="關閉", command=win.destroy).grid(
            row=2, column=0, sticky="e", padx=12, pady=(0, 12)
        )


class StudentEditDialog:
    def __init__(self, parent: tk.Tk | tk.Toplevel, stu: Student):
        self.result: dict | None = None
        win = tk.Toplevel(parent)
        self._win = win
        win.title("修改學生資料")
        win.transient(parent)
        win.resizable(True, True)

        frm = ttk.Frame(win, padding=12)
        frm.grid(row=0, column=0, sticky="ew")
        for c in range(3):
            frm.columnconfigure(c, weight=1)

        # 基本資料：學號、姓名、入學年度不可修改；科系可改
        self.var_id = tk.StringVar(value=stu.id)
        self.var_name = tk.StringVar(value=stu.name)
        self.var_major = tk.StringVar(value=stu.major)
        self.var_year = tk.StringVar(value=str(getattr(stu, "admission_year", "")))

        ttk.Label(frm, text="學號：", style="Bold.TLabel").grid(
            row=0, column=0, sticky="e", padx=(0, 6), pady=4
        )
        ttk.Entry(frm, textvariable=self.var_id, state="readonly").grid(
            row=0, column=1, columnspan=2, sticky="ew", pady=4
        )

        ttk.Label(frm, text="姓名：", style="Bold.TLabel").grid(
            row=1, column=0, sticky="e", padx=(0, 6), pady=4
        )
        ttk.Entry(frm, textvariable=self.var_name, state="readonly").grid(
            row=1, column=1, columnspan=2, sticky="ew", pady=4
        )

        ttk.Label(frm, text="科系：", style="Bold.TLabel").grid(
            row=2, column=0, sticky="e", padx=(0, 6), pady=4
        )
        ttk.Entry(frm, textvariable=self.var_major).grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=4
        )

        ttk.Label(frm, text="入學年度（自動計算）：", style="Bold.TLabel").grid(
            row=3, column=0, sticky="e", padx=(0, 6), pady=4
        )
        ttk.Entry(frm, textvariable=self.var_year, state="readonly").grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=4
        )

        # 修課清單（可新增/編輯/刪除）
        box = ttk.LabelFrame(win, text="修課清單", padding=8)
        box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        win.rowconfigure(1, weight=1)
        win.columnconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        box.rowconfigure(1, weight=1)

        # 工具列
        toolbar = ttk.Frame(box)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Button(toolbar, text="新增課程", command=self._on_add_course).pack(
            side="left"
        )
        ttk.Button(toolbar, text="編輯所選", command=self._on_edit_course).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(toolbar, text="刪除所選", command=self._on_delete_course).pack(
            side="left", padx=(6, 0)
        )

        cols = ("course_name", "course_codes", "grade")
        self.tree = ttk.Treeview(
            box, columns=cols, show="headings", selectmode="browse"
        )
        for cid, title in zip(cols, ("課程名稱", "課程序號", "成績")):
            self.tree.heading(cid, text=title)
        self.tree.column("course_name", width=240, anchor="w")
        self.tree.column("course_codes", width=180, anchor="center")
        self.tree.column("grade", width=80, anchor="center")
        vsb = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        # 以 StudentCourse 物件列表維護暫存課程
        self._courses: list[StudentCourse] = list(getattr(stu, "courses", []) or [])
        UtilityFunctions._populate_course_tree(self.tree, self._courses)

        btns = ttk.Frame(win)
        btns.grid(row=2, column=0, sticky="e", padx=12, pady=(0, 12))
        ttk.Button(btns, text="取消", command=self._win.destroy).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(btns, text="保存", command=self._ok).grid(row=0, column=1)

        # 雙擊快速編輯課程
        self.tree.bind("<Double-1>", lambda _e: self._on_edit_course())

        win.wait_window()

    def _on_add_course(self) -> None:
        dlg = CourseEditDialog(self._win)
        data = dlg.result
        if not data:
            return
        try:
            course = StudentCourse(**data)
            self._courses.append(course)
            UtilityFunctions._populate_course_tree(self.tree, self._courses)
        except Exception as e:
            messagebox.showerror("錯誤", f"新增課程失敗：{e}", parent=self._win)

    def _on_edit_course(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇要編輯的課程", parent=self._win)
            return
        idx = self.tree.index(sel[0])
        old = self._courses[idx]
        dlg = CourseEditDialog(self._win, initial=UtilityFunctions.course_to_dict(old))
        data = dlg.result
        if not data:
            return
        try:
            self._courses[idx] = StudentCourse(**data)
            UtilityFunctions._populate_course_tree(self.tree, self._courses)
        except Exception as e:
            messagebox.showerror("錯誤", f"編輯課程失敗：{e}", parent=self._win)

    def _on_delete_course(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "請先選擇要刪除的課程", parent=self._win)
            return
        idx = self.tree.index(sel[0])
        if not messagebox.askyesno("確認", "確定刪除所選課程？", parent=self._win):
            return
        self._courses.pop(idx)
        UtilityFunctions._populate_course_tree(self.tree, self._courses)

    def _ok(self) -> None:
        sid = self.var_id.get().strip()
        name = self.var_name.get().strip()
        major = self.var_major.get().strip().upper()
        if not sid or not name or not major:
            messagebox.showwarning("提示", "資料不完整", parent=self._win)
            return
        # 回傳：學號/姓名（雖不可改，仍回傳原值），科系（可改），課程（可改）
        self.result = {
            "id": sid,
            "name": name,
            "major": major,
            "courses": [
                (
                    c.model_dump()
                    if hasattr(c, "model_dump")
                    else UtilityFunctions.course_to_dict(c)
                )
                for c in self._courses
            ],
        }
        self._win.destroy()
