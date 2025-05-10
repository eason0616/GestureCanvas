@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo 選擇啟動模式:
echo [1] 正常模式
echo [2] Debug模式
choice /c 12 /n /m "請選擇 (1-2): "

if errorlevel 2 (
    if not exist "node_modules" (
        echo 首次執行，正在安裝依賴項...
        call npm install
    ) else (
        echo 依賴項檢查完成...
    )
    
    echo 正在以Debug模式啟動 GestureCanvas...
    set DEBUG=electron:*
    set ELECTRON_ENABLE_LOGGING=true
    call npm run debug
) else (
    if not exist "node_modules" (
        echo 首次執行，正在安裝依賴項...
        call npm install
    ) else (
        echo 依賴項檢查完成...
    )
    
    echo 正在啟動 GestureCanvas...
    call npm start
)

pause
