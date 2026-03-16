import time
import pyautogui
import cv2
import numpy as np
import win32gui
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


def capture_rectangle(top_left_norm, bottom_right_norm, save_path=None):
    """
    根据两个归一化坐标点截图矩形区域
    
    Args:
        top_left_norm: 左上角 (norm_x, norm_y)
        bottom_right_norm: 右下角 (norm_x, norm_y)
        save_path: 可选，截图保存路径
    
    Returns:
        tuple: (截图数组, 实际坐标) 或 None
    """
    game_rect = get_game_window_rect()
    if game_rect is None:
        print("未找到游戏窗口")
        return None
    
    left, top, width, height = game_rect
    
    # 计算左上角实际坐标
    top_left_x = round(left + top_left_norm[0] * width, 2)
    top_left_y = round(top + top_left_norm[1] * height, 2)
    
    # 计算右下角实际坐标
    bottom_right_x = round(left + bottom_right_norm[0] * width, 2)
    bottom_right_y = round(top + bottom_right_norm[1] * height, 2)
    
    # 计算截图区域的宽高
    region_width = int(bottom_right_x - top_left_x)
    region_height = int(bottom_right_y - top_left_y)
    
    # 截图
    screenshot = pyautogui.screenshot(region=(int(top_left_x), int(top_left_y), region_width, region_height))
    img_array = np.array(screenshot)
    
    if save_path:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        cv2.imwrite(save_path, img_bgr)
        print(f"截图已保存: {save_path}")
    
    return img_array, {
        'top_left': (top_left_x, top_left_y),
        'bottom_right': (bottom_right_x, bottom_right_y),
        'size': (region_width, region_height)
    }


def show_rectangle_overlay(top_left_norm, bottom_right_norm, duration=5):
    """
    在游戏窗口上实时显示绿框
    
    Args:
        top_left_norm: 左上角 (norm_x, norm_y)
        bottom_right_norm: 右下角 (norm_x, norm_y)
        duration: 显示时长（秒）
    """
    game_rect = get_game_window_rect()
    if game_rect is None:
        print("未找到游戏窗口")
        return
    
    left, top, width, height = game_rect
    
    # 计算实际坐标
    top_left_x = int(left + top_left_norm[0] * width)
    top_left_y = int(top + top_left_norm[1] * height)
    bottom_right_x = int(left + bottom_right_norm[0] * width)
    bottom_right_y = int(top + bottom_right_norm[1] * height)
    
    # 获取完整游戏窗口截图
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    img_array = np.array(screenshot)
    
    # 绘制绿框
    cv2.rectangle(img_array, 
                  (top_left_x - left, top_left_y - top), 
                  (bottom_right_x - left, bottom_right_y - top), 
                  (0, 255, 0), 3)
    
    # 显示窗口
    cv2.imshow('Game Window - Green Rectangle', img_array)
    print(f"显示绿框 {duration} 秒...")
    cv2.waitKey(int(duration * 1000))
    cv2.destroyAllWindows()


def get_arrow_direction_from_vertices(points):
    """
    从4个顶点中找出尖端(Tip)和凹点(Notch)，并计算方向
    坐标系：原点在质心，竖直向上是0度/360度，竖直向下是180度
    
    Args:
        points: 4个顶点坐标列表
    
    Returns:
        tuple: (角度, 尖端, 凹点, 质心)
    """
    import math
    
    pts = np.array(points)
    
    # 计算质心
    centroid = np.mean(pts, axis=0)
    
    # 计算每个顶点到质心的距离
    distances = np.linalg.norm(pts - centroid, axis=1)
    
    # 距离最远的是尖端，距离最近的是凹点
    tip_idx = np.argmax(distances)
    notch_idx = np.argmin(distances)
    
    p_tip = pts[tip_idx]
    p_notch = pts[notch_idx]
    
    # 计算从质心到尖端的方向向量
    dx = p_tip[0] - centroid[0]
    dy = p_tip[1] - centroid[1]
    
    # 转换为指定坐标系：竖直向上是0度，竖直向下是180度
    # 原点在质心
    angle_rad = math.atan2(dx, -dy)
    angle_deg = math.degrees(angle_rad)
    
    # 确保角度在0-360范围内
    if angle_deg < 0:
        angle_deg += 360
    
    return round(angle_deg, 2), p_tip, p_notch, centroid


def get_arrow_direction(img_array, process_scale=8):
    """
    从截图中获取箭头朝向度数
    
    Args:
        img_array: 截图数组 (RGB格式)
        process_scale: 处理缩放倍数
    
    Returns:
        float: 箭头朝向度数 (0-360)，如果失败返回None
    """
    result = analyze_arrow_from_screenshot(img_array, process_scale=process_scale)
    if result:
        return result['angle']
    return None


