import time
import win32api
import win32con
import cv2
import numpy as np
from screenshot import capture_rectangle
import tiqu


def test_mouse_movement_sensitivity(pixel_distance=1, split_moves=1, interval=0.1, screenshot_delay=1.0):
    """
    测试鼠标移动与角度变化的关系
    
    Args:
        pixel_distance: 鼠标移动的总像素距离
        split_moves: 分成多少次移动（1表示一次性移动）
        interval: 每次移动之间的间隔（秒）
        screenshot_delay: 移动后到截图的延迟（秒）
    """
    if split_moves == 1:
        test_name = f"一次性移动{pixel_distance}像素"
    else:
        test_name = f"分{split_moves}次移动，每次{pixel_distance//split_moves}像素，间隔{interval}秒"
    
    print(f"鼠标移动灵敏度测试: {test_name}")
    print(f"截图延迟: {screenshot_delay}秒")
    print("=" * 60)
    
    # 截图区域坐标
    region2_top_left = (0.92, 0.16)
    region2_bottom_right = (0.938, 0.19)
    
    print("\n3秒后开始测试...")
    time.sleep(3)
    
    # 第一次截图和检测
    print("\n[第1步] 检测初始箭头角度...")
    result1 = capture_rectangle(region2_top_left, region2_bottom_right)
    if not result1:
        print("截图失败")
        return
    
    img1_array, coords1 = result1
    arrow_result1 = tiqu.get_arrow_direction(img1_array, save_marked=False)
    
    if arrow_result1 is None:
        print("未能检测到箭头")
        return
    
    initial_angle = arrow_result1['angle']
    print(f"初始箭头角度: {initial_angle}°")
    
    # 点按鼠标右键
    # print("\n[第2步] 点按鼠标右键...")
    # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    # time.sleep(0.1)
    # win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    # time.sleep(0.5)
    
    # 移动鼠标
    print(f"\n[第3步] 执行鼠标移动...")
    pixel_per_move = pixel_distance // split_moves
    for i in range(split_moves):
        print(f"  移动 {i+1}/{split_moves}: 向右{pixel_per_move}像素")
        win32api.mouse_event(0x0001, pixel_per_move, 0, 0, 0)
        if i < split_moves - 1:
            time.sleep(interval)
    
    # 等待指定的延迟时间后再截图
    print(f"\n[第3.5步] 等待{screenshot_delay}秒让游戏更新视角...")
    time.sleep(screenshot_delay)
    
    # 第二次截图和检测
    print("\n[第4步] 检测拖动后的箭头角度...")
    result2 = capture_rectangle(region2_top_left, region2_bottom_right)
    if not result2:
        print("截图失败")
        return
    
    img2_array, coords2 = result2
    arrow_result2 = tiqu.get_arrow_direction(img2_array, save_marked=False)
    
    if arrow_result2 is None:
        print("未能检测到箭头")
        return
    
    final_angle = arrow_result2['angle']
    print(f"拖动后箭头角度: {final_angle}°")
    
    # 计算角度变化
    angle_diff = final_angle - initial_angle
    # 处理360度跨越的情况
    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff < -180:
        angle_diff += 360
    
    print("\n" + "=" * 60)
    print("测试结果:")
    print(f"初始角度: {initial_angle}°")
    print(f"最终角度: {final_angle}°")
    print(f"角度变化: {angle_diff}°")
    print(f"鼠标移动: {pixel_distance}像素 ({split_moves}次)")
    sensitivity = abs(angle_diff) / pixel_distance if pixel_distance > 0 else 0
    print(f"灵敏度: {sensitivity:.4f}°/像素")
    print("=" * 60)
    
    return {
        'test_name': test_name,
        'initial_angle': initial_angle,
        'final_angle': final_angle,
        'angle_diff': angle_diff,
        'pixel_moved': pixel_distance,
        'split_moves': split_moves,
        'screenshot_delay': screenshot_delay,
        'sensitivity': sensitivity
    }


if __name__ == "__main__":
    print("开始鼠标移动速度限制测试...\n")
    
    results = []
    screenshot_delay = 1.0  # 1秒延迟
    
    # 测试A：一次性移动100像素
    print("\n" + "="*60)
    print("测试A: 一次性移动100像素")
    print("="*60)
    result_a = test_mouse_movement_sensitivity(pixel_distance=100, split_moves=1, screenshot_delay=screenshot_delay)
    if result_a:
        results.append(result_a)
    
    time.sleep(2)
    
    # 测试B：分10次移动，每次10像素，间隔0.1秒
    print("\n" + "="*60)
    print("测试B: 分10次移动，每次10像素，间隔0.1秒")
    print("="*60)
    result_b = test_mouse_movement_sensitivity(pixel_distance=100, split_moves=10, interval=0.1, screenshot_delay=screenshot_delay)
    if result_b:
        results.append(result_b)
    
    time.sleep(2)
    
    # 测试C：分10次移动，每次10像素，间隔0.5秒
    print("\n" + "="*60)
    print("测试C: 分10次移动，每次10像素，间隔0.5秒")
    print("="*60)
    result_c = test_mouse_movement_sensitivity(pixel_distance=100, split_moves=10, interval=0.5, screenshot_delay=screenshot_delay)
    if result_c:
        results.append(result_c)
    
    # 汇总结果
    print(f"\n\n{'='*60}")
    print("汇总结果:")
    print(f"{'='*60}")
    for result in results:
        print(f"{result['test_name']}")
        print(f"  角度变化: {result['angle_diff']:6.2f}°")
        print(f"  灵敏度: {result['sensitivity']:.4f}°/像素")
        print()
    
    # 分析结果
    print("="*60)
    print("分析:")
    if len(results) >= 3:
        if abs(results[1]['angle_diff'] - results[0]['angle_diff']) > 5 or \
           abs(results[2]['angle_diff'] - results[0]['angle_diff']) > 5:
            print("✓ 游戏限制了鼠标移动速度")
            print("  分次移动的总角度变化明显大于一次性移动")
        else:
            print("✗ 游戏未限制鼠标移动速度")
            print("  所有测试的角度变化基本相同")
    print("="*60)
