@echo off
chcp 65001 >nul
title 天猫最新30天市场TOP300床垫 1.8m SKU 平台到手价极速采集助手
color 0b

:MENU
cls
echo =======================================================================
echo     天猫最新 30 天市场 TOP 300 床垫 1.8米全量 SKU 到手价极速采集器
echo                      (基于 DrissionPage 自动化引擎)
echo =======================================================================
echo.
echo   [1] 登录/检测天猫账号 (仅需扫码一次，Cookie 永久保存在本地 tmall_chrome_profile/)
echo   [2] 启动全自动极速采集 300 款床垫 1.8m SKU 到手价 (支持自动断点续传)
echo   [3] 测试模式：仅采集前 5 款验证效果
echo   [4] 重新从生意参谋报表重新生成 300 款商品目录 (extract_sycm_300_catalog.py)
echo   [0] 退出
echo.
echo =======================================================================
set /p opt=请输入选项 [1/2/3/4/0]: 

if "%opt%"=="1" goto LOGIN
if "%opt%"=="2" goto CRAWL_ALL
if "%opt%"=="3" goto CRAWL_TEST
if "%opt%"=="4" goto CATALOG
if "%opt%"=="0" exit
goto MENU

:LOGIN
echo.
echo 正在启动浏览器并打开天猫登录页，请在弹出的窗口中扫码或短信登录...
python login_tmall_drission.py
echo.
echo 按任意键返回主菜单...
pause >nul
goto MENU

:CRAWL_ALL
echo.
echo 正在加载本地保存的登录态，开始全自动巡航采集 300 款床垫 1.8m SKU 到手价...
python crawl_market_300_18m_skus.py
echo.
echo 采集完毕！按任意键返回主菜单...
pause >nul
goto MENU

:CRAWL_TEST
echo.
echo 正在测试采集前 5 款商品...
python crawl_market_300_18m_skus.py --limit 5
echo.
echo 测试完毕！按任意键返回主菜单...
pause >nul
goto MENU

:CATALOG
echo.
echo 正在从 Sycm_Report_1790518002796.html 穿透提取 300 款商品 ID...
python extract_sycm_300_catalog.py
python build_autopilot_script.py
echo.
echo 商品目录更新完毕！按任意键返回主菜单...
pause >nul
goto MENU
