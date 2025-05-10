@echo off
chcp 65001 > nul

if not exist "node_modules" (
    echo 首次執行，正在安裝依賴項...
    call npm install
) else (
    echo 依賴項檢查完成...
)

echo 正在啟動 GestureCanvas...
call npm start

pause
