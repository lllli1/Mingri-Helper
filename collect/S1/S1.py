import pyautogui
import time
import json

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
    
    # 在开始滚动前，先点击相对坐标(0.15, 0.15)位置
    init_x = game_window_left + int(0.15 * game_window_width)
    init_y = game_window_top + int(0.15 * game_window_height)
    pyautogui.moveTo(init_x, init_y)
    pyautogui.click()
    print(f"已点击初始化位置: ({init_x}, {init_y})")
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

    # 完成所有操作后等待3秒
    time.sleep(3)
    
    # 读取当前点击序号
    try:
        with open('s1_state.json', 'r') as f:
            state = json.load(f)
            click_index = state.get('click_index', 1)
    except FileNotFoundError:
        click_index = 1
    
    # 确保序号在有效范围内
    if click_index < 1 or click_index > 10:
        click_index = 1
    
    # 使用线性函数计算指定序号的点击位置
    # y = -0.0588 * x + 0.9425，其中x为序号(0-9)
    base_y = 0.9425
    slope = -0.0588
    normalized_offset_x = 0.15
    
    # 计算当前序号对应的y坐标（将序号转换为0基）
    normalized_offset_y = round(base_y + slope * (click_index - 1), 2)
    target_x = game_window_left + int(normalized_offset_x * game_window_width)
    target_y = game_window_top + int(normalized_offset_y * game_window_height)
    
    # 移动到目标位置并点击
    pyautogui.moveTo(target_x, target_y)
    pyautogui.click()
    print(f"已点击第{click_index}个位置: ({target_x}, {target_y})")

    # 当前所有操作完成后
    time.sleep(0.5)
    scroll_x = game_window_left + int(0.15 * game_window_width)
    scroll_y = game_window_top + int(0.36 * game_window_height)
    pyautogui.moveTo(scroll_x, scroll_y)
    for _ in range(40):
        pyautogui.scroll(-3)
        time.sleep(0.02)
    time.sleep(3)
    # 读取当前点击序号
    try:
        with open('s1_state.json', 'r') as f:
            state = json.load(f)
            click_index = state.get('click_index', 1)
    except FileNotFoundError:
        click_index = 1
    
    # 确保序号在有效范围内
    if click_index < 1 or click_index > 10:
        click_index = 1
    
    # 构建图像路径
    image_path = f"images/level_{click_index}/level_{click_index}_map.png"
    
    # 在游戏区域查找图像
    try:
        # 获取游戏窗口截图
        game_screenshot = pyautogui.screenshot(region=(game_window_left, game_window_top, game_window_width, game_window_height))
        # 保存截图用于调试
        game_screenshot.save('debug_game_window.png')
        
        # 先检查图像文件是否存在
        import os
        if not os.path.exists(image_path):
            print(f"图像文件不存在: {os.path.abspath(image_path)}")
            return
        
        # 查找主图像位置
        location = pyautogui.locate(image_path, game_screenshot, confidence=0.97)
        if location:
            center_x, center_y = pyautogui.center(location)
            # 转换为屏幕绝对坐标
            abs_x = game_window_left + center_x
            abs_y = game_window_top + center_y
            pyautogui.click(abs_x, abs_y)
            print(f"已点击找到的图像位置: ({abs_x}, {abs_y})")
            
            # 等待新状况图像出现
            time.sleep(3)
            
            # 重新获取游戏窗口截图
            game_screenshot = pyautogui.screenshot(region=(game_window_left, game_window_top, game_window_width, game_window_height))
            
            # 主图像找到后，进行两个附加图像的识别
            info_image_path_1 = f"images/level_{click_index}/level_{click_index}_map_info1.png"
            info_image_path_2 = f"images/level_{click_index}/level_{click_index}_map_info2.png"
            
            # 初始化变量
            info_location_1 = None
            info_location_2 = None
            
            # 检查第一个附加图像文件是否存在
            if not os.path.exists(info_image_path_1):
                print(f"附加图像文件不存在: {os.path.abspath(info_image_path_1)}")
            else:
                # 查找第一个附加图像位置
                info_location_1 = pyautogui.locate(info_image_path_1, game_screenshot, confidence=0.97)
            
            # 检查第二个附加图像文件是否存在
            if not os.path.exists(info_image_path_2):
                print(f"附加图像文件不存在: {os.path.abspath(info_image_path_2)}")
            else:
                # 查找第二个附加图像位置
                info_location_2 = pyautogui.locate(info_image_path_2, game_screenshot, confidence=0.97)
            
            # 只有当两个附加图像都找到时才输出匹配成功并按F键
            if info_location_1 and info_location_2:
                print("两个附加图像匹配成功，按下F键")
                # pyautogui.press('f')
            else:
                if not info_location_1:
                    print(f"未找到附加图像1: {info_image_path_1}")
                if not info_location_2:
                    print(f"未找到附加图像2: {info_image_path_2}")
        else:
            print(f"未找到主图像: {image_path}")
    except Exception as e:
        print(f"查找图像时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()