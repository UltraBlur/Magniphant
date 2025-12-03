#!/usr/bin/env python3
"""
Eulerian Video Magnification - Main Entry Point
欧拉视频放大 - 主程序入口
"""

import sys
import argparse
import numpy as np


def run_gui():
    """运行图形界面"""
    try:
        from ui import EVMMainWindow
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QPalette, QColor
        import os

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        # 设置深色主题
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(40, 40, 46))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(31, 31, 31))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 46))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(40, 40, 46))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(100, 200, 255))
        palette.setColor(QPalette.Highlight, QColor(100, 200, 255))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        app.setPalette(palette)

        window = EVMMainWindow()
        window.show()

        sys.exit(app.exec_())
    except ImportError:
        print("错误: 未安装PyQt5，无法启动图形界面")
        print("请运行: pip install PyQt5")
        print("或使用命令行模式: python main.py input.mp4 -o output.mp4")
        sys.exit(1)


def run_cli(args):
    """运行命令行模式"""
    from core import EulerianVideoMagnification

    evm = EulerianVideoMagnification(args.input, args.output)
    evm.get_video_info()

    # 加载视频帧
    frames = evm.load_video(max_frames=args.max_frames)
    original_frames = frames.copy()

    # 处理视频
    if args.mode == 'motion':
        processed_frames = evm.magnify_motion(
            frames, evm.fps,
            freq_low=args.freq_low,
            freq_high=args.freq_high,
            amplification=args.amplification,
            levels=args.levels,
            skip_levels_at_top=args.skip_levels
        )
    elif args.mode == 'color':
        processed_frames = evm.magnify_color(
            frames, evm.fps,
            freq_low=args.freq_low,
            freq_high=args.freq_high,
            amplification=args.amplification,
            levels=args.levels,
            skip_levels_at_top=args.skip_levels
        )
    else:  # hybrid
        print("\n=== 混合模式 ===")
        motion_frames = evm.magnify_motion(
            frames, evm.fps,
            freq_low=args.freq_low,
            freq_high=args.freq_high,
            amplification=args.amplification * 0.7,
            levels=args.levels,
            skip_levels_at_top=args.skip_levels
        )
        processed_frames = evm.magnify_color(
            motion_frames, evm.fps,
            freq_low=args.freq_low,
            freq_high=args.freq_high,
            amplification=args.amplification * 1.5,
            levels=args.levels,
            skip_levels_at_top=args.skip_levels
        )

    # 混合处理
    if args.blend < 1.0:
        print(f"\n混合原始视频，比例: {args.blend}")
        processed_frames = processed_frames * args.blend + original_frames * (1 - args.blend)
        processed_frames = np.clip(processed_frames, 0, 1)

    # 保存视频
    audio_source = args.input if args.keep_audio else None
    evm.save_video_from_frames(
        processed_frames,
        audio_source=audio_source,
        output_format='mp4',
        mode=args.mode,
        freq_low=args.freq_low,
        freq_high=args.freq_high,
        amplification=args.amplification
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='欧拉视频放大 - VideoArt创作工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 启动图形界面
  python main.py

  # 命令行模式 - 运动放大（心跳检测）
  python main.py input.mp4 -o output.mp4 -m motion -a 20 -fl 0.8 -fh 1.5 -l 4 -s 2

  # 命令行模式 - 色彩放大
  python main.py input.mp4 -o output.mp4 -m color -a 50 -fl 0.5 -fh 3.0 -l 4 -s 2
        """
    )

    parser.add_argument('input', nargs='?', help='输入视频路径')
    parser.add_argument('-o', '--output', default='output.mp4', help='输出视频路径')
    parser.add_argument('-m', '--mode', choices=['motion', 'color', 'hybrid'],
                       default='motion', help='处理模式')
    parser.add_argument('-a', '--amplification', type=float, default=10,
                       help='放大倍数')
    parser.add_argument('-fl', '--freq-low', type=float, default=0.4,
                       help='低频截止 (Hz)')
    parser.add_argument('-fh', '--freq-high', type=float, default=3.0,
                       help='高频截止 (Hz)')
    parser.add_argument('-l', '--levels', type=int, default=4,
                       help='金字塔层数')
    parser.add_argument('-s', '--skip-levels', type=int, default=2,
                       help='跳过金字塔顶层数量（减少噪声）')
    parser.add_argument('-f', '--max-frames', type=int, default=None,
                       help='最大处理帧数（用于测试）')
    parser.add_argument('--keep-audio', action='store_true',
                       help='保留原视频音频')
    parser.add_argument('--blend', type=float, default=1.0,
                       help='与原视频混合比例 (0-1)')

    args = parser.parse_args()

    if args.input:
        # 命令行模式
        run_cli(args)
    else:
        # 图形界面模式
        run_gui()


if __name__ == "__main__":
    main()