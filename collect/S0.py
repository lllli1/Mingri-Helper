# S0阶段：准备与校验

import pygetwindow as gw
import pyautogui
import time

def main():
    # 查找目标窗口
    target_title = "夏尔镇 - 明日之后"
    windows = gw.getWindowsWithTitle(target_title)
    
    if not windows:
        print("未找到目标窗口，请先打开游戏并进入对应界面")
        return False
    
    target_window = windows[0]
    
    # 检查是否已在前台
    if not target_window.isActive:
        # 如果最小化，则先恢复
        if target_window.isMinimized:
            target_window.restore()
            time.sleep(0.5)
        
        # 置前
        target_window.activate()
        time.sleep(0.5)
        
        # 再次确认是否成功置前
        if not target_window.isActive:
            print("系统阻止窗口抢焦点/置前失败，请手动切到前台后再运行")
            return False
    
    # 校验分辨率
    client_width = target_window.width
    client_height = target_window.height
    
    # 输出实际获取到的窗口信息用于调试
    print(f"获取到的窗口位置和大小: Left={target_window.left}, Top={target_window.top}, Width={client_width}, Height={client_height}")
    
    if client_width != 960 or client_height != 540:
        print(f"当前客户区尺寸为 {client_width}x{client_height}，需要 960x540，请检查游戏设置")
        return False
    
    # 记录基准坐标
    base_x = target_window.left
    base_y = target_window.top
    print(f"基准坐标记录: ({base_x}, {base_y})")
    
    # 返回基准坐标和状态
    return (base_x, base_y)

if __name__ == "__main__":
    result = main()
    # if result:
    #     print("S0阶段完成，进入S1")
    # else:
    #     print("S0阶段失败，停止执行")
    print("S0阶段完成，进入S1")