def analyze_arrow_from_screenshot(img_array, process_scale=8, output_path=None):
    """
    从截图中分析箭头方向
    
    Args:
        img_array: 截图数组 (RGB格式)
        process_scale: 处理缩放倍数
        output_path: 可选，标记后的截图保存路径
    
    Returns:
        dict: 包含分析结果和标记图像
    """
    if img_array is None:
        print("截图数组为空")
        return None
    
    # 转换为BGR用于cv2处理
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    h, w = img_bgr.shape[:2]
    
    # 高精度处理
    high_res_img = cv2.resize(img_bgr, (w * process_scale, h * process_scale), interpolation=cv2.INTER_CUBIC)
    
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
    
    # 计算方向
    angle, p_tip, p_notch, p_centroid = get_arrow_direction_from_vertices(original_vertices)
    
    # 绘制标记
    marked_img = img_bgr.copy()
    
    # 画所有角点 (蓝色小圆)
    for pt in original_vertices:
        cv2.circle(marked_img, (int(pt[0]), int(pt[1])), radius=3, color=(255, 0, 0), thickness=-1)
    
    # 画质心 (黄色)
    cv2.circle(marked_img, (int(p_centroid[0]), int(p_centroid[1])), radius=5, color=(0, 255, 255), thickness=-1)
    
    # 画凹点 (红色)
    cv2.circle(marked_img, (int(p_notch[0]), int(p_notch[1])), radius=6, color=(0, 0, 255), thickness=-1)
    
    # 画尖端 (绿色)
    cv2.circle(marked_img, (int(p_tip[0]), int(p_tip[1])), radius=6, color=(0, 255, 0), thickness=-1)
    
    # 画方向引导线
    cv2.arrowedLine(marked_img, (int(p_notch[0]), int(p_notch[1])), (int(p_tip[0]), int(p_tip[1])), 
                    color=(0, 255, 0), thickness=2, tipLength=0.15)
    
    if output_path:
        cv2.imwrite(output_path, marked_img)
        print(f"箭头分析结果已保存: {output_path}")
    
    return {
        'marked_image': marked_img,
        'angle': angle,
        'centroid': (round(p_centroid[0], 2), round(p_centroid[1], 2)),
        'tip': (round(p_tip[0], 2), round(p_tip[1], 2)),
        'notch': (round(p_notch[0], 2), round(p_notch[1], 2)),
        'vertices': original_vertices
    }


def calculate_angle(point1, point2):
    """
    计算从point1指向point2的角度
    规定：竖直向上是0度/360度，竖直向下是180度
    
    Args:
        point1: 起点 (x, y)
        point2: 终点 (x, y)
    
    Returns:
        float: 角度 (0-360度)
    """
    import math
    
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    
    # 计算弧度（标准数学坐标系：右为0度，上为90度）
    angle_rad = math.atan2(dx, -dy)  # -dy是因为屏幕坐标Y轴向下
    
    # 转换为度数
    angle_deg = math.degrees(angle_rad)
    
    # 确保角度在0-360范围内
    if angle_deg < 0:
        angle_deg += 360
    
    return round(angle_deg, 2)


def draw_line_between_points(img_array, point1, point2, color=(0, 255, 0), thickness=2, output_path=None):
    """
    在图像上绘制连接两个点的直线
    
    Args:
        img_array: 图像数组 (RGB格式)
        point1: 第一个点 (x, y)
        point2: 第二个点 (x, y)
        color: 线条颜色 (BGR格式)
        thickness: 线条粗度
        output_path: 可选，保存路径
    
    Returns:
        np.ndarray: 绘制后的图像
    """
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    marked_img = img_bgr.copy()
    
    # 绘制直线
    cv2.line(marked_img, point1, point2, color, thickness)
    
    # 绘制两个点
    cv2.circle(marked_img, point1, 5, (255, 0, 0), -1)  # 蓝色
    cv2.circle(marked_img, point2, 5, (0, 0, 255), -1)  # 红色
    
    if output_path:
        cv2.imwrite(output_path, marked_img)
        print(f"连接线已保存: {output_path}")
    
    return marked_img


