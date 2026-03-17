import win32api
import win32con
import time
import cv2
import numpy as np
from screenshot import capture_rectangle


def press_key(key_code, duration=0.1):
    """
    按下并释放一个键
    
    Args:
        key_code: 虚拟键码
        duration: 按键持续时间（秒）
    """
    win32api.keybd_event(key_code, 0, 0, 0)
    time.sleep(duration)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def hold_key(key_code):
    """
    持续按下一个键（不释放）
    
    Args:
        key_code: 虚拟键码
    """
    win32api.keybd_event(key_code, 0, 0, 0)


def release_key(key_code):
    """
    释放一个键
    
    Args:
        key_code: 虚拟键码
    """
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def calculate_image_difference(img1, img2):
    """
    计算两张图片的差异程度
    
    Args:
        img1: 第一张图片数组
        img2: 第二张图片数组
    
    Returns:
        float: 差异程度（0-1，0表示完全相同，1表示完全不同）
    """
    if img1 is None or img2 is None:
        return 0
    
    # 确保两张图片大小相同
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # 计算差异
    diff = cv2.absdiff(img1, img2)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    
    # 计算差异百分比
    total_pixels = gray_diff.size
    changed_pixels = np.count_nonzero(gray_diff > 30)
    
    difference_ratio = changed_pixels / total_pixels
    return difference_ratio


def detect_stuck(region_top_left, region_bottom_right, check_duration=4.0, threshold=0.05):
    """
    检测角色是否卡住
    
    Args:
        region_top_left: 检测区域左上角
        region_bottom_right: 检测区域右下角
        check_duration: 检测时长（秒）
        threshold: 变化阈值（0-1，低于此值认为卡住）
    
    Returns:
        dict: 包含检测结果
    """
    print(f"\n开始检测是否卡住...")
    print(f"检测时长: {check_duration}秒")
    print(f"变化阈值: {threshold}")
    
    # 获取初始截图
    print("获取初始截图...")
    result1 = capture_rectangle(region_top_left, region_bottom_right)
    if not result1:
        print("初始截图失败")
        return {
            'success': False,
            'is_stuck': False,
            'reason': 'initial_capture_failed'
        }
    
    img1, coords1 = result1
    
    # 等待指定时间
    print(f"等待{check_duration}秒...")
    time.sleep(check_duration)
    
    # 获取最终截图
    print("获取最终截图...")
    result2 = capture_rectangle(region_top_left, region_bottom_right)
    if not result2:
        print("最终截图失败")
        return {
            'success': False,
            'is_stuck': False,
            'reason': 'final_capture_failed'
        }
    
    img2, coords2 = result2
    
    # 计算差异
    difference = calculate_image_difference(img1, img2)
    
    print(f"\n检测结果:")
    print(f"图片变化程度: {difference:.4f}")
    print(f"变化阈值: {threshold}")
    
    is_stuck = difference < threshold
    
    if is_stuck:
        print("✓ 检测到卡住！")
    else:
        print("✗ 未检测到卡住")
    
    return {
        'success': True,
        'is_stuck': is_stuck,
        'difference': difference,
        'threshold': threshold
    }


def pathfinding(duration=60, jump_interval=1.0, region_top_left=(0.865, 0.08), region_bottom_right=(0.985, 0.27), stuck_check_interval=4.0, stuck_threshold=0.05):
    """
    寻路逻辑：持续按下W键，每1秒按下空格键，定期检查是否卡住
    
    Args:
        duration: 寻路持续时间（秒）
        jump_interval: 跳跃间隔（秒）
        region_top_left: 卡住检测区域左上角
        region_bottom_right: 卡住检测区域右下角
        stuck_check_interval: 卡住检测间隔（秒）
        stuck_threshold: 卡住判定阈值
    
    Returns:
        dict: 包含寻路结果
    """
    print(f"\n开始寻路...")
    print(f"持续时间: {duration}秒")
    print(f"跳跃间隔: {jump_interval}秒")
    print(f"卡住检测间隔: {stuck_check_interval}秒")
    print("3秒后开始...")
    time.sleep(3)
    
    # W键的虚拟键码是0x57
    W_KEY = 0x57
    # 空格键的虚拟键码是0x20
    SPACE_KEY = 0x20
    
    print("持续按下W键，每1秒按下空格键...")
    
    # 持续按下W键
    hold_key(W_KEY)
    
    start_time = time.time()
    last_jump_time = start_time
    last_stuck_check_time = start_time
    jump_count = 0
    
    try:
        while time.time() - start_time < duration:
            current_time = time.time()
            
            # 每jump_interval秒按下一次空格键
            if current_time - last_jump_time >= jump_interval:
                print(f"[{current_time - start_time:.1f}s] 按下空格键 (第{jump_count + 1}次)")
                press_key(SPACE_KEY, duration=0.1)
                last_jump_time = current_time
                jump_count += 1
            
            # 每stuck_check_interval秒检查一次是否卡住
            if current_time - last_stuck_check_time >= stuck_check_interval:
                print(f"\n[{current_time - start_time:.1f}s] 检查是否卡住...")
                stuck_result = detect_stuck(region_top_left, region_bottom_right, check_duration=0.5, threshold=stuck_threshold)
                
                if stuck_result['success'] and stuck_result['is_stuck']:
                    print(f"\n✓ 卡住了！")
                    return {
                        'success': True,
                        'is_stuck': True,
                        'duration': time.time() - start_time,
                        'jump_count': jump_count,
                        'stuck_at': time.time() - start_time
                    }
                
                last_stuck_check_time = current_time
            
            time.sleep(0.1)  # 小延迟避免CPU占用过高
    
    finally:
        # 释放W键
        release_key(W_KEY)
        print(f"\n寻路完成！")
        print(f"总耗时: {time.time() - start_time:.1f}秒")
        print(f"跳跃次数: {jump_count}")
    
    return {
        'success': True,
        'is_stuck': False,
        'duration': time.time() - start_time,
        'jump_count': jump_count
    }


if __name__ == "__main__":
    print("寻路模块测试")
    print("=" * 60)
    
    # 测试：寻路60秒，每1秒跳跃一次，每4秒检查一次是否卡住
    region_top_left = (0.865, 0.08)
    region_bottom_right = (0.985, 0.27)
    
    result = pathfinding(
        duration=60, 
        jump_interval=1.0,
        region_top_left=region_top_left,
        region_bottom_right=region_bottom_right,
        stuck_check_interval=4.0,
        stuck_threshold=0.05
    )
    print(f"\n结果: {result}")
