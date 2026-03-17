import win32api
import win32con
import time
import math


def normalize_angle(angle):
    """
    将角度归一化到0-360范围
    
    Args:
        angle: 角度值
    
    Returns:
        float: 0-360范围内的角度
    """
    angle = angle % 360
    if angle < 0:
        angle += 360
    return angle


def calculate_angle_difference(current_angle, target_angle):
    """
    计算当前角度到目标角度的最短转动角度和方向
    
    Args:
        current_angle: 当前角度 (0-360)
        target_angle: 目标角度 (0-360)
    
    Returns:
        tuple: (角度差, 方向) 
               方向: 'left' 表示逆时针, 'right' 表示顺时针
    """
    current_angle = normalize_angle(current_angle)
    target_angle = normalize_angle(target_angle)
    
    # 计算两个方向的角度差
    diff_clockwise = (target_angle - current_angle) % 360
    diff_counter_clockwise = (current_angle - target_angle) % 360
    
    # 选择最短的转动方向
    if diff_clockwise <= diff_counter_clockwise:
        return diff_clockwise, 'right'  # 顺时针
    else:
        return diff_counter_clockwise, 'left'  # 逆时针


def move_mouse_relative(dx, dy, duration=0.1):
    """
    相对移动鼠标（使用mouse_event）
    
    Args:
        dx: X轴移动距离（正数向右，负数向左）
        dy: Y轴移动距离（正数向下，负数向上）
        duration: 移动持续时间（秒）
    """
    # 使用mouse_event进行相对移动
    # MOUSEEVENTF_MOVE = 0x0001
    win32api.mouse_event(0x0001, dx, dy, 0, 0)
    time.sleep(duration)


def adjust_view_angle(current_angle, target_angle, sensitivity=1.0, step_delay=0.05):
    """
    调整视角角度以对齐目标方向
    
    Args:
        current_angle: 当前箭头朝向角度 (0-360)
        target_angle: 目标角度 (0-360)
        sensitivity: 鼠标移动灵敏度（像素/度）
        step_delay: 每步移动的延迟（秒）
    
    Returns:
        dict: 包含调整过程信息
    """
    current_angle = normalize_angle(current_angle)
    target_angle = normalize_angle(target_angle)
    
    angle_diff, direction = calculate_angle_difference(current_angle, target_angle)
    
    if angle_diff < 1:  # 如果差异小于1度，认为已对齐
        print(f"已对齐！当前角度: {current_angle:.2f}°, 目标角度: {target_angle:.2f}°")
        return {
            'success': True,
            'current_angle': current_angle,
            'target_angle': target_angle,
            'angle_diff': angle_diff,
            'direction': direction,
            'steps': 0
        }
    
    # 计算需要移动的像素距离
    pixel_distance = int(angle_diff * sensitivity)
    
    if direction == 'left':
        # 向左滑动（逆时针）
        print(f"向左转动 {angle_diff:.2f}°...")
        move_mouse_relative(-pixel_distance, 0, duration=step_delay)
    else:
        # 向右滑动（顺时针）
        print(f"向右转动 {angle_diff:.2f}°...")
        move_mouse_relative(pixel_distance, 0, duration=step_delay)
    
    return {
        'success': True,
        'current_angle': current_angle,
        'target_angle': target_angle,
        'angle_diff': angle_diff,
        'direction': direction,
        'pixel_distance': pixel_distance,
        'steps': 1
    }


def align_arrow_to_target(arrow_angle, target_angle, sensitivity=1.0, max_iterations=10):
    """
    通过多次调整将箭头方向对齐到目标方向
    
    Args:
        arrow_angle: 当前箭头朝向角度 (0-360)
        target_angle: 目标角度 (0-360)
        sensitivity: 鼠标移动灵敏度（像素/度）
        max_iterations: 最大迭代次数
    
    Returns:
        dict: 包含对齐结果
    """
    print(f"\n开始对齐视角...")
    print(f"当前箭头朝向: {arrow_angle:.2f}°")
    print(f"目标方向: {target_angle:.2f}°")
    
    # 点按鼠标右键
    print("点按鼠标右键...")
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    time.sleep(0.3)  # 等待右键点击完成
    
    current_angle = normalize_angle(arrow_angle)
    iterations = 0
    total_adjustment = 0
    
    while iterations < max_iterations:
        angle_diff, direction = calculate_angle_difference(current_angle, target_angle)
        
        if angle_diff < 1:  # 对齐完成
            print(f"\n对齐完成！")
            print(f"最终角度: {current_angle:.2f}°")
            print(f"总调整: {total_adjustment:.2f}°")
            print(f"迭代次数: {iterations}")
            return {
                'success': True,
                'final_angle': current_angle,
                'target_angle': target_angle,
                'total_adjustment': total_adjustment,
                'iterations': iterations
            }
        
        # 执行一步调整
        result = adjust_view_angle(current_angle, target_angle, sensitivity=sensitivity)
        
        # 更新当前角度（这里假设调整成功）
        current_angle = normalize_angle(current_angle + (angle_diff if direction == 'right' else -angle_diff))
        total_adjustment += angle_diff
        iterations += 1
        
        time.sleep(0.1)  # 等待一下再进行下一次调整
    
    print(f"\n达到最大迭代次数，对齐未完成")
    print(f"最终角度: {current_angle:.2f}°")
    print(f"目标角度: {target_angle:.2f}°")
    print(f"剩余差异: {calculate_angle_difference(current_angle, target_angle)[0]:.2f}°")
    
    return {
        'success': False,
        'final_angle': current_angle,
        'target_angle': target_angle,
        'total_adjustment': total_adjustment,
        'iterations': iterations,
        'reason': 'max_iterations_reached'
    }


