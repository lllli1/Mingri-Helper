"""
测试tiqu.py模块集成到S2.py的功能
"""
import tiqu
import cv2
import os

# 创建测试输出目录
output_dir = "test_output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 测试1：验证tiqu模块函数可用性
print("="*50)
print("测试1：验证tiqu模块函数可用性")
print("="*50)
print(f"可用函数: {[x for x in dir(tiqu) if not x.startswith('_')]}")
print("[成功] tiqu模块导入成功")

# 测试2：读取测试图像
print("\n" + "="*50)
print("测试2：测试图像处理功能")
print("="*50)

# 检查是否有测试图像
test_image = "screenshots/mainPosition.png"
if os.path.exists(test_image):
    print(f"读取测试图像: {test_image}")
    img = cv2.imread(test_image)
    if img is not None:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print("[成功] 图像读取成功")
        
        # 测试get_arrow_direction函数
        print("\n测试get_arrow_direction函数...")
        arrow_result = tiqu.get_arrow_direction(img_rgb, process_scale=8, save_marked=True, output_dir=output_dir)
        if arrow_result:
            print("[成功] 箭头分析成功")
            print(f"  箭头朝向角度: {arrow_result['angle']}°")
            print(f"  箭头质心位置: {arrow_result['centroid']}")
            print(f"  箭头尖端位置: {arrow_result['tip']}")
            print(f"  箭头凹点位置: {arrow_result['notch']}")
            if arrow_result['marked_path']:
                print(f"  标记图像: {arrow_result['marked_path']}")
        else:
            print("[失败] 箭头分析失败")
        
        # 测试analyze_arrow_from_screenshot函数
        print("\n测试analyze_arrow_from_screenshot函数...")
        detailed_result = tiqu.analyze_arrow_from_screenshot(img_rgb, process_scale=8, 
                                                            output_path=os.path.join(output_dir, "detailed_analysis.png"))
        if detailed_result:
            print("[成功] 详细分析成功")
            print(f"  角度: {detailed_result['angle']}°")
            print(f"  质心: {detailed_result['centroid']}")
            print(f"  尖端: {detailed_result['tip']}")
            print(f"  凹点: {detailed_result['notch']}")
            print(f"  顶点数: {len(detailed_result['vertices'])}")
        else:
            print("[失败] 详细分析失败")
        
        # 测试get_arrow_direction_from_vertices函数
        print("\n测试get_arrow_direction_from_vertices函数...")
        if detailed_result and len(detailed_result['vertices']) >= 4:
            test_vertices = detailed_result['vertices'][:4]
            angle_test, tip_test, notch_test, centroid_test = tiqu.get_arrow_direction_from_vertices(test_vertices)
            print("[成功] 顶点测试成功")
            print(f"  角度: {angle_test}°")
            print(f"  尖端: {tip_test}")
            print(f"  凹点: {notch_test}")
            print(f"  质心: {centroid_test}")
        else:
            print("[失败] 顶点测试失败（顶点不足或分析失败）")
    else:
        print("[失败] 图像读取失败")
else:
    print(f"[失败] 测试图像不存在: {test_image}")
    print("  请先运行S2.py生成测试图像")

print("\n" + "="*50)
print("测试完成")
print("="*50)