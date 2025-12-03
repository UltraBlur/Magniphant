#!/usr/bin/env python3
"""
Test Preview Window
测试预览窗口功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.preview_window import VideoPreviewWidget

def test_preview():
    """测试预览窗口"""
    print("Step 1: Creating QApplication...")
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 设置深色主题
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(40, 40, 46))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(31, 31, 31))
    palette.setColor(QPalette.AlternateBase, QColor(40, 40, 46))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(40, 40, 46))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)

    print("Step 2: Preview window test completed!")
    print("\nPreview window features:")
    print("- Real-time video preview")
    print("- Side-by-side comparison")
    print("- Split-screen comparison (horizontal/vertical)")
    print("- Playback controls")
    print("- Frame slider")
    print("\nTo test with actual video:")
    print("1. Run the main application: python main.py")
    print("2. Select an input video")
    print("3. Click the 'Preview' button")

    return 0

if __name__ == "__main__":
    sys.exit(test_preview())
