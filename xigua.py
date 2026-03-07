import time
import keyboard
import sys
import argparse

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='模拟按键F的脚本，支持周期性Y+数字键组合')
    parser.add_argument('--press-time', type=float, default=0.5, help='按键持续时间（秒），默认0.5')
    parser.add_argument('--wait-time', type=float, default=3.0, help='等待时间（秒），默认3')
    parser.add_argument('--n1-threshold', type=int, default=10, help='N1阈值，决定何时从数字1切换到数字2，默认10')
    parser.add_argument('--cycle-trigger', type=int, default=500, help='每多少个循环触发Y+数字键组合，默认500')
    args = parser.parse_args()
    
    print(f"脚本开始运行...")
    print(f"配置：")
    print(f"  - 按键时长: {args.press_time}秒")
    print(f"  - 等待时长: {args.wait_time}秒")
    print(f"  - N1阈值: {args.n1_threshold}")
    print(f"  - 触发周期: 每{args.cycle_trigger}个循环")
    print("按 Ctrl+C 可以停止脚本")
    print("按 Esc 键也可以停止脚本")
    print("=" * 60)
    
    cycle_count = 0  # 主循环计数器
    n = 0  # Y+数字组合执行计数器
    N1 = args.n1_threshold  # 阈值常数
    
    # 注册退出热键
    keyboard.add_hotkey('esc', lambda: sys.exit("按Esc键退出"))
    
    def execute_y_number_combo():
        """执行Y+数字键组合的函数"""
        nonlocal n
        
        # 根据n和N1的关系决定按哪个数字键
        number_key = '1' if n < N1 else '2'
        
        print(f"\n{'='*60}")
        print(f"🎯 触发特殊操作 (n={n}, N1={N1})")
        print(f"   执行组合: Y + {number_key}")
        print(f"{'='*60}")
        
        # 按下Y键
        print("  [特殊] 按下Y键", end='', flush=True)
        keyboard.press('y')
        time.sleep(0.05)  # 短暂按下
        keyboard.release('y')
        print(" ✓")
        
        # 等待0.2秒
        print("  [特殊] 等待0.2秒", end='', flush=True)
        time.sleep(0.2)
        print(" ✓")
        
        # 按下数字键
        print(f"  [特殊] 按下数字键 {number_key}", end='', flush=True)
        keyboard.press(number_key)
        time.sleep(0.05)
        keyboard.release(number_key)
        print(" ✓")
        
        # n自增
        n += 1
        print(f"  [状态] n 已更新: {n-1} → {n}")
        
        # 显示下次将使用的数字键
        next_key = '1' if n < N1 else '2'
        print(f"  [预告] 下次将使用: Y + {next_key}")
        print(f"{'='*60}\n")
    
    try:
        while True:
            cycle_count += 1
            
            # 检查是否需要执行Y+数字组合
            if cycle_count % args.cycle_trigger == 0:
                execute_y_number_combo()
            
            print(f"第 {cycle_count:5d} 个循环开始 (距离下次特殊操作还有 {args.cycle_trigger - (cycle_count % args.cycle_trigger)} 个循环)")
            
            # 第一步：按F键
            print("  [步骤1] 按下F键", end='', flush=True)
            keyboard.press('f')
            for i in range(int(args.press_time * 10)):
                time.sleep(0.1)
                if i % 5 == 0:  # 每0.5秒打印一个点
                    print('.', end='', flush=True)
            keyboard.release('f')
            print(" 松开")
            
            # 等待
            print(f"  等待 {args.wait_time}秒", end='', flush=True)
            for i in range(int(args.wait_time)):
                time.sleep(1)
                print('.', end='', flush=True)
            print()
            
            # 第二步：再次按F键
            print("  [步骤2] 按下F键", end='', flush=True)
            keyboard.press('f')
            for i in range(int(args.press_time * 10)):
                time.sleep(0.1)
                if i % 5 == 0:
                    print('.', end='', flush=True)
            keyboard.release('f')
            print(" 松开")
            
            # 等待下一个循环
            print(f"  等待 {args.wait_time}秒后继续", end='', flush=True)
            for i in range(int(args.wait_time)):
                time.sleep(1)
                print('.', end='', flush=True)
            print()
            
            print(f"第 {cycle_count:5d} 个循环完成")
            print("-" * 60)
            
    except KeyboardInterrupt:
        print("\n\n脚本已停止")
        print(f"统计信息：")
        print(f"  - 总循环次数: {cycle_count}")
        print(f"  - Y+数字组合执行次数: {n}")
    except SystemExit as e:
        print(f"\n\n{e}")
        print(f"统计信息：")
        print(f"  - 总循环次数: {cycle_count}")
        print(f"  - Y+数字组合执行次数: {n}")
    finally:
        # 确保所有按键被释放
        keyboard.release('f')
        keyboard.release('y')
        keyboard.release('1')
        keyboard.release('2')
        sys.exit(0)

if __name__ == "__main__":
    # 检查是否安装了keyboard库
    try:
        import keyboard
    except ImportError:
        print("请先安装keyboard库：pip install keyboard")
        print("在Linux系统上可能需要sudo权限")
        sys.exit(1)
    
    # Windows系统可能需要管理员权限
    if sys.platform.startswith('win'):
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("提示：在Windows上，某些程序可能需要以管理员权限运行才能模拟按键")
    
    main()