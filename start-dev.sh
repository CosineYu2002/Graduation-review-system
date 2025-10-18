#!/bin/bash

# 畢業審查系統 - 開發環境啟動腳本

echo "🎓 成功大學畢業審查系統"
echo "=========================="
echo ""

# 檢查是否在項目根目錄
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 錯誤：請在項目根目錄執行此腳本"
    exit 1
fi

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1/4]${NC} 檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  警告：未找到 python3${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 環境正常"

echo ""
echo -e "${BLUE}[2/4]${NC} 檢查 Node.js 環境..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  警告：未找到 node${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js 環境正常"

echo ""
echo -e "${BLUE}[3/4]${NC} 啟動後端服務器..."
echo "   URL: http://127.0.0.1:8000"
echo "   Docs: http://127.0.0.1:8000/docs"
cd backend
python3 run.py --reload &
BACKEND_PID=$!
cd ..

# 等待後端啟動
sleep 3

# 檢查後端是否正常運行
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo -e "${GREEN}✓${NC} 後端服務器啟動成功"
else
    echo -e "${YELLOW}⚠️  警告：後端服務器可能未正常啟動${NC}"
fi

echo ""
echo -e "${BLUE}[4/4]${NC} 啟動前端開發服務器..."
echo "   URL: http://localhost:9000"
cd frontend

# 檢查是否需要安裝依賴
if [ ! -d "node_modules" ]; then
    echo "   正在安裝依賴..."
    npm install
fi

quasar dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✓✓✓ 系統啟動完成！ ✓✓✓${NC}"
echo ""
echo "📝 使用說明："
echo "   - 前端應用: http://localhost:9000"
echo "   - 後端 API: http://127.0.0.1:8000"
echo "   - API 文檔: http://127.0.0.1:8000/docs"
echo ""
echo "⏹️  停止服務："
echo "   按 Ctrl+C 停止所有服務"
echo ""

# 捕獲中斷信號
trap "echo ''; echo '正在停止服務...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待子進程
wait
