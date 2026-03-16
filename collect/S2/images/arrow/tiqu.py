import cv2
import numpy as np
import math

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
    # ================= 1. 高精度提取顶点 =================
    orig_img = cv2.imread(image_path)
    if orig_img is None:
        print(f"未能读取图片 '{image_path}'")
        return

    h, w = orig_img.shape[:2]
    high_res_img = cv2.resize(orig_img, (w * process_scale, h * process_scale), interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(high_res_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("未找到轮廓！")
        return
        
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

    cv2.imshow("Arrow Direction Analysis", upscaled_view)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    analyze_arrow_image("arrow_ico2.png", process_scale=8, view_scale=6) # view_scale调大到了6，看得更清楚