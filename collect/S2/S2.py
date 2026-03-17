import time
import pyautogui
import cv2
import numpy as np
import win32gui
import win32api
import win32con
from datetime import datetime
import math
import mouse_control


def get_game_window_rect():
    """获取游戏窗口矩形区域"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "BooK思议" in title:
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        hwnd = windows[0]
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, 9)
            time.sleep(0.5)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        return left, top, width, height
    else:
        return None


def activate_game_window():
    """识别窗口并置为最前"""
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "BooK思议" in title:
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        hwnd = windows[0]
        win32gui.SetForegroundWindow(hwnd)
        print(f"窗口已置为最前")
        return hwnd
    else:
        print("未找到游戏窗口")
        return None


def press_m_key():
    """按下M键"""
    M_KEY = 0x4D
    win32api.keybd_event(M_KEY, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(M_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
    print("M键已按下")


def match_and_click(template_path, confidence=0.7):
    """对模板进行图像匹配并点击识别到的位置中心"""
    # 获取游戏窗口
    game_rect = get_game_window_rect()
    if game_rect is None:
        print("未找到游戏窗口")
        return False
    
    left, top, width, height = game_rect
    
    # 截图游戏窗口
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    img_array = np.array(screenshot)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # 读取模板
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"模板加载失败: {template_path}")
        return False
    
    # 转换为灰度图进行匹配
    gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 模板匹配
    result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= confidence:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        
        # 转换为屏幕坐标
        screen_x = left + center_x
        screen_y = top + center_y
        
        print(f"识别成功，置信度: {max_val:.3f}")
        print(f"点击位置: ({screen_x}, {screen_y})")
        
        # 点击
        pyautogui.click(screen_x, screen_y)
        return True
    else:
        print(f"未识别到目标，置信度: {max_val:.3f}")
        return False


if __name__ == "__main__":
    print("开始执行...")
    
    # 识别窗口并置为最前
    activate_game_window()
    
    # 等待3秒
    print("等待3秒...")
    time.sleep(3)
    
    # 按下M键
    press_m_key()
    
    # 等待一下让菜单打开
    time.sleep(1)
    
    # 图像匹配并点击
    template_path = r"D:\mingriHelper\collect\S2\images\gatherTeam\gatherTeam_ico.png"
    match_and_click(template_path, confidence=0.7)
    
    print("执行完成")