def capture_detect_and_connect(region1_top_left, region1_bottom_right, region2_top_left, region2_bottom_right, 
                               template_paths, output_dir="screenshots", confidence=0.7):
    """
    截图两个区域，检测第一个区域的点，连接识别点和第二个区域的中心点
    
    Args:
        region1_top_left: 第一个区域左上角
        region1_bottom_right: 第一个区域右下角
        region2_top_left: 第二个区域左上角
        region2_bottom_right: 第二个区域右下角
        template_paths: 模板图像路径列表
        output_dir: 输出目录
        confidence: 置信度阈值
    
    Returns:
        dict: 包含所有结果信息
    """
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 截图第一个区域
    result1 = capture_rectangle(region1_top_left, region1_bottom_right)
    if result1 is None:
        print("第一个区域截图失败")
        return None
    
    img1_array, coords1 = result1
    
    # 截图第二个区域
    result2 = capture_rectangle(region2_top_left, region2_bottom_right)
    if result2 is None:
        print("第二个区域截图失败")
        return None
    
    img2_array, coords2 = result2
    
    # 计算第二个区域的中心点（相对于第一个区域的坐标系）
    region2_center_x = int((coords2['top_left'][0] - coords1['top_left'][0]))
    region2_center_y = int((coords2['top_left'][1] - coords1['top_left'][1]))
    region2_width = int(coords2['bottom_right'][0] - coords2['top_left'][0])
    region2_height = int(coords2['bottom_right'][1] - coords2['top_left'][1])
    region2_center_x += region2_width // 2
    region2_center_y += region2_height // 2
    
    # 检测第一个区域的点
    detection_result = detect_and_mark_points(img1_array, template_paths, confidence=confidence)
    
    if detection_result is None or detection_result['count'] == 0:
        print("未检测到识别点")
        return None
    
    # 获取识别点的中心
    detected_point = detection_result['detections'][0]['center']
    
    # 计算角度（从第二个区域中心指向识别点）
    angle = calculate_angle((region2_center_x, region2_center_y), detected_point)
    
    # 在第一个区域的图像上绘制连接线
    marked_img = draw_line_between_points(
        img1_array, 
        detected_point, 
        (region2_center_x, region2_center_y),
        color=(0, 255, 0),
        thickness=2
    )
    
    # 保存结果
    original_path = os.path.join(output_dir, "smallMap.png")
    marked_path = os.path.join(output_dir, "smallMap_with_line.png")
    mainposition_path = os.path.join(output_dir, "mainPosition.png")
    
    img1_bgr = cv2.cvtColor(img1_array, cv2.COLOR_RGB2BGR)
    img2_bgr = cv2.cvtColor(img2_array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(original_path, img1_bgr)
    cv2.imwrite(marked_path, marked_img)
    cv2.imwrite(mainposition_path, img2_bgr)
    
    return {
        'region1_coords': coords1,
        'region2_coords': coords2,
        'detected_point': detected_point,
        'region2_center': (region2_center_x, region2_center_y),
        'angle': angle,
        'original_path': original_path,
        'marked_path': marked_path,
        'mainposition_path': mainposition_path,
        'detection_count': detection_result['count']
    }


def detect_and_mark_points(img_array, template_paths, confidence=0.7, output_path=None):
    """
    在截图中检测模板图像并框出识别点
    
    Args:
        img_array: 截图数组 (RGB格式)
        template_paths: 模板图像路径列表
        confidence: 置信度阈值
        output_path: 可选，标记后的截图保存路径
    
    Returns:
        dict: 包含检测结果和标记后的图像
    """
    if img_array is None:
        print("截图数组为空")
        return None
    
    # 转换为BGR用于cv2处理
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    marked_img = img_bgr.copy()
    
    detections = []
    
    for template_path in template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"模板加载失败: {template_path}")
            continue
        
        # 转换为灰度图进行匹配
        gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 模板匹配
        result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            h, w = template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            # 绘制绿框
            cv2.rectangle(marked_img, top_left, bottom_right, (0, 255, 0), 2)
            
            # 计算中心点
            center_x = top_left[0] + w // 2
            center_y = top_left[1] + h // 2
            cv2.circle(marked_img, (center_x, center_y), 5, (0, 255, 0), -1)
            
            detections.append({
                'template': template_path,
                'confidence': round(max_val, 3),
                'top_left': top_left,
                'bottom_right': bottom_right,
                'center': (center_x, center_y)
            })
            
            print(f"检测到: {template_path}, 置信度: {max_val:.3f}")
    
    # 保存标记后的截图
    if output_path and detections:
        cv2.imwrite(output_path, marked_img)
        print(f"标记后的截图已保存: {output_path}")
    
    return {
        'marked_image': marked_img,
        'detections': detections,
        'count': len(detections)
    }


