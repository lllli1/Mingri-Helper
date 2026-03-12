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

def get_arrow_direction(points):
    """
    使用质心距离法，从 4 个顶点中找出尖端(Tip)和凹点(Notch)，并计算方向。
    """
    pts = np.array(points)
    
    # 1. 计算质心 (Centroid)
    centroid = np.mean(pts, axis=0)
    
    # 2. 计算每个顶点到质心的距离
    distances = np.linalg.norm(pts - centroid, axis=1)
    
    # 3. 距离最远的是尖端，距离最近的是凹点
    tip_idx = np.argmax(distances)
    notch_idx = np.argmin(distances)
    
    p_tip = pts[tip_idx]
    p_notch = pts[notch_idx]
    
    # 4. 计算方向向量
    dx = p_tip[0] - p_notch[0]
    dy = p_tip[1] - p_notch[1]
    
    # 5. 计算角度 (注意：图像坐标系中 Y 轴向下，所以在算数学角度时我们将 dy 取反)
    # 这样算出来的角度：0°向右，90°向上，180°向左，-90°向下
    angle_rad = math.atan2(-dy, dx) 
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg, p_tip, p_notch, centroid

def analyze_arrow_image(image_path, process_scale=8, view_scale=4):
    """
    从箭头图像中提取顶点、计算方向，并生成可视化截图。
    """
    # ================= 1. 高精度提取顶点 =================
    orig_img = cv2.imread(image_path)
    if orig_img is None:
        print(f"未能读取图片 '{image_path}'")
        return None
    
    h, w = orig_img.shape[:2]
    high_res_img = cv2.resize(orig_img, (w * process_scale, h * process_scale), interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(high_res_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("未找到轮廓！")
        return None
        
    largest_contour = max(contours, key=cv2.contourArea)
    perimeter = cv2.arcLength(largest_contour, True)
    epsilon_ratio = 0.01
    hr_vertices = []
    
    for _ in range(50):
        approx = cv2.approxPolyDP(largest_contour, epsilon_ratio * perimeter, True)
        if len(approx) == 4:
            hr_vertices = [point[0].tolist() for point in approx]
            break
        epsilon_ratio += 0.005 if len(approx) > 4 else -0.005
    
    if not hr_vertices:
        hr_vertices = [p[0].tolist() for p in cv2.approxPolyDP(largest_contour, 0.04*perimeter, True)]
    
    # 换算回原图的高精度浮点坐标
    original_vertices = [(x / process_scale, y / process_scale) for x, y in hr_vertices]
    
    # ================= 2. 计算方向 =================
    angle, p_tip, p_notch, p_centroid = get_arrow_direction(original_vertices)
    
    print("\n====== 箭头方向分析结果 ======")
    print(f"质心坐标: ({p_centroid[0]:.2f}, {p_centroid[1]:.2f})")
    print(f"凹点(尾部): ({p_notch[0]:.2f}, {p_notch[1]:.2f})")
    print(f"尖端(头部): ({p_tip[0]:.2f}, {p_tip[1]:.2f})")
    print(f"数学坐标系指向角度: {angle:.2f}°")
    print("==============================\n")
    
    # ================= 3. 高清可视化 =================
    view_w, view_h = w * view_scale, h * view_scale
    upscaled_view = cv2.resize(orig_img, (view_w, view_h), interpolation=cv2.INTER_CUBIC)
    
    # 转换坐标到放大后的视图用于绘制
    def scale_pt(pt):
        return (int(pt[0] * view_scale), int(pt[1] * view_scale))
    
    v_tip = scale_pt(p_tip)
    v_notch = scale_pt(p_notch)
    v_centroid = scale_pt(p_centroid)
    
    # 画所有角点 (蓝色小圆)
    for pt in original_vertices:
        cv2.circle(upscaled_view, scale_pt(pt), radius=3, color=(255, 0, 0), thickness=-1)
    
    # 画质心 (黄色)
    cv2.circle(upscaled_view, v_centroid, radius=5, color=(0, 255, 255), thickness=-1)
    cv2.putText(upscaled_view, "Centroid", (v_centroid[0]+10, v_centroid[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    
    # 画凹点 (红色)
    cv2.circle(upscaled_view, v_notch, radius=6, color=(0, 0, 255), thickness=-1)
    
    # 画尖端 (绿色)
    cv2.circle(upscaled_view, v_tip, radius=6, color=(0, 255, 0), thickness=-1)
    
    # 画出方向引导线 (一条绿色的箭头线，从凹点穿过质心指向尖端)
    cv2.arrowedLine(upscaled_view, v_notch, v_tip, color=(0, 255, 0), thickness=2, tipLength=0.15)
    
    # 保存可视化截图
    viz_path = 'arrow_analysis_visualization.png'
    cv2.imwrite(viz_path, upscaled_view)
    print(f"已保存箭头分析可视化截图: {viz_path}")
    
    return angle, p_tip, p_notch, p_centroid

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
    
    # 分析箭头方向并生成可视化截图
    arrow_result = analyze_arrow_image(region_path, process_scale=8, view_scale=4)
    if arrow_result is not None:
        angle, p_tip, p_notch, p_centroid = arrow_result
        print(f"箭头指向角度: {angle:.2f}°")

