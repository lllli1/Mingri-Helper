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
import screenshot
import tiqu


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


def press_esc_key():
    """按下ESC键"""
    ESC_KEY = 0x1B
    win32api.keybd_event(ESC_KEY, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(ESC_KEY, 0, win32con.KEYEVENTF_KEYUP, 0)
    print("ESC键已按下")


def calculate_angle(point1, point2):
    """计算从point1指向point2的角度（竖直向上是0度）"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    
    angle_rad = math.atan2(dx, -dy)
    angle_deg = math.degrees(angle_rad)
    
    if angle_deg < 0:
        angle_deg += 360
    
    return round(angle_deg, 2)


def draw_and_save_connection(img1_array, coords1, coords2, template_paths, output_dir="screenshots", confidence=0.7):
    """在第一个图像中检测目标点，计算第二个区域中心，绘制连接线并保存"""
    img1_bgr = cv2.cvtColor(img1_array, cv2.COLOR_RGB2BGR)
    marked_img = img1_bgr.copy()
    
    # 计算第二个区域中心在第一个图像中的相对位置
    region2_center_x = int((coords2['top_left'][0] - coords1['top_left'][0]))
    region2_center_y = int((coords2['top_left'][1] - coords1['top_left'][1]))
    region2_width = int(coords2['bottom_right'][0] - coords2['top_left'][0])
    region2_height = int(coords2['bottom_right'][1] - coords2['top_left'][1])
    region2_center_x += region2_width // 2
    region2_center_y += region2_height // 2
    
    print(f"第二个区域中心相对位置: ({region2_center_x}, {region2_center_y})")
    
    # 检测第一个图像中的目标点
    detections = []
    for template_path in template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            continue
        
        gray_img = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # 框出目标点
            cv2.rectangle(marked_img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
            cv2.circle(marked_img, (center_x, center_y), 5, (0, 255, 0), -1)
            
            detections.append((center_x, center_y))
            print(f"检测到目标点: ({center_x}, {center_y})")
    
    if detections:
        detected_point = detections[0]
        
        # 绘制绿线连接
        cv2.line(marked_img, detected_point, (region2_center_x, region2_center_y), (0, 255, 0), 2)
        
        # 计算角度
        angle = calculate_angle((region2_center_x, region2_center_y), detected_point)
        print(f"连接线角度: {angle}°")
        
        # 保存标记后的截图
        marked_path = os.path.join(output_dir, "smallMap_with_line.png")
        cv2.imwrite(marked_path, marked_img)
        print(f"标记图像已保存: {marked_path}")
        
        return {
            'angle': angle,
            'detected_point': detected_point,
            'region2_center': (region2_center_x, region2_center_y),
            'marked_path': marked_path
        }
    
    return None


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
    import os
    
    # 初始化变量，确保在所有代码路径中都可用
    img1 = None
    coords1 = None
    img2 = None
    coords2 = None
    template_paths = []
    output_dir = "screenshots"
    
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
    if match_and_click(template_path, confidence=0.7):
        print("\n点击成功，按下ESC键...")
        press_esc_key()
        time.sleep(1)
        
        print("开始截图...")
        
        # 创建screenshots文件夹
        output_dir = "screenshots"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 定义两个截图区域
        region1_top_left = (0.865, 0.08)
        region1_bottom_right = (0.985, 0.27)
        
        region2_top_left = (0.92, 0.16)
        region2_bottom_right = (0.938, 0.19)
        
# 截取第一个区域并保存
        img1 = None
        coords1 = None
        img2 = None
        coords2 = None
        template_paths = [
            r"D:\mingriHelper\collect\S2\images\point\point.png",
            r"D:\mingriHelper\collect\S2\images\point\point_2.png"
        ]
        
        print("\n截取第一个区域...")
        result1 = screenshot.capture_rectangle(region1_top_left, region1_bottom_right, 
                                              save_path=os.path.join(output_dir, "smallMap.png"))
        if not result1:
            print("第一个区域截图失败")
        else:
            img1, coords1 = result1
            print(f"第一个区域截图成功: {coords1}")
            
            # 截取第二个区域并保存
            print("\n截取第二个区域...")
            result2 = screenshot.capture_rectangle(region2_top_left, region2_bottom_right,
                                                  save_path=os.path.join(output_dir, "mainPosition.png"))
            if not result2:
                print("第二个区域截图失败")
            else:
                img2, coords2 = result2
                print(f"第二个区域截图成功: {coords2}")
                
                # 绘制连接线并计算角度
                print("\n绘制连接线...")
                connection_result = draw_and_save_connection(img1, coords1, coords2, template_paths, output_dir, confidence=0.5)
                
                if connection_result:
                    print(f"\n✓ 处理成功！")
                    print(f"目标点: {connection_result['detected_point']}")
                    print(f"第二个区域中心: {connection_result['region2_center']}")
                    print(f"连接线角度: {connection_result['angle']}°")
                    
                    # 使用tiqu.py模块进行箭头分析
                    print("\n开始箭头分析...")
                    arrow_result = tiqu.get_arrow_direction(img2, process_scale=8, save_marked=True, output_dir=output_dir)
                    
                    if arrow_result:
                        print(f"✓ 箭头分析成功！")
                        print(f"箭头朝向角度: {arrow_result['angle']}°")
                        print(f"箭头质心位置: {arrow_result['centroid']}")
                        print(f"箭头尖端位置: {arrow_result['tip']}")
                        print(f"箭头凹点位置: {arrow_result['notch']}")
                        if arrow_result['marked_path']:
                            print(f"箭头标记图像已保存: {arrow_result['marked_path']}")
                    else:
                        print("箭头分析失败")
                else:
                    print("未检测到目标点")
    
    print("\n执行完成")
    
    # 示例：展示tiqu.py的完整功能
    print("\n" + "="*50)
    print("tiqu.py模块功能演示")
    print("="*50)
    
    # 创建演示用的输出目录
    demo_output_dir = "screenshots"
    if not os.path.exists(demo_output_dir):
        os.makedirs(demo_output_dir)
    
    # 确保变量在演示代码中使用前已经被定义
    if img2 is not None:
        print("\n1. 使用analyze_arrow_from_screenshot进行详细分析...")
        detailed_result = tiqu.analyze_arrow_from_screenshot(img2, process_scale=8, 
                                                            output_path=os.path.join(demo_output_dir, "detailed_arrow_analysis.png"))
        if detailed_result:
            print(f"   详细分析完成 - 角度: {detailed_result['angle']}°")
            print(f"   质心: {detailed_result['centroid']}")
            print(f"   尖端: {detailed_result['tip']}")
            print(f"   凹点: {detailed_result['notch']}")
            print(f"   顶点数: {len(detailed_result['vertices'])}")
        
        print("\n2. 测试get_arrow_direction_from_vertices函数...")
        # 使用检测结果中的顶点进行测试
        if detailed_result and len(detailed_result['vertices']) >= 4:
            test_vertices = detailed_result['vertices'][:4]  # 取前4个顶点
            angle_test, tip_test, notch_test, centroid_test = tiqu.get_arrow_direction_from_vertices(test_vertices)
            print(f"   顶点测试角度: {angle_test}°")
            print(f"   尖端: {tip_test}")
            print(f"   凹点: {notch_test}")
            print(f"   质心: {centroid_test}")
        else:
            print("   无法进行顶点测试（顶点不足或分析失败）")
    else:
        print("\n没有可用的图像进行tiqu.py功能演示")
