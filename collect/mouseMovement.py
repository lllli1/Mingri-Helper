import win32api
import win32con
import time
import keyboard

def turn_camera_win32(dx, dy):
    """
    直接向操作系统底层发送鼠标的相对物理移动信号。
    dx: 水平移动量 (正数向右转，负数向左转)
    dy: 垂直移动量 (正数向下看，负数向上看)
    """
    # MOUSEEVENTF_MOVE 代表这是一个相对移动指令，而非绝对坐标跳转
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

def test_mouse_movement():
    """
    使用 Win32 API mouse_event 进行鼠标转向测试
    按C键可随时退出
    """
    print("\n开始鼠标自动测试模式 (使用 Win32 API)")
    print("按C键可随时退出\n")
    print("将在3秒后开始测试...")
    time.sleep(3)
    
    print("\n初始化完成，开始测试\n")
    test_angle = 0
    
    # 测试1: 向左移动100像素（逆时针）
    print("测试1: 向左移动100像素（逆时针转动）")
    for i in range(100):
        if keyboard.is_pressed('c'):
            print("\n已按下C键，退出脚本")
            return
        turn_camera_win32(-1, 0)  # 向左移动1像素
        test_angle += 1
        if i % 10 == 0:
            print(f"  已移动 {i}px, 当前角度: {test_angle:.2f}°")
        time.sleep(0.01)
    time.sleep(1)
    
    # 测试2: 向右移动200像素（顺时针）
    print("\n测试2: 向右移动200像素（顺时针转动）")
    for i in range(200):
        if keyboard.is_pressed('c'):
            print("\n已按下C键，退出脚本")
            return
        turn_camera_win32(1, 0)  # 向右移动1像素
        test_angle -= 1
        if i % 10 == 0:
            print(f"  已移动 {i}px, 当前角度: {test_angle:.2f}°")
        time.sleep(0.01)
    time.sleep(1)
    
    # 测试3: 向左移动100像素回到初始位置
    print("\n测试3: 向左移动100像素（回到初始位置）")
    for i in range(100):
        if keyboard.is_pressed('c'):
            print("\n已按下C键，退出脚本")
            return
        turn_camera_win32(-1, 0)  # 向左移动1像素
        test_angle += 1
        if i % 10 == 0:
            print(f"  已移动 {i}px, 当前角度: {test_angle:.2f}°")
        time.sleep(0.01)
    
    # 归一化最终角度
    while test_angle > 180:
        test_angle -= 360
    while test_angle <= -180:
        test_angle += 360
    
    print(f"\n鼠标自动测试完成，最终角度: {test_angle:.2f}°")


if __name__ == "__main__":
    test_mouse_movement()
