import sys
import tkinter as tk
from tkinter import messagebox

from .main_window import MainWindow


def run_gui() -> None:
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        run_gui()
    except Exception as e:
        messagebox.showerror("系統錯誤", f"GUI 啟動失敗：{e}")
        sys.exit(1)
