import json
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from rule_engine.factory import StudentFactory, RuleFactory
from rule_engine.evaluator import Evaluator
from rule_engine.models.result import Result
from rule_engine.models.student import Student
from rule_engine.models.course import StudentCourse
from rule_engine.models.rule import Rule, RuleSet, RuleAll

from gui.state import AppStatus
from gui.dialog.major_dialog import MajorDialog
from gui.dialog.student_dialog import StudentDetailDialog, StudentEditDialog
from gui.dialog.minor_rule_dialog import MinorRuleDialog


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("畢業審核系統")
        self.root.geometry("1000x600")
        self.menu_del: tk.Menu | None = None
        self.menu_manage: tk.Menu | None = None

        self.state = AppStatus(students={})
        self.evaluator = Evaluator()
        self.status_var = tk.StringVar(value="就緒")
        self.count_var = tk.StringVar(value="學生數量: 0")

        self._setup_style()
        self._build_ui()
        self._bind_events()

        self._auto_load_students()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Microsoft JhengHei UI", 16, "bold"))
        style.configure("Bold.TLabel", font=("Microsoft JhengHei UI", 11, "bold"))

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        ttk.Label(container, text="畢業審核系統", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        self.nb = ttk.Notebook(container)
        self.nb.grid(row=1, column=0, sticky="nsew")
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        # Tab 1: 學生列表
        self._tab_students = ttk.Frame(self.nb, padding=6)
        self.nb.add(self._tab_students, text="學生列表")
        self._build_tab_students(self._tab_students)

        # 狀態列
        status = ttk.Frame(container)
        status.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        status.columnconfigure(1, weight=1)
        ttk.Label(status, text="狀態：").grid(row=0, column=0, padx=(0, 6))
        ttk.Label(status, textvariable=self.status_var).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(status, textvariable=self.count_var).grid(
            row=0, column=2, padx=(16, 0)
        )

    def _build_tab_students(self, tab: ttk.Frame):
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        # 左側操作
        ops = ttk.LabelFrame(tab, text="操作", padding=10)
        ops.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        ops.columnconfigure(0, weight=1)

        # 新增學生
        self.btn_add = ttk.Menubutton(ops, text="新增學生", width=18)
        menu_add = tk.Menu(self.btn_add, tearoff=False)
        menu_add.add_command(
            label="從 Excel 批量匯入", command=self.on_import_from_excel
        )
        menu_add.add_command(
            label="手動匯入（未完成）", command=self.on_add_manual_placeholder
        )
        self.btn_add["menu"] = menu_add
        self.btn_add.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        # 查改學生
        self.btn_manage = ttk.Menubutton(
            ops, text="查改學生", width=18, state="disabled"
        )
        self.menu_manage = tk.Menu(self.btn_manage, tearoff=False)
        self.menu_manage.add_command(label="查看學生資料", command=self.on_view_student)
        self.menu_manage.add_command(label="修改學生資料", command=self.on_edit_student)
        self.btn_manage["menu"] = self.menu_manage
        self.btn_manage.grid(row=1, column=0, pady=(0, 6))

        # 刪除學生
        self.btn_delete = ttk.Menubutton(ops, text="刪除學生", width=18)
        self.menu_del = tk.Menu(self.btn_delete, tearoff=False)
        self.menu_del.add_command(label="刪除所選學生", command=self.on_delete_selected)
        self.menu_del.add_command(label="刪除所有學生", command=self.on_delete_all)
        self.btn_delete["menu"] = self.menu_del
        self.btn_delete.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        # 開始審查
        self.btn_eval = ttk.Button(
            ops, text="開始審查", command=self.on_start_evaluation, state="disabled"
        )
        self.btn_eval.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        # 右側列表
        right = ttk.Frame(tab)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        cols = ("id", "name", "major")
        self.tree = ttk.Treeview(
            right, columns=cols, show="headings", selectmode="browse"
        )
        self.tree.heading("id", text="學號")
        self.tree.heading("name", text="姓名")
        self.tree.heading("major", text="科系")
        self.tree.column("id", width=150, anchor="w")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("major", width=80, anchor="center")

        vsb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

    # ------------ Data loading -------------
    def _auto_load_students(self):
        try:
            self.state.students_dir.mkdir(parents=True, exist_ok=True)
            files = list(self.state.students_dir.glob("*.json"))
            if not files:
                self._set_status("未找到學生資料")
                self._refresh_tree()
                return

            self.state.students.clear()
            for jf in files:
                student = StudentFactory.from_json_file(jf)
                self.state.students[student.id] = student

            self._set_status(f"已載入 {len(self.state.students)} 位學生")
            self._refresh_tree()
        except Exception as e:
            self._set_status(f"載入學生資料失敗")
            messagebox.showerror("錯誤", f"載入學生資料失敗：{e}")

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for stu in self.state.students.values():
            self.tree.insert(
                "", "end", iid=stu.id, values=(stu.id, stu.name, stu.major)
            )
        self.count_var.set(f"學生數量: {len(self.state.students)}")
        self._update_action_buttons()

    def _update_action_buttons(self):
        has_sel = bool(self.state.selected_id)
        self.btn_eval.configure(state=("normal" if has_sel else "disabled"))
        self.btn_delete.configure(state="normal")
        self.btn_manage.configure(state=("normal" if has_sel else "disabled"))
        self._update_delete_menu(has_sel)

    def _update_delete_menu(self, has_sel: bool):
        if not self.menu_del:
            return
        self.menu_del.entryconfigure(0, state=("normal" if has_sel else "disabled"))
        has_any = bool(self.state.students)
        self.menu_del.entryconfigure(1, state=("normal" if has_any else "disabled"))

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    # ------------ Actions -------------
    def on_import_from_excel(self):
        path = filedialog.askopenfilename(
            title="選擇 Excel 檔案",
            filetypes=[("Excel", "*.xlsx *.xls"), ("所有檔案", "*.*")],
        )
        if not path:
            return

        major = MajorDialog(self.root).result
        if not major:
            return

        try:
            self._set_status("正在從 Excel 匯入學生...")
            self.state.students_dir.mkdir(parents=True, exist_ok=True)
            loaded = StudentFactory.load_students_from_excel(
                Path(path), self.state.students_dir, major
            )
            self.state.students.update(loaded)
            self._refresh_tree()
            self._set_status(f"匯入完成，共 {len(loaded)} 位")
            messagebox.showinfo("成功", f"成功從 Excel 匯入 {len(loaded)} 位學生")
        except Exception as e:
            self._set_status("匯入失敗")
            messagebox.showerror("錯誤", f"匯入失敗：{e}")

    def on_add_manual_placeholder(self):
        messagebox.showinfo("提示", "手動新增暫未實作")

    def on_delete_selected(self):
        sel = self.state.selected_id
        if not sel:
            messagebox.showwarning("提示", "請先選擇要刪除的學生")
            return
        stu = self.state.students.get(sel)
        if not stu:
            return
        if not messagebox.askyesno("確認", f"確定刪除學生 {stu.name}（{stu.id}）？"):
            return
        try:
            (self.state.students_dir / f"{stu.id}.json").unlink(missing_ok=True)
            self.state.students.pop(stu.id, None)
            self.state.selected_id = None
            self._refresh_tree()
            self._set_status("已刪除選中學生")
        except Exception as e:
            messagebox.showerror("錯誤", f"刪除失敗：{e}")

    def on_view_student(self):
        stu = self._get_selected_student()
        if not stu:
            return
        StudentDetailDialog(self.root, stu)

    def on_edit_student(self):
        stu = self._get_selected_student()
        if not stu:
            return
        dlg = StudentEditDialog(self.root, stu)
        data = dlg.result
        if not data:
            return
        new_id = data["id"]  # 與原值相同（不可改）
        if new_id != stu.id and new_id in self.state.students:
            messagebox.showwarning("警告", f"學號 {new_id} 已存在，請使用其他學號")
            return
        try:
            # 學號不可改，這段僅防護（兩者不同時直接放棄）
            if new_id != stu.id:
                messagebox.showwarning("提示", "學號不可修改，已忽略變更")
            # 更新允許的欄位：科系、課程
            stu.major = data["major"]
            if "courses" in data:
                try:
                    stu.courses = [StudentCourse(**c) for c in data["courses"]]
                except Exception as e:
                    messagebox.showerror("錯誤", f"課程資料格式錯誤：{e}")
                    return

            # 寫回檔案（入學年度為 computed_field，不寫）
            (self.state.students_dir / f"{stu.id}.json").write_text(
                json.dumps(stu.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.state.students[stu.id] = stu
            self._refresh_tree()
            if stu.id in self.tree.get_children():
                self.tree.selection_set(stu.id)
                self.tree.see(stu.id)
            self._set_status("已更新學生資料與課程")
        except Exception as e:
            messagebox.showerror("錯誤", f"更新學生資料失敗：{e}")

    def _get_selected_student(self) -> Student | None:
        sid = self.state.selected_id
        return self.state.students.get(sid) if sid else None

    def on_delete_all(self):
        if not self.state.students:
            messagebox.showinfo("提示", "目前沒有學生資料")
            return
        if not messagebox.askyesno("確認", "確定刪除全部學生？ 此動作不可恢復！！"):
            return
        try:
            for jf in self.state.students_dir.glob("*.json"):
                jf.unlink(missing_ok=True)
            self.state.students.clear()
            self.state.selected_id = None
            self._refresh_tree()
            self._set_status("已刪除全部學生")
        except Exception as e:
            messagebox.showerror("錯誤", f"刪除失敗：{e}")

    def on_start_evaluation(self):
        sid = self.state.selected_id
        if not sid:
            return
        stu = self.state.students.get(sid)
        if not stu:
            return
        if not getattr(stu, "courses", None):
            messagebox.showwarning("提示", "此學生暫無課程資料，無法進行審查")
            return
        rule = self._auto_select_rule(stu)
        if not rule:
            return
        if stu.major == "AN":
            sel = MinorRuleDialog(self.root, self.state.rules_dir).result
            if not sel:
                return
            minor_rule, dept_codes = sel
            assert isinstance(rule, RuleSet), "AN 主規則需為 RuleSet"
            rule.sub_rules[0] = minor_rule
            for sub in rule.sub_rules[1:]:
                if isinstance(sub, RuleAll):
                    sub.course_criteria.department_codes = dept_codes

        try:
            self._set_status("正在進行審查...")
            result: Result = self.evaluator.evaluate(rule, stu.courses)
            self._set_status("審查完成")
            self._show_result_dialog(stu, rule, result)
        except Exception as e:
            self._set_status("審查失敗")
            messagebox.showerror("錯誤", f"評估失敗：{e}")

    # ------------- Helpers ---------------
    def _on_tree_select(self, _evt=None) -> None:
        sel = self.tree.selection()
        self.state.selected_id = sel[0] if sel else None
        self._update_action_buttons()

    def _on_tree_double_click(self, _evt=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        stu = self.state.students.get(sel[0])
        if not stu:
            return
        StudentDetailDialog(self.root, stu)

    def _auto_select_rule(self, student: Student) -> Rule | None:
        d = self.state.rules_dir
        if not d.exists():
            messagebox.showerror("錯誤", f"規則目錄不存在：{d}")
            return None
        dept_dir = d / student.major
        if not dept_dir.exists():
            messagebox.showerror("錯誤", f"找不到主修 '{student.major}' 的規則資料夾")
            return None
        candidates: list[tuple[int, Path]] = []
        for jf in dept_dir.glob("*.json"):
            if jf.stem.isdigit():
                y = int(jf.stem)
                if y <= student.admission_year:
                    candidates.append((y, jf))
        if not candidates:
            messagebox.showerror(
                "錯誤", f"找不到適用於 {student.admission_year} 的規則"
            )
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        _, path = candidates[0]
        try:
            rule = RuleFactory.from_json_file(path)
            return rule
        except Exception as e:
            messagebox.showerror("錯誤", f"載入規則失敗：{e}")
            return None

    def _show_result_dialog(self, student: Student, rule: Rule, result: Result) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.title("審查結果")
        dlg.transient(self.root)

        txt = tk.Text(
            dlg, wrap="word", font=("Microsoft JhengHei UI", 10), width=80, height=24
        )
        vsb = tk.Scrollbar(dlg, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        txt.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)

        dlg.rowconfigure(0, weight=1)
        dlg.columnconfigure(0, weight=1)
        lines = [
            "畢業審查結果",
            "=" * 10,
            "",
            f"姓名：{student.name}",
            f"學號：{student.id}",
            f"主修：{student.major}",
            "",
            f"規則：{rule.name}",
            f"結果：{'✅ 通過' if result.is_valid else '❌ 不通過'}",
            f"獲得學分：{result.earned_credits}",
            "",
            f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state="disabled")

        ttk.Button(dlg, text="關閉", command=dlg.destroy).grid(
            row=1, column=0, sticky="e", padx=10, pady=(0, 10)
        )
