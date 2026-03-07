import pyautogui
import time

def main():
    print("S1阶段开始")
    time.sleep(3)  # 启动后等待3秒
    
    # 获取游戏窗口句柄
    import win32gui
    
    def get_game_window_rect():
        # 根据窗口标题查找游戏窗口，标题包含BooK思议即可
        # 使用EnumWindows枚举所有窗口并检查标题是否包含"BooK思议"
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "BooK思议" in title:
                    windows.append(hwnd)
            return True
            
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            hwnd = windows[0]  # 取第一个匹配的窗口
        else:
            hwnd = None
        
        if hwnd:
            # 检查窗口是否最小化
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, 9)  # 还原窗口
                time.sleep(0.5)
            
            # 获取窗口位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            return left, top, width, height
        else:
            return None
    
    # 尝试获取游戏窗口
    game_window_rect = get_game_window_rect()
    if game_window_rect:
        game_window_left, game_window_top, game_window_width, game_window_height = game_window_rect
        print(f"找到游戏窗口: ({game_window_left}, {game_window_top}, {game_window_width}, {game_window_height})")
        
        # 计算窗口中心坐标并点击
        center_x = game_window_left + game_window_width // 2
        center_y = game_window_top + game_window_height // 2
        pyautogui.click(center_x, center_y)
        print(f"已点击窗口中心: ({center_x}, {center_y})")
    else:
        print("未找到游戏窗口，脚本退出")
        return

    # 主动触发F键
    pyautogui.press('f')
    print("已按下F键")
    
    time.sleep(1)
    
    # 计算相对坐标
    normalized_offset_x = 0.20
    normalized_offset_y = 0.09
    target_x = game_window_left + int(normalized_offset_x * game_window_width)
    target_y = game_window_top + int(normalized_offset_y * game_window_height)
    
    # 将鼠标移动到计算出的相对位置
    pyautogui.moveTo(target_x, target_y)
    print(f"鼠标已移动到: ({target_x}, {target_y})")
    
    time.sleep(0.5)
    
    # 鼠标左键点击
    pyautogui.click()
    time.sleep(0.5)
    
    # 移动到新的归一化偏移位置进行下滚操作 (0.15, 0.36)
    scroll_x = game_window_left + int(0.15 * game_window_width)
    scroll_y = game_window_top + int(0.36 * game_window_height)
    pyautogui.moveTo(scroll_x, scroll_y)
    print(f"鼠标已移动到下滚位置: ({scroll_x}, {scroll_y})")
    
    # 鼠标快速下滚到底
    for _ in range(50):
        pyautogui.scroll(-5)  # 每次滚动-5，共50次
        time.sleep(0.05)  # 每次滚动间隔0.05秒
    
if __name__ == "__main__":
    main()