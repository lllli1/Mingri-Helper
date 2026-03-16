import time
import pyautogui
import cv2
import numpy as np
import win32gui


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


def find_and_mark_image(template_path, confidence=0.8):
    """
    在游戏窗口中查找模板图像并标记
    返回: ((center_x, center_y), confidence) 或 (None, max_confidence)
    """
    result = capture_game_window()
    if result is None:
        return None, 0
    
    screen_img, left, top = result
    orig_img = screen_img.copy()
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"模板图像加载失败: {template_path}")
        return None, 0
    
    gray_screen_img = cv2.cvtColor(screen_img, cv2.COLOR_RGB2GRAY)
    
    result = cv2.matchTemplate(gray_screen_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    h, w = template.shape[:2]
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(orig_img, top_left, bottom_right, (0, 255, 0), 2)
    
    cv2.putText(orig_img, f'Confidence: {max_val:.3f}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
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


# 主流程
time.sleep(3)
pyautogui.press('m')
time.sleep(2)

# 查找并点击 gatherTeam_ico
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
