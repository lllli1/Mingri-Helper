import pyautogui
import time
import sys

def main():
    """
    主函数：每隔10秒点击鼠标左键，每点击三次左键后按下s键0.8秒
    """
    print("鼠标键盘自动控制脚本启动")
    print("快捷键：按 Ctrl+C 退出程序")
    print("正在开始执行循环操作...")
    
    # 计数器，用于记录鼠标点击次数
    click_count = 0
    
    try:
        while True:
            # 点击鼠标左键
            pyautogui.click()
            click_count += 1
            print(f"点击鼠标左键 - 第 {click_count} 次点击")
            
            # 检查是否需要按下s键
            if click_count % 3 == 0:
                print("已点击三次，开始按下s键...")
                pyautogui.keyDown('s')  # 按下s键
                time.sleep(1.8)         # 保持0.8秒
                pyautogui.keyUp('s')    # 松开s键
                print("s键已释放")
                print("-" * 30)  # 分隔线，表示一个循环结束
            
            # 等待10秒（如果是第三次点击，已经包含了0.8秒的s键按下时间）
            if click_count % 3 == 0:
                # 第三次点击后，已经等待了0.8秒，所以只需要再等待9.2秒
                wait_time = 3
            else:
                wait_time = 3
            
            print(f"等待 {wait_time:.1f} 秒...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出错: {e}")
    finally:
        print("程序结束")

def check_dependencies():
    """
    检查必要的库是否已安装
    """
    try:
        import pyautogui
        print("pyautogui 库已安装")
        return True
    except ImportError:
        print("需要安装 pyautogui 库")
        print("请运行: pip install pyautogui")
        return False

if __name__ == "__main__":
    # 显示使用说明
    print("=" * 50)
    print("鼠标键盘自动控制脚本")
    print("功能:")
    print("  1. 每隔10秒点击鼠标左键")
    print("  2. 每点击3次左键后，按下s键0.8秒")
    print("  3. 上述操作为一个循环，持续重复")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 安全提示
    print("\n警告：脚本启动后，鼠标和键盘将被控制。")
    print("请确保:")
    print("  1. 光标在安全位置")
    print("  2. 当前窗口可以接收点击和键盘输入")
    print("  3. 准备好随时按 Ctrl+C 终止程序")
    
    # 倒计时开始
    for i in range(5, 0, -1):
        print(f"脚本将在 {i} 秒后开始...")
        time.sleep(1)
    
    print("\n开始执行!")
    main()