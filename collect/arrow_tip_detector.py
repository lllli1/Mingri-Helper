import cv2
import numpy as np

def detect_arrow_body(arrow_image_path):
    """
    检测箭头本体并返回外接矩形
    参数:
        arrow_image_path: 箭头图像路径
    返回:
        (x, y, w, h) 矩形坐标和宽高，或 None
    """
    # 读取箭头图像
    arrow = cv2.imread(arrow_image_path)
    if arrow is None:
        print(f"无法加载图像: {arrow_image_path}")
        return None

    # 转换为灰度图
    gray = cv2.cvtColor(arrow, cv2.COLOR_BGR2GRAY)
    
    # 使用自适应阈值处理
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # 如果自适应阈值效果不好，尝试普通阈值
    if cv2.countNonZero(binary) == 0:
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # 找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print("未找到轮廓")
        return None

    # 获取最大轮廓（箭头本体）
    largest_contour = max(contours, key=cv2.contourArea)

    # 获取外接矩形
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    return x, y, w, h


def get_arrow_tip(arrow_image_path):
    """
    检测箭头尖端位置 - 找所有直线对的交点，选择最接近图像中心的有效交点
    参数:
        arrow_image_path: 箭头图像路径
    返回:
        (tip_x, tip_y) 尖端坐标，或 None
    """
    # 读取箭头图像
    arrow = cv2.imread(arrow_image_path, cv2.IMREAD_GRAYSCALE)
    if arrow is None:
        return None
    
    # 边缘检测
    edges = cv2.Canny(arrow, 30, 100)
    
    # 霍夫直线检测
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 5, minLineLength=3, maxLineGap=2)
    
    if lines is None or len(lines) < 2:
        return None
    
    # 计算每条直线的信息
    line_data = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        line_data.append({
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'length': length
        })
    
    # 按长度排序
    line_data.sort(key=lambda x: x['length'], reverse=True)
    
    # 计算两条直线的交点
    def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        
        return int(x), int(y)
    
    # 尝试所有直线对，找最接近图像中心的交点
    best_intersection = None
    best_distance = float('inf')
    
    image_center_x, image_center_y = 12, 12
    
    for i in range(len(line_data)):
        for j in range(i + 1, len(line_data)):
            line1 = line_data[i]
            line2 = line_data[j]
            
            # 尝试4种方向组合
            for reverse1 in [False, True]:
                for reverse2 in [False, True]:
                    if reverse1:
                        x1, y1, x2, y2 = line1['x2'], line1['y2'], line1['x1'], line1['y1']
                    else:
                        x1, y1, x2, y2 = line1['x1'], line1['y1'], line1['x2'], line1['y2']
                    
                    if reverse2:
                        x3, y3, x4, y4 = line2['x2'], line2['y2'], line2['x1'], line2['y1']
                    else:
                        x3, y3, x4, y4 = line2['x1'], line2['y1'], line2['x2'], line2['y2']
                    
                    p = line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)
                    
                    if p:
                        px, py = p
                        # 检查交点是否在图像范围内
                        if 0 <= px < 24 and 0 <= py < 24:
                            # 计算到图像中心的距离
                            dist = np.sqrt((px - image_center_x)**2 + (py - image_center_y)**2)
                            
                            if dist < best_distance:
                                best_distance = dist
                                best_intersection = p
    
    return best_intersection


def visualize_arrow_body(arrow_image_path, output_path='arrow_body_marked.png'):
    """
    可视化箭头本体检测结果，绘制外接矩形和中心到尖端的连线
    """
    result = detect_arrow_body(arrow_image_path)
    if result is None:
        return

    x, y, w, h = result
    
    # 读取原始图像用于绘制
    arrow_img = cv2.imread(arrow_image_path)
    if arrow_img is None:
        return

    # 计算中心点
    center_x = x + w // 2
    center_y = y + h // 2

    # 获取尖端
    tip = get_arrow_tip(arrow_image_path)
    
    # 绘制外接矩形
    cv2.rectangle(arrow_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # 绘制中心点
    cv2.circle(arrow_img, (center_x, center_y), 3, (0, 255, 0), -1)
    
    # 如果找到尖端，绘制连线
    if tip:
        tip_x, tip_y = tip
        cv2.line(arrow_img, (center_x, center_y), (tip_x, tip_y), (0, 0, 255), 1)
        cv2.circle(arrow_img, (tip_x, tip_y), 3, (0, 0, 255), -1)
    
    # 保存结果
    cv2.imwrite(output_path, arrow_img)


if __name__ == "__main__":
    arrow_path = r'D:\mingriHelper\collect\images\arrow\arrow_ico.png'
    result = detect_arrow_body(arrow_path)
    
    if result:
        x, y, w, h = result
        print(f"箭头本体位置: x={x}, y={y}, w={w}, h={h}")
        
        # 可视化
        visualize_arrow_body(arrow_path)
    else:
        print("检测失败")