def getover(initial_arrow_angle, rotation_target=30, sensitivity=1.0, max_iterations=10, step_delay=0.05):
    """
    旋转指定度数（默认30度）
    
    Args:
        initial_arrow_angle: 初始箭头朝向角度 (0-360)
        rotation_target: 目标旋转度数（默认30度）
        sensitivity: 鼠标移动灵敏度（像素/度）
        max_iterations: 最大迭代次数
        step_delay: 每步移动的延迟（秒）
    
    Returns:
        dict: 包含旋转结果
    """
    print(f"\n开始旋转...")
    print(f"初始箭头方向: {initial_arrow_angle:.2f}°")
    print(f"目标旋转度数: {rotation_target}°")
    
    # 点按鼠标右键
    # print("点按鼠标右键...")
    # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    # time.sleep(0.1)
    # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    # time.sleep(0.3)  # 等待右键点击完成
    
    current_angle = normalize_angle(initial_arrow_angle)
    previous_angle = current_angle
    target_angle = normalize_angle(initial_arrow_angle + rotation_target)
    iterations = 0
    total_rotation = 0
    
    while iterations < max_iterations:
        # 计算当前旋转量（当前角度 - 初始角度）
        rotation_amount = normalize_angle(current_angle - initial_arrow_angle)
        
        # 如果旋转量接近目标旋转度数，认为成功
        if abs(rotation_amount - rotation_target) < 1 or abs(rotation_amount - (rotation_target - 360)) < 1:
            print(f"\n旋转完成！")
            print(f"初始角度: {initial_arrow_angle:.2f}°")
            print(f"最终角度: {current_angle:.2f}°")
            print(f"实际旋转: {rotation_amount:.2f}°")
            print(f"迭代次数: {iterations}")
            return {
                'success': True,
                'initial_angle': initial_arrow_angle,
                'final_angle': current_angle,
                'rotation_amount': rotation_amount,
                'target_rotation': rotation_target,
                'iterations': iterations
            }
        
        # 执行一步调整
        result = adjust_view_angle(current_angle, target_angle, sensitivity=sensitivity, step_delay=step_delay)
        
        # 更新当前角度
        angle_diff, direction = calculate_angle_difference(current_angle, target_angle)
        if direction == 'right':
            current_angle = normalize_angle(current_angle + angle_diff)
        else:
            current_angle = normalize_angle(current_angle - angle_diff)
        
        total_rotation += angle_diff
        iterations += 1
        
        print(f"[迭代 {iterations}] 当前角度: {current_angle:.2f}°, 已旋转: {normalize_angle(current_angle - initial_arrow_angle):.2f}°")
        
        time.sleep(0.1)  # 等待一下再进行下一次调整
    
    print(f"\n达到最大迭代次数，旋转未完成")
    print(f"初始角度: {initial_arrow_angle:.2f}°")
    print(f"最终角度: {current_angle:.2f}°")
    print(f"实际旋转: {normalize_angle(current_angle - initial_arrow_angle):.2f}°")
    print(f"目标旋转: {rotation_target}°")
    
    return {
        'success': False,
        'initial_angle': initial_arrow_angle,
        'final_angle': current_angle,
        'rotation_amount': normalize_angle(current_angle - initial_arrow_angle),
        'target_rotation': rotation_target,
        'iterations': iterations,
        'reason': 'max_iterations_reached'
    }


if __name__ == "__main__":
    # 测试示例
    print("鼠标控制模块测试")
    
    # 示例：将当前视角从45度调整到135度
    current = 45.0
    target = 135.0
    
    result = align_arrow_to_target(current, target, sensitivity=2.0)
    print(f"\n结果: {result}")
