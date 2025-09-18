import sys
from cli import GraduationSystemCLI


def main():
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
