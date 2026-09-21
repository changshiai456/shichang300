@echo off
chcp 65001 >nul
title 天猫95款核心床垫 1.8m SKU 平台加补价全自动极速采集助手
color 0b

:MENU
cls
echo =======================================================================
echo          天猫 95 款床垫 1.8米全量 SKU 平台加补到手价极速采集器
echo                      (基于 DrissionPage 自动化引擎)
echo =======================================================================
echo.
echo   [1] 首次登录天猫 (仅需扫码一次，Cookie 永久保存在本地，后续免登录)
echo   [2] 启动全自动极速采集 95 款床垫 1.8m SKU 到手价 (毫秒级瞬时提取)
echo   [3] 一键完整运行 (首次登录 + 自动接续采集)
echo   [0] 退出
echo.
echo =======================================================================
set /p opt=请输入选项 [1/2/3/0]: 

if "%opt%"=="1" goto LOGIN
if "%opt%"=="2" goto CRAWL
if "%opt%"=="3" goto ALL
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

:CRAWL
echo.
echo 正在加载本地保存的登录态，开始全自动巡航采集 95 款床垫 1.8m SKU 到手价...
python crawl_tmall_18m_skus_drission.py
echo.
echo 采集完毕！按任意键返回主菜单...
pause >nul
goto MENU

:ALL
echo.
echo 步骤 1: 正在检测或引导登录天猫...
python login_tmall_drission.py
echo.
echo 步骤 2: 正在启动自动化极速采集...
python crawl_tmall_18m_skus_drission.py
echo.
echo 全部完成！按任意键返回主菜单...
pause >nul
goto MENU