import cv2
import numpy as np
import math


def get_arrow_direction_from_vertices(points):
    """
    从4个顶点中找出尖端(Tip)和凹点(Notch)，并计算方向
    坐标系：原点在质心，竖直向上是0度/360度，竖直向下是180度
    
    Args:
        points: 4个顶点坐标列表
    
    Returns:
        tuple: (角度, 尖端, 凹点, 质心)
    """
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


def get_arrow_direction(img_array, process_scale=8, save_marked=True, output_dir="screenshots"):
    """
    从截图中获取箭头朝向度数，并可选保存标记图像
    
    Args:
        img_array: 截图数组 (RGB格式)
        process_scale: 处理缩放倍数
        save_marked: 是否保存标记后的截图
        output_dir: 输出目录
    
    Returns:
        dict: 包含角度和保存路径的信息
    """
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    marked_path = None
    if save_marked:
        marked_path = os.path.join(output_dir, "arrow_analysis.png")
    
    result = analyze_arrow_from_screenshot(img_array, process_scale=process_scale, output_path=marked_path)
    if result:
        return {
            'angle': result['angle'],
            'marked_path': marked_path,
            'centroid': result['centroid'],
            'tip': result['tip'],
            'notch': result['notch']
        }
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
        cv2.circle(marked_img, (int(pt[0]), int(pt[1])), radius=2, color=(255, 0, 0), thickness=1)
    
    # 画质心 (黄色)
    cv2.circle(marked_img, (int(p_centroid[0]), int(p_centroid[1])), radius=3, color=(0, 255, 255), thickness=1)
    
    # 画凹点 (红色)
    cv2.circle(marked_img, (int(p_notch[0]), int(p_notch[1])), radius=3, color=(0, 0, 255), thickness=1)
    
    # 画尖端 (绿色)
    cv2.circle(marked_img, (int(p_tip[0]), int(p_tip[1])), radius=3, color=(0, 255, 0), thickness=1)
    
    # 画方向引导线
    cv2.arrowedLine(marked_img, (int(p_notch[0]), int(p_notch[1])), (int(p_tip[0]), int(p_tip[1])), 
                    color=(0, 255, 0), thickness=1, tipLength=0.15)
    
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


if __name__ == "__main__":
    # 示例：分析screenshots/mainPosition.png
    import os
    
    test_image = "screenshots/mainPosition.png"
    if os.path.exists(test_image):
        img = cv2.imread(test_image)
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = analyze_arrow_from_screenshot(img_rgb, output_path="screenshots/mainPosition_marked.png")
            if result:
                print(f"箭头朝向: {result['angle']}°")
        else:
            print(f"无法读取图像: {test_image}")
    else:
        print(f"测试图像不存在: {test_image}")