def capture_and_detect(top_left_norm, bottom_right_norm, name, template_paths, output_dir="screenshots", confidence=0.7):
    """
    截图并检测模板
    
    Args:
        top_left_norm: 左上角 (norm_x, norm_y)
        bottom_right_norm: 右下角 (norm_x, norm_y)
        name: 文件名（不含扩展名）
        template_paths: 模板图像路径列表
        output_dir: 输出目录
        confidence: 置信度阈值
    
    Returns:
        dict: 包含截图、检测结果和标记图像
    """
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 截图
    result = capture_rectangle(top_left_norm, bottom_right_norm)
    if result is None:
        return None
    
    img_array, coords = result
    
    # 检测
    marked_path = os.path.join(output_dir, f"{name}_marked.png")
    detection_result = detect_and_mark_points(img_array, template_paths, confidence=confidence, output_path=marked_path)
    
    # 保存原始截图
    original_path = os.path.join(output_dir, f"{name}.png")
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(original_path, img_bgr)
    
    return {
        'original_path': original_path,
        'marked_path': marked_path,
        'coords': coords,
        'detections': detection_result['detections'] if detection_result else [],
        'detection_count': detection_result['count'] if detection_result else 0
    }


def capture_with_name(top_left_norm, bottom_right_norm, name, output_dir="screenshots"):
    """
    矩形区域截图，使用指定名称
    
    Args:
        top_left_norm: 左上角 (norm_x, norm_y)
        bottom_right_norm: 右下角 (norm_x, norm_y)
        name: 文件名（不含扩展名）
        output_dir: 输出目录
    
    Returns:
        dict: 截图结果信息
    """
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = f"{name}.png"
    filepath = os.path.join(output_dir, filename)
    
    result = capture_rectangle(top_left_norm, bottom_right_norm, save_path=filepath)
    if result:
        img_array, coords = result
        return {
            'image': img_array,
            'coords': coords,
            'filepath': filepath
        }
    return None


if __name__ == "__main__":
    # 第一个截图区域
    region1_top_left = (0.865, 0.08)
    region1_bottom_right = (0.985, 0.27)
    
    # 第二个截图区域
    region2_top_left = (0.92, 0.16)
    region2_bottom_right = (0.938, 0.19)
    
    # 模板路径
    template_paths = [
        r"D:\mingriHelper\collect\S2\images\point\point.png",
        r"D:\mingriHelper\collect\S2\images\point\point_2.png"
    ]
    
    print("3秒后开始截图...")
    time.sleep(3)
    
    # 截图、检测并连接
    print("\n截图、检测并连接...")
    result = capture_detect_and_connect(
        region1_top_left, region1_bottom_right,
        region2_top_left, region2_bottom_right,
        template_paths,
        confidence=0.5
    )
    
    if result:
        print(f"处理成功！")
        print(f"第一个区域坐标: {result['region1_coords']}")
        print(f"第二个区域坐标: {result['region2_coords']}")
        print(f"检测到的点: {result['detected_point']}")
        print(f"第二个区域中心: {result['region2_center']}")
        print(f"斜线角度: {result['angle']}°")
        print(f"原始截图: {result['original_path']}")
        print(f"连接线截图: {result['marked_path']}")
        print(f"mainPosition截图: {result['mainposition_path']}")
        
        # 调用tiqu模块分析第二个区域的箭头方向
        print("\n分析mainPosition区域的箭头方向...")
        import tiqu
        
        # 获取第二个区域的截图
        result2 = capture_rectangle(region2_top_left, region2_bottom_right)
        if result2:
            img2_array, coords2 = result2
            arrow_result = tiqu.get_arrow_direction(img2_array, save_marked=True)
            if arrow_result is not None:
                print(f"箭头朝向: {arrow_result['angle']}°")
                print(f"质心: {arrow_result['centroid']}")
                print(f"尖端: {arrow_result['tip']}")
                print(f"凹点: {arrow_result['notch']}")
                print(f"标记图像: {arrow_result['marked_path']}")
                
                # 获取连接线的角度（目标角度）
                target_angle = result['angle']
                current_arrow_angle = arrow_result['angle']
                
                print(f"\n视角对齐信息:")
                print(f"当前箭头朝向: {current_arrow_angle}°")
                print(f"目标方向（连接线角度）: {target_angle}°")
                
                # # 调用mouse_control模块对齐视角
                # print("\n开始调整视角...")
                # print("3秒后开始调整...")
                # time.sleep(3)
                
                align_result = mouse_control.align_arrow_to_target(
                    current_arrow_angle, 
                    target_angle, 
                    sensitivity=2.0,
                    max_iterations=5
                )
                
                if align_result['success']:
                    print(f"视角对齐成功！")
                else:
                    print(f"视角对齐未完成，剩余差异: {mouse_control.calculate_angle_difference(align_result['final_angle'], target_angle)[0]:.2f}°")
            else:
                print("未能检测到箭头")
    else:
        print("处理失败")
