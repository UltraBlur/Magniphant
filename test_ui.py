#!/usr/bin/env python3
"""
Simple UI test to diagnose startup issues
"""

import sys
import os

print("Step 1: Starting test...")

try:
    print("Step 2: Importing PyQt5...")
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    print("Step 3: PyQt5 imported successfully")

    print("Step 4: Creating QApplication...")
    app = QApplication(sys.argv)
    print("Step 5: QApplication created")

    print("Step 6: Creating main window...")
    window = QMainWindow()
    window.setWindowTitle("EVM Test")
    window.setGeometry(100, 100, 300, 200)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    layout = QVBoxLayout(central_widget)
    label = QLabel("EVM UI Test - 如果你看到这个，说明PyQt5工作正常")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    print("Step 7: Showing window...")
    window.show()

    print("Step 8: Starting event loop...")
    # 不使用 exec_() 避免阻塞，只显示窗口
    app.processEvents()
    print("Step 9: UI test completed successfully!")

except Exception as e:
    print(f"Error at step: {e}")
    import traceback
    traceback.print_exc()