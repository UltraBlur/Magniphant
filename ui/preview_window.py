#!/usr/bin/env python3
"""
Video Preview Window with Real-time Comparison
实时视频预览和对比窗口
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import EulerianVideoMagnification


class VideoPreviewWidget(QWidget):
    """视频预览组件 - 高性能实时预览"""

    closed = pyqtSignal()

    def __init__(self, video_path, params, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.params = params
        self.cap = None
        self.original_frames = []
        self.processed_frames = []
        self.current_frame_idx = 0
        self.is_playing = False
        self.fps = 30
        self.total_frames = 0
        self.preview_size = (640, 480)

        # 预加载帧数（用于实时预览）
        self.max_preview_frames = 150

        self.setup_ui()
        self.load_preview_frames()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("视频预览")
        self.setMinimumSize(1400, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel("实时预览对比")
        title_label.setStyleSheet("color: rgb(255, 255, 255); font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 视频显示区域
        video_layout = QHBoxLayout()

        # 原始视频
        original_container = QVBoxLayout()
        original_title = QLabel("原始视频")
        original_title.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        original_title.setAlignment(Qt.AlignCenter)
        original_container.addWidget(original_title)

        self.original_label = QLabel()
        self.original_label.setMinimumSize(640, 480)
        self.original_label.setStyleSheet("background-color: rgb(20, 20, 20); border: 2px solid rgb(80, 80, 80);")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setScaledContents(False)
        original_container.addWidget(self.original_label)

        video_layout.addLayout(original_container)

        # 处理后视频
        processed_container = QVBoxLayout()
        processed_title = QLabel("处理后视频")
        processed_title.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        processed_title.setAlignment(Qt.AlignCenter)
        processed_container.addWidget(processed_title)

        self.processed_label = QLabel()
        self.processed_label.setMinimumSize(640, 480)
        self.processed_label.setStyleSheet("background-color: rgb(20, 20, 20); border: 2px solid rgb(80, 80, 80);")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setScaledContents(False)
        processed_container.addWidget(self.processed_label)

        video_layout.addLayout(processed_container)

        main_layout.addLayout(video_layout)

        # 进度条
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.setMinimum(0)
        self.frame_slider.setMaximum(100)
        self.frame_slider.setValue(0)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)
        self.frame_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 2px solid rgb(80, 80, 80);
                height: 12px;
                background: rgb(35, 35, 40);
                margin: 4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: rgb(80, 120, 180);
                border: 2px solid rgb(100, 140, 200);
                width: 24px;
                margin: -6px 0;
                border-radius: 12px;
            }
        """)
        main_layout.addWidget(self.frame_slider)

        # 帧信息
        self.frame_info_label = QLabel("帧: 0 / 0")
        self.frame_info_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        self.frame_info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.frame_info_label)

        # 控制按钮
        control_layout = QHBoxLayout()

        self.play_btn = QPushButton("播放")
        self.play_btn.setFixedSize(100, 40)
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(60, 120, 60);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(80, 140, 80);
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QPushButton:hover {
                background-color: rgb(80, 140, 80);
            }
        """)
        control_layout.addWidget(self.play_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedSize(100, 40)
        self.reset_btn.clicked.connect(self.reset_preview)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(45, 45, 50);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 120, 180);
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QPushButton:hover {
                background-color: rgb(60, 60, 65);
            }
        """)
        control_layout.addWidget(self.reset_btn)

        # 对比模式选择
        mode_label = QLabel("对比模式:")
        mode_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 15px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        control_layout.addWidget(mode_label)

        self.compare_mode = QComboBox()
        self.compare_mode.addItems(["并排对比", "左右分屏", "上下分屏"])
        self.compare_mode.currentIndexChanged.connect(self.update_display)
        self.compare_mode.setStyleSheet("""
            QComboBox {
                background-color: rgb(45, 45, 50);
                color: rgb(220, 220, 220);
                border: 2px solid rgb(80, 80, 80);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
        """)
        control_layout.addWidget(self.compare_mode)

        control_layout.addStretch()

        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        control_layout.addWidget(self.status_label)

        main_layout.addLayout(control_layout)

        # 播放定时器
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.next_frame)

        # 设置窗口样式
        self.setStyleSheet("background-color: rgb(30, 30, 35);")

    def load_preview_frames(self):
        """加载预览帧（优化版本 - 快速加载）"""
        try:
            self.status_label.setText("加载视频...")
            self.status_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px;")

            # 打开视频
            self.cap = cv2.VideoCapture(self.video_path)
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            self.total_frames = min(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), self.max_preview_frames)

            # 快速加载原始帧
            self.original_frames = []
            frame_count = 0

            while frame_count < self.total_frames:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # 转换为RGB并调整大小以提高性能
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = frame.shape[:2]

                # 计算缩放比例以适应预览窗口
                scale = min(self.preview_size[0] / w, self.preview_size[1] / h)
                new_w, new_h = int(w * scale), int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                self.original_frames.append(frame)
                frame_count += 1

                # 每10帧更新一次状态
                if frame_count % 10 == 0:
                    self.status_label.setText(f"加载中: {frame_count}/{self.total_frames}")

            self.cap.release()

            # 处理帧（使用EVM算法）
            self.status_label.setText("处理视频...")
            self.process_frames()

            # 更新滑块
            self.frame_slider.setMaximum(self.total_frames - 1)
            self.update_display()

            self.status_label.setText("准备就绪")
            self.status_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px;")

        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
            self.status_label.setStyleSheet("color: rgb(200, 100, 100); font-size: 14px;")

    def process_frames(self):
        """处理视频帧"""
        try:
            # 将帧列表转换为numpy数组
            frames_array = np.array(self.original_frames, dtype=np.float32) / 255.0

            # 创建EVM实例
            evm = EulerianVideoMagnification(self.video_path)
            evm.fps = self.fps

            mode = self.params.get('mode', 'motion')

            # 应用处理
            if mode == 'motion':
                processed = evm.magnify_motion(
                    frames_array,
                    self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10),
                    levels=4,
                    skip_levels_at_top=2
                )
            elif mode == 'color':
                processed = evm.magnify_color(
                    frames_array,
                    self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10),
                    levels=4,
                    skip_levels_at_top=2
                )
            else:  # hybrid
                motion_frames = evm.magnify_motion(
                    frames_array,
                    self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10) * 0.7,
                    levels=4,
                    skip_levels_at_top=2
                )
                processed = evm.magnify_color(
                    motion_frames,
                    self.fps,
                    freq_low=self.params.get('freq_low', 0.4),
                    freq_high=self.params.get('freq_high', 3.0),
                    amplification=self.params.get('amplification', 10) * 1.5,
                    levels=4,
                    skip_levels_at_top=2
                )

            # 转换回uint8
            processed = np.clip(processed * 255, 0, 255).astype(np.uint8)
            self.processed_frames = [processed[i] for i in range(len(processed))]

        except Exception as e:
            self.status_label.setText(f"处理失败: {str(e)}")
            self.status_label.setStyleSheet("color: rgb(200, 100, 100); font-size: 14px;")
            # 如果处理失败，使用原始帧作为处理后的帧
            self.processed_frames = self.original_frames.copy()

    def update_display(self):
        """更新显示"""
        if not self.original_frames or not self.processed_frames:
            return

        if self.current_frame_idx >= len(self.original_frames):
            self.current_frame_idx = 0

        original = self.original_frames[self.current_frame_idx]
        processed = self.processed_frames[self.current_frame_idx]

        mode = self.compare_mode.currentText()

        if mode == "并排对比":
            # 分别显示
            self.display_frame(original, self.original_label)
            self.display_frame(processed, self.processed_label)
        elif mode == "左右分屏":
            # 左右分屏对比
            h, w = original.shape[:2]
            combined = np.zeros_like(original)
            combined[:, :w//2] = original[:, :w//2]
            combined[:, w//2:] = processed[:, w//2:]

            # 添加分割线
            combined[:, w//2-2:w//2+2] = [255, 255, 0]

            self.display_frame(combined, self.original_label)
            self.display_frame(combined, self.processed_label)
        else:  # 上下分屏
            h, w = original.shape[:2]
            combined = np.zeros_like(original)
            combined[:h//2, :] = original[:h//2, :]
            combined[h//2:, :] = processed[h//2:, :]

            # 添加分割线
            combined[h//2-2:h//2+2, :] = [255, 255, 0]

            self.display_frame(combined, self.original_label)
            self.display_frame(combined, self.processed_label)

        # 更新帧信息
        self.frame_info_label.setText(f"帧: {self.current_frame_idx + 1} / {self.total_frames}")

    def display_frame(self, frame, label):
        """在标签上显示帧"""
        h, w = frame.shape[:2]
        bytes_per_line = 3 * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # 缩放以适应标签大小
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def toggle_play(self):
        """切换播放/暂停"""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_btn.setText("暂停")
            interval = int(1000 / self.fps) if self.fps > 0 else 33
            self.play_timer.start(interval)
        else:
            self.play_btn.setText("播放")
            self.play_timer.stop()

    def next_frame(self):
        """下一帧"""
        self.current_frame_idx = (self.current_frame_idx + 1) % self.total_frames
        self.frame_slider.setValue(self.current_frame_idx)
        self.update_display()

    def on_slider_changed(self, value):
        """滑块改变"""
        self.current_frame_idx = value
        self.update_display()

    def reset_preview(self):
        """重置预览"""
        self.current_frame_idx = 0
        self.is_playing = False
        self.play_btn.setText("播放")
        self.play_timer.stop()
        self.frame_slider.setValue(0)
        self.update_display()

    def closeEvent(self, event):
        """关闭事件"""
        self.play_timer.stop()
        if self.cap:
            self.cap.release()
        self.closed.emit()
        event.accept()
