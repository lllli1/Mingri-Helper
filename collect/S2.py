import time
import pyautogui
import cv2
import numpy as np
from PIL import Image
import win32gui
import math

def get_game_window_rect():
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

def capture_game_window():
    game_rect = get_game_window_rect()
    if game_rect is None:
        print("未找到游戏窗口")
        return None
    
    left, top, width, height = game_rect
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return np.array(screenshot), left, top

def capture_relative_region(screenshot_img, left, top, width, height, norm_left, norm_top, norm_right, norm_bottom):
    x1 = int(norm_left * width)
    y1 = int(norm_top * height)
    x2 = int(norm_right * width)
    y2 = int(norm_bottom * height)
    region = screenshot_img[y1:y2, x1:x2]
    region_path = 'relative_region.png'
    cv2.imwrite(region_path, cv2.cvtColor(region, cv2.COLOR_RGB2BGR))
    print(f"已保存相对区域截图: {region_path}")

def find_and_mark_image(template_path, confidence=0.8):
    # 获取游戏窗口截图
    result = capture_game_window()
    if result is None:
        return None
    
    screen_img, left, top = result
    orig_img = screen_img.copy()
    
    # 读取模板图像并转换为灰度图
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"模板图像加载失败: {template_path}")
        return None
    
    # 将截图转换为灰度图
    gray_screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGB2GRAY)
    
    # 执行模板匹配
    result = cv2.matchTemplate(gray_screen_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 在原图上绘制矩形框
    h, w = template.shape[:2]
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(orig_img, top_left, bottom_right, (0, 255, 0), 2)
    
    # 添加置信度文本
    cv2.putText(orig_img, f'Confidence: {max_val:.3f}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 保存带标记的截图
    marked_screenshot_path = 'marked_screenshot.png'
    cv2.imwrite(marked_screenshot_path, orig_img)
    print(f"已保存带标记的截图: {marked_screenshot_path}")
    
    if max_val >= confidence:
        center_x = top_left[0] + w // 2 + left
        center_y = top_left[1] + h // 2 + top
        return (center_x, center_y), max_val
    else:
        print(f"未找到匹配的图像，最大置信度: {max_val:.3f}")
        return None, max_val

time.sleep(3)
pyautogui.press('m')
time.sleep(2)

# 获取游戏窗口截图用于后续区域捕获
result = capture_game_window()

# 图像识别并标记
target_result = find_and_mark_image(r'D:\mingriHelper\collect\images\gatherTeam\gatherTeam_ico.png', confidence=0.8)
if target_result and target_result[0] is not None:
    target_pos, conf = target_result
    if conf > 0.9:
        pyautogui.click(target_pos[0], target_pos[1])
        time.sleep(0.5)
        pyautogui.press('esc')
        print(f"已点击目标位置: {target_pos}, 置信度: {conf:.3f}，并按下ESC键")

    else:
        print(f"置信度存疑: {conf:.3f}，未达到点击阈值")
else:
    print(f"未找到目标，最大置信度: {target_result[1] if target_result else 'N/A'}")
    
time.sleep(2)

# 根据Y键记录的两个点截取矩形区域（使用归一化坐标）
# 第一个点 (0.913934, 0.174914) - 左上角
# 第二个点 (0.927596, 0.187572) - 右下角
norm_point1 = (0.92, 0.176)
norm_point2 = (0.934, 0.201)

# 获取最新截图
new_result = capture_game_window()
if new_result is not None:
    screen_img, left, top = new_result
    height, width = screen_img.shape[:2]
    
    # 将归一化坐标转换为像素坐标
    x1 = int(norm_point1[0] * width)
    y1 = int(norm_point1[1] * height)
    x2 = int(norm_point2[0] * width)
    y2 = int(norm_point2[1] * height)
    
    # 确保坐标顺序正确（左上角和右下角）
    x_min = min(x1, x2)
    y_min = min(y1, y2)
    x_max = max(x1, x2)
    y_max = max(y1, y2)
    
    # 截取矩形区域
    region = screen_img[y_min:y_max, x_min:x_max]
    
    # 保存截取的区域
    region_path = 'arrow_region.png'
    cv2.imwrite(region_path, cv2.cvtColor(region, cv2.COLOR_RGB2BGR))
    print(f"已截取箭头区域: ({x_min}, {y_min}) 到 ({x_max}, {y_max}), 保存到 {region_path}")

