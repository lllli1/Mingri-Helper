import time
import threading
import keyboard
import pyautogui
import sys

class AutoAction:
    def __init__(self):
        self.running = False  # 主循环运行状态
        self.program_running = True  # 程序运行状态
        
    def action_sequence(self):
        """执行一个完整的动作循环"""
        print("[循环开始] 执行完整动作序列")
        
        # 按下x键
        print("[动作] 按下X键")
        pyautogui.press('x')
        
        # 延迟0.5秒
        time.sleep(0.5)
        
        # 按下鼠标左键
        print("[动作] 按下鼠标左键")
        pyautogui.click()
        
        # 睡眠10秒
        print("[等待] 10秒")
        time.sleep(10)
        
        # 长按F键5秒
        print("[动作] 长按F键5秒")
        pyautogui.keyDown('f')
        time.sleep(5)
        pyautogui.keyUp('f')
        
        # 等待3秒
        print("[等待] 3秒")
        time.sleep(3)
        
        print("[循环结束] 准备下一次循环")
    
    def main_loop(self):
        """主循环 - 无限循环执行动作序列"""
        print("[开始] 主循环已启动")
        
        while self.running and self.program_running:
            self.action_sequence()
        
        print("[停止] 主循环已停止")
    
    def start_loop(self):
        """启动主循环"""
        if not self.running:
            self.running = True
            # 在新线程中启动主循环
            loop_thread = threading.Thread(target=self.main_loop, daemon=True)
            loop_thread.start()
            print("[通知] 主循环已启动")
    
    def stop_loop(self):
        """停止主循环"""
        if self.running:
            self.running = False
            print("[通知] 主循环已停止")
    
    def stop(self):
        """停止程序"""
        print("\n[通知] 正在停止程序...")
        self.stop_loop()
        self.program_running = False
        time.sleep(1)  # 给线程一点时间清理
        print("[通知] 程序已停止")
        sys.exit(0)
    
    def start(self):
        """启动程序"""
        print("=" * 50)
        print("自动动作脚本 - 循环版本")
        print("=" * 50)
        print("功能说明:")
        print("  1. 按 J 键启动无限循环")
        print("  2. 每次循环包含:")
        print("     - 按下X键")
        print("     - 延迟0.5秒")
        print("     - 点击鼠标左键")
        print("     - 等待10秒")
        print("     - 长按F键5秒")
        print("     - 等待3秒")
        print("  3. 按 K 键停止循环")
        print("  4. 按 ESC 键退出程序")
        print("=" * 50)
        
        print("等待启动命令...")
        
        # 设置热键
        keyboard.add_hotkey('j', self.start_loop)
        keyboard.add_hotkey('k', self.stop_loop)
        keyboard.add_hotkey('esc', self.stop)
        
        # 保持程序运行
        try:
            while self.program_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

# 简化版本（如果你想要更简单的版本）
def simple_version():
    """简单版本，更容易理解"""
    import time
    import pyautogui
    import keyboard
    
    print("简单版本 - 按J键开始循环，按ESC退出")
    
    # 等待J键启动
    print("等待按J键开始...")
    keyboard.wait('j')
    
    print("循环已启动！按ESC键退出")
    
    try:
        while True:
            # 按下x键
            print("按下X键")
            pyautogui.press('x')
            
            # 延迟0.5秒
            time.sleep(0.5)
            
            # 按下鼠标左键
            print("点击鼠标左键")
            pyautogui.click()
            
            # 睡眠10秒
            print("等待10秒")
            time.sleep(10)
            
            # 长按F键5秒
            print("长按F键5秒")
            pyautogui.keyDown('f')
            time.sleep(5)
            pyautogui.keyUp('f')
            
            # 等待3秒
            print("等待3秒")
            time.sleep(3)
            
            print("完成一次循环，开始下一次...")
            
            # 检查是否按下了ESC键
            if keyboard.is_pressed('esc'):
                print("检测到ESC键，退出循环")
                break
                
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("程序结束")

if __name__ == "__main__":
    # 使用完整版本
    try:
        auto_action = AutoAction()
        auto_action.start()
    except Exception as e:
        print(f"程序错误: {e}")
        sys.exit(1)
    
    # 如果要使用简单版本，注释上面的代码，取消下面的注释：
    # simple_version()