# -*- coding: utf-8 -*-
"""
=============================================================================
天猫账号首次登录助手 (基于 DrissionPage)
功能：
1. 启动带独立用户数据目录的 Chromium 浏览器；
2. 引导您扫码或账号登录天猫；
3. 登录成功后自动将 Cookie、Token、会话状态永久保存至本地 tmall_chrome_profile/；
4. 之后运行批量爬虫无需再次登录，永久复用登录态！
=============================================================================
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import time
from DrissionPage import ChromiumPage, ChromiumOptions

BASE_DIR = os.path.abspath(".")
PROFILE_DIR = os.path.join(BASE_DIR, "tmall_chrome_profile")
os.makedirs(PROFILE_DIR, exist_ok=True)

def main():
    print("=" * 60)
    print("🚀 启动天猫登录助手 (DrissionPage 永久免密会话)")
    print(f"📁 Cookie 与浏览器数据存储路径:\n   {PROFILE_DIR}")
    print("=" * 60)

    # 配置独立的浏览器用户数据目录
    co = ChromiumOptions()
    co.set_user_data_path(PROFILE_DIR)
    co.headless(False)
    co.set_argument('--no-first-run')
    co.set_argument('--no-default-browser-check')

    print("\n正在启动 Chrome 浏览器，请稍候...")
    page = ChromiumPage(co)

    # 打开天猫登录页
    login_url = "https://login.tmall.com/"
    print(f"正在打开登录页: {login_url}")
    page.get(login_url)

    print("\n" + "#" * 60)
    print("👉 请在弹出的浏览器窗口中完成【扫码登录】或【手机短信登录】！")
    print("👉 登录成功后，脚本会自动检测并保存 Cookie！")
    print("#" * 60 + "\n")

    # 循环检测是否已登录
    max_wait = 180  # 最长等待 3 分钟
    start_time = time.time()
    logged_in = False

    while time.time() - start_time < max_wait:
        cur_url = page.url
        if "login" not in cur_url or page.ele("text:我的淘宝") or page.ele("text:购物车") or page.ele("text:退出"):
            logged_in = True
            break
        time.sleep(1.5)

    if logged_in:
        print("\n" + "=" * 60)
        print("🎉 恭喜！检测到已成功登录天猫账号！")
        print("✅ 登录凭据与全部 Cookie 已自动持久化保存至本地 tmall_chrome_profile 目录！")
        print("✅ 下次执行批量采集脚本时将【完全自动免登录】！")
        print("=" * 60 + "\n")
        time.sleep(3)
    else:
        print("\n⚠️ 等待超时，如果已登录成功，配置也已写入本地目录。")

    page.quit()
    print("浏览器已安全关闭。")

if __name__ == "__main__":
    main()
