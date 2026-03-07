import pyautogui
import json
import time
from datetime import datetime
import keyboard

def main():
    results = []
    print("按键鼠标追踪器已启动 (按Ctrl+C退出)")
    print("请确保目标窗口在前台，按下Y键记录当前鼠标位置...")
    
    try:
        while True:
            # 检测Y键是否被按下
            import keyboard
            if keyboard.is_pressed('y'):
                # 等待按键释放避免重复触发
                while keyboard.is_pressed('y'):
                    time.sleep(0.01)
                
                mouse_x, mouse_y = pyautogui.position()
                
                # 查找目标窗口
                import pygetwindow as gw
                target_title = "夏尔镇 - 明日之后"
                windows = gw.getWindowsWithTitle(target_title)

                if not windows:
                    print("未找到目标窗口")
                    continue
                
                target_window = windows[0]
                window_left = target_window.left
                window_top = target_window.top
                window_width = target_window.width
                window_height = target_window.height
                
                # 计算偏移量
                offset_x = mouse_x - window_left
                offset_y = mouse_y - window_top
                
                # 计算归一化偏移量
                normalized_x = offset_x / window_width
                normalized_y = offset_y / window_height
                
                # 记录结果
                result = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mouse_position": {"x": mouse_x, "y": mouse_y},
                    "window_rect": {
                        "left": window_left,
                        "top": window_top,
                        "width": window_width,
                        "height": window_height
                    },
                    "offset": {"x": offset_x, "y": offset_y},
                    "normalized_offset": {"x": round(normalized_x, 6), "y": round(normalized_y, 6)}
                }
                
                results.append(result)
                
                # 实时输出
                print(f"\n[Y键记录] 时间: {result['timestamp']}")
                print(f"鼠标位置: ({mouse_x}, {mouse_y})")
                print(f"偏移量: ({offset_x}, {offset_y})")
                print(f"归一化偏移: ({normalized_x:.6f}, {normalized_y:.6f})")
                
                # 每5次保存一次到文件
                if len(results) % 5 == 0:
                    with open('mouse_tracking_results.json', 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"已保存 {len(results)} 条记录到 mouse_tracking_results.json")
                
                # 防抖
                time.sleep(0.3)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        # 退出时保存所有结果
        with open('mouse_tracking_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n程序已退出，共记录 {len(results)} 次点击，结果已保存到 mouse_tracking_results.json")

if __name__ == "__main__":
    main()