import sys
import argparse
from cli import GraduationSystemCLI


def main():
    parser = argparse.ArgumentParser(description="畢業審查系統")
    parser.add_argument("--gui", action="store_true", help="啟動圖形界面")
    args = parser.parse_args()

    if args.gui:
        try:
            from gui.app import run_gui

            run_gui()
        except Exception as e:
            print(f"❌ GUI 啟動失敗：{e}")
            sys.exit(1)
        return

    cli = GraduationSystemCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 系統已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 系統錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
