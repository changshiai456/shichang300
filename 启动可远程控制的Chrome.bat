@echo off
chcp 65001 >nul
echo ========================================================
echo   正在以自动化调试模式启动 Chrome 浏览器
echo ========================================================
echo.
echo 正在安全退出当前普通模式的 Chrome...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 1 >nul

echo 正在以调试端口 9222 启动 Chrome (保留所有账号登录态)...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

echo.
echo ========================================================
echo   Chrome 启动成功！已开启 9222 自动化远程控制端口
echo ========================================================
echo 1. 请在打开的 Chrome 窗口中正常进入您的生意参谋页面；
echo 2. 返回 AI 助手窗口，回复【已启动】；
echo 3. AI 助手将直接连接该浏览器，全自动帮您完成 41 页采集！
echo ========================================================
pause
