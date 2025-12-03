#!/usr/bin/env python3
"""
测试欧拉视频放大算法
"""

import sys
import numpy as np
from core import EulerianVideoMagnification

def test_algorithm():
    """测试算法是否正常工作"""

    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python test_algorithm.py <视频文件路径> [最大帧数]")
        print("示例: python test_algorithm.py input.mp4 100")
        sys.exit(1)

    video_path = sys.argv[1]
    max_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print(f"\n{'='*60}")
    print(f"测试欧拉视频放大算法")
    print(f"{'='*60}")
    print(f"输入视频: {video_path}")
    print(f"最大处理帧数: {max_frames}")
    print(f"{'='*60}\n")

    try:
        # 1. 初始化
        print("步骤 1/5: 初始化处理器...")
        evm = EulerianVideoMagnification(video_path, "test_output.mp4")

        # 2. 获取视频信息
        print("\n步骤 2/5: 获取视频信息...")
        evm.get_video_info()

        # 3. 加载视频帧
        print(f"\n步骤 3/5: 加载视频帧（最多{max_frames}帧）...")
        frames = evm.load_video(max_frames=max_frames)
        print(f"✅ 成功加载 {len(frames)} 帧")
        print(f"   帧形状: {frames.shape}")
        print(f"   数据类型: {frames.dtype}")
        print(f"   数值范围: [{frames.min():.3f}, {frames.max():.3f}]")

        # 4. 运动放大
        print("\n步骤 4/5: 应用运动放大...")
        print("   参数: 频率 0.8-1.5 Hz, 放大倍数 20x, 金字塔层数 4, 跳过顶层 2")

        processed_frames = evm.magnify_motion(
            frames,
            fps=evm.fps,
            freq_low=0.8,
            freq_high=1.5,
            amplification=20,
            levels=4,
            skip_levels_at_top=2
        )

        print(f"✅ 处理完成")
        print(f"   输出形状: {processed_frames.shape}")
        print(f"   数据类型: {processed_frames.dtype}")
        print(f"   数值范围: [{processed_frames.min():.3f}, {processed_frames.max():.3f}]")

        # 5. 检查是否有变化
        print("\n步骤 5/5: 验证处理效果...")
        diff = np.abs(processed_frames - frames)
        mean_diff = diff.mean()
        max_diff = diff.max()

        print(f"   平均差异: {mean_diff:.6f}")
        print(f"   最大差异: {max_diff:.6f}")

        if mean_diff > 0.001:
            print(f"\n✅ 算法正常工作！检测到明显的运动放大效果")
            print(f"   建议: 可以继续保存视频")
        else:
            print(f"\n❌ 警告：处理前后几乎没有变化")
            print(f"   可能原因：")
            print(f"   1. 视频中没有目标频率范围的运动")
            print(f"   2. 放大倍数太小")
            print(f"   3. 算法参数需要调整")

        # 6. 保存视频（可选）
        save = input("\n是否保存处理后的视频？(y/n): ").strip().lower()
        if save == 'y':
            print("\n保存视频...")
            evm.save_video_from_frames(
                processed_frames,
                audio_source=None,
                output_format='mp4',
                mode='motion',
                freq_low=0.8,
                freq_high=1.5,
                amplification=20
            )
            print("✅ 视频已保存")

        print(f"\n{'='*60}")
        print("测试完成！")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_algorithm()
