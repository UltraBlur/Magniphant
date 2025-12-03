#!/usr/bin/env python3
"""
Integrated Preview Component
集成预览组件 - 嵌入式设计
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import EulerianVideoMagnification


class IntegratedPreviewWidget(QWidget):
    """集成预览组件 - 嵌入主窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_path = None
        self.params = None
        self.cap = None
        self.original_frames = []
        self.processed_frames = []
        self.current_frame_idx = 0
        self.is_playing = False
        self.fps = 30
        self.total_frames = 0
        self.preview_size = (640, 480)
        self.max_preview_frames = 120
        self.is_loaded = False

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 视频显示区域
        video_container = QHBoxLayout()
        video_container.setSpacing(15)

        # 原始视频
        original_layout = QVBoxLayout()
        original_layout.setSpacing(5)
        original_title = QLabel("原始")
        original_title.setStyleSheet("color: rgb(160, 160, 160); font-size: 12px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        original_title.setAlignment(Qt.AlignCenter)
        original_layout.addWidget(original_title)

        self.original_label = QLabel()
        self.original_label.setMinimumSize(640, 360)
        self.original_label.setStyleSheet("background-color: rgb(20, 20, 20); border: 2px solid rgb(60, 60, 60); border-radius: 4px;")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setScaledContents(False)
        from PyQt5.QtWidgets import QSizePolicy
        self.original_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        original_layout.addWidget(self.original_label)

        video_container.addLayout(original_layout)

        # 处理后视频
        processed_layout = QVBoxLayout()
        processed_layout.setSpacing(5)
        processed_title = QLabel("处理后")
        processed_title.setStyleSheet("color: rgb(160, 160, 160); font-size: 12px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        processed_title.setAlignment(Qt.AlignCenter)
        processed_layout.addWidget(processed_title)

        self.processed_label = QLabel()
        self.processed_label.setMinimumSize(640, 360)
        self.processed_label.setStyleSheet("background-color: rgb(20, 20, 20); border: 2px solid rgb(60, 60, 60); border-radius: 4px;")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setScaledContents(False)
        from PyQt5.QtWidgets import QSizePolicy
        self.processed_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        processed_layout.addWidget(self.processed_label)

        video_container.addLayout(processed_layout)

        main_layout.addLayout(video_container)

        # 控制区域
        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)

        # 进度条
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(100)
        self.frame_slider.setValue(0)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)
        self.frame_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid rgb(80, 80, 80);
                height: 8px;
                background: rgb(35, 35, 40);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: rgb(80, 120, 180);
                border: 2px solid rgb(100, 140, 200);
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        control_layout.addWidget(self.frame_slider)

        # 控制按钮行
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.play_btn = QPushButton("播放")
        self.play_btn.setFixedSize(80, 32)
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        button_layout.addWidget(self.play_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedSize(80, 32)
        self.reset_btn.clicked.connect(self.reset_preview)
        self.reset_btn.setEnabled(False)
        button_layout.addWidget(self.reset_btn)

        # 对比模式
        mode_label = QLabel("对比:")
        mode_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        button_layout.addWidget(mode_label)

        self.compare_mode = QComboBox()
        self.compare_mode.addItems(["并排", "左右分屏", "上下分屏"])
        self.compare_mode.currentIndexChanged.connect(self.update_display)
        self.compare_mode.setFixedHeight(32)
        button_layout.addWidget(self.compare_mode)

        button_layout.addStretch()

        # 帧信息
        self.frame_info_label = QLabel("帧: 0 / 0")
        self.frame_info_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 12px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        button_layout.addWidget(self.frame_info_label)

        control_layout.addLayout(button_layout)

        # 状态标签
        self.status_label = QLabel("等待加载视频")
        self.status_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 12px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        self.status_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.status_label)

        main_layout.addLayout(control_layout)

        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.next_frame)

        # 应用按钮样式
        button_style = """
            QPushButton {
                background-color: rgb(45, 45, 50);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 120, 180);
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QPushButton:hover {
                background-color: rgb(60, 60, 65);
                border-color: rgb(100, 140, 200);
            }
            QPushButton:pressed {
                background-color: rgb(35, 35, 40);
            }
            QPushButton:disabled {
                background-color: rgb(30, 30, 30);
                color: rgb(80, 80, 80);
                border-color: rgb(50, 50, 50);
            }
        """
        self.play_btn.setStyleSheet(button_style)
        self.reset_btn.setStyleSheet(button_style)

        combo_style = """
            QComboBox {
                background-color: rgb(45, 45, 50);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 80, 80);
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QComboBox:hover {
                border-color: rgb(100, 140, 200);
            }
            QComboBox QAbstractItemView {
                background-color: rgb(45, 45, 50);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 80, 80);
                selection-background-color: rgb(80, 120, 180);
            }
        """
        self.compare_mode.setStyleSheet(combo_style)

    def load_and_process(self, video_path, params):
        """加载并处理视频"""
        self.video_path = video_path
        self.params = params
        self.is_loaded = False

        # 重置状态
        self.stop_playback()
        self.original_frames = []
        self.processed_frames = []
        self.current_frame_idx = 0

        try:
            self.status_label.setText("加载视频中...")
            self.status_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 12px;")

            # 加载视频帧
            self.cap = cv2.VideoCapture(video_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.total_frames = min(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), self.max_preview_frames)

            frame_count = 0
            while frame_count < self.total_frames:
                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]
                scale = min(self.preview_size[0] / w, self.preview_size[1] / h)
                new_w, new_h = int(w * scale), int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                self.original_frames.append(frame)
                frame_count += 1

                if frame_count % 10 == 0:
                    self.status_label.setText(f"加载: {frame_count}/{self.total_frames}")

            self.cap.release()

            # 处理帧
            self.status_label.setText("处理视频中...")
            self.process_frames()

            # 更新UI
            self.frame_slider.setMaximum(self.total_frames - 1)
            self.play_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)
            self.is_loaded = True

            self.update_display()
            self.status_label.setText("就绪")
            self.status_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 12px;")

        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
            self.status_label.setStyleSheet("color: rgb(200, 100, 100); font-size: 12px;")
            self.is_loaded = False

    def process_frames(self):
        """处理视频帧"""
        try:
            frames_array = np.array(self.original_frames, dtype=np.float32) / 255.0

            evm = EulerianVideoMagnification(self.video_path)
            evm.fps = self.fps

            mode = self.params.get('mode', 'motion')

            if mode == 'motion':
                processed = evm.magnify_motion(
                    frames_array, self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10),
                    levels=4, skip_levels_at_top=2
                )
            elif mode == 'color':
                processed = evm.magnify_color(
                    frames_array, self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10),
                    levels=4, skip_levels_at_top=2
                )
            else:
                motion_frames = evm.magnify_motion(
                    frames_array, self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10) * 0.7,
                    levels=4, skip_levels_at_top=2
                )
                processed = evm.magnify_color(
                    motion_frames, self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10) * 1.5,
                    levels=4, skip_levels_at_top=2
                )

            processed = np.clip(processed * 255, 0, 255).astype(np.uint8)
            self.processed_frames = [processed[i] for i in range(len(processed))]

        except Exception as e:
            self.status_label.setText(f"处理失败: {str(e)}")
            self.processed_frames = self.original_frames.copy()

    def update_display(self):
        """更新显示"""
        if not self.is_loaded or not self.original_frames or not self.processed_frames:
            return

        if self.current_frame_idx >= len(self.original_frames):
            self.current_frame_idx = 0

        original = self.original_frames[self.current_frame_idx]
        processed = self.processed_frames[self.current_frame_idx]

        mode = self.compare_mode.currentText()

        if mode == "并排":
            self.display_frame(original, self.original_label)
            self.display_frame(processed, self.processed_label)
        elif mode == "左右分屏":
            h, w = original.shape[:2]
            combined = np.zeros_like(original)
            combined[:, :w//2] = original[:, :w//2]
            combined[:, w//2:] = processed[:, w//2:]
            combined[:, w//2-1:w//2+1] = [255, 200, 0]

            self.display_frame(combined, self.original_label)
            self.display_frame(combined, self.processed_label)
        else:
            h, w = original.shape[:2]
            combined = np.zeros_like(original)
            combined[:h//2, :] = original[:h//2, :]
            combined[h//2:, :] = processed[h//2:, :]
            combined[h//2-1:h//2+1, :] = [255, 200, 0]

            self.display_frame(combined, self.original_label)
            self.display_frame(combined, self.processed_label)

        self.frame_info_label.setText(f"帧: {self.current_frame_idx + 1} / {self.total_frames}")

    def display_frame(self, frame, label):
        """显示帧"""
        h, w = frame.shape[:2]
        bytes_per_line = 3 * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def toggle_play(self):
        """切换播放"""
        if not self.is_loaded:
            return

        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_btn.setText("暂停")
            interval = int(1000 / self.fps) if self.fps > 0 else 33
            self.play_timer.start(interval)
        else:
            self.play_btn.setText("播放")
            self.play_timer.stop()

    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.play_btn.setText("播放")
        self.play_timer.stop()

    def next_frame(self):
        """下一帧"""
        if not self.is_loaded:
            return
        self.current_frame_idx = (self.current_frame_idx + 1) % self.total_frames
        self.frame_slider.setValue(self.current_frame_idx)
        self.update_display()

    def on_slider_changed(self, value):
        """滑块改变"""
        if not self.is_loaded:
            return
        self.current_frame_idx = value
        self.update_display()

    def reset_preview(self):
        """重置"""
        if not self.is_loaded:
            return
        self.current_frame_idx = 0
        self.stop_playback()
        self.frame_slider.setValue(0)
        self.update_display()

    def clear(self):
        """清空预览"""
        self.stop_playback()
        self.original_frames = []
        self.processed_frames = []
        self.is_loaded = False
        self.original_label.clear()
        self.processed_label.clear()
        self.frame_slider.setValue(0)
        self.frame_info_label.setText("帧: 0 / 0")
        self.status_label.setText("等待加载视频")
        self.status_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 12px;")
        self.play_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
