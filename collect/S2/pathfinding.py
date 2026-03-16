import win32api
import win32con
import time


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


def pathfinding(duration=60, jump_interval=2.0):
    """
    寻路逻辑：持续按下W键，每2秒按下空格键
    
    Args:
        duration: 寻路持续时间（秒）
        jump_interval: 跳跃间隔（秒）
    
    Returns:
        dict: 包含寻路结果
    """
    print(f"\n开始寻路...")
    print(f"持续时间: {duration}秒")
    print(f"跳跃间隔: {jump_interval}秒")
    print("3秒后开始...")
    time.sleep(3)
    
    # W键的虚拟键码是0x57
    W_KEY = 0x57
    # 空格键的虚拟键码是0x20
    SPACE_KEY = 0x20
    
    print("持续按下W键，每2秒按下空格键...")
    
    # 持续按下W键
    hold_key(W_KEY)
    
    start_time = time.time()
    last_jump_time = start_time
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
            
            time.sleep(0.1)  # 小延迟避免CPU占用过高
    
    finally:
        # 释放W键
        release_key(W_KEY)
        print(f"\n寻路完成！")
        print(f"总耗时: {time.time() - start_time:.1f}秒")
        print(f"跳跃次数: {jump_count}")
    
    return {
        'success': True,
        'duration': time.time() - start_time,
        'jump_count': jump_count
    }


if __name__ == "__main__":
    print("寻路模块测试")
    print("=" * 60)
    
    # 测试：寻路30秒
    result = pathfinding(duration=30, jump_interval=2.0)
    print(f"\n结果: {result}")
