@echo off
chcp 65001 >nul
echo ====================================================
echo   正在自动同步更新至 GitHub (changshiai456/shichang300)
echo ====================================================

git add -A
for /f "tokens=1-4 delims=/ " %%i in ("%date%") do set d=%%i-%%j-%%k
for /f "tokens=1-2 delims=: " %%i in ("%time%") do set t=%%i:%%j
git commit -m "update: 自动同步数据与分析大屏 (%date% %time%)"

echo.
echo 正在推送到 GitHub main 分支...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo [成功] 已成功推送至 GitHub 仓库！
    echo 仓库地址: https://github.com/changshiai456/shichang300
) else (
    echo.
    echo [提示] 推送遇到问题或无新改动，请检查网络或提交状态。
)

echo.
pause
