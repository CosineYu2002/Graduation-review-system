import uvicorn
import argparse


def main():
    """
    API 伺服器啟動腳本
    """
    parser = argparse.ArgumentParser(description="畢業審查系統 API 伺服器")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="伺服器監聽的主機地址"
    )
    parser.add_argument("--port", type=int, default=8000, help="伺服器監聽的端口")
    parser.add_argument("--reload", action="store_true", help="啟用熱重載模式 (開發用)")
    args = parser.parse_args()

    print(f"啟動 API 伺服器於 http://{args.host}:{args.port}")
    if args.reload:
        print("熱重載已啟用。")

    # 使用字串路徑 "module.path:app_variable" 來啟動
    # 這樣可以確保 uvicorn 的熱重載功能正常運作
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
