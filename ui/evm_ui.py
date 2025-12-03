#!/usr/bin/env python3
"""
Eulerian Video Magnification UI
欧拉视频放大用户界面
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QPushButton, QTextEdit, QFrame,
    QComboBox, QSlider, QFileDialog, QProgressBar, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import PyQt5.QtCore as QtCore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import EulerianVideoMagnification
from ui.preview_window import VideoPreviewWidget


class ProcessingThread(QThread):
    """视频处理线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, video_path, output_path, params):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.params = params

    def run(self):
        try:
            self.progress.emit("初始化处理器...")
            evm = EulerianVideoMagnification(self.video_path, self.output_path)
            evm.get_video_info()

            mode = self.params['mode']

            # 使用批处理方法（正确的欧拉视频放大算法）
            self.progress.emit("加载视频帧...")
            frames = evm.load_video(max_frames=self.params.get('max_frames'))

            if mode == 'motion':
                self.progress.emit("应用运动放大算法...")
                processed_frames = evm.magnify_motion(
                    frames,
                    evm.fps,
                    freq_low=self.params['freq_low'],
                    freq_high=self.params['freq_high'],
                    amplification=self.params['amplification'],
                    levels=self.params['levels'],
                    skip_levels_at_top=2
                )
            elif mode == 'color':
                self.progress.emit("应用色彩放大算法...")
                processed_frames = evm.magnify_color(
                    frames,
                    evm.fps,
                    freq_low=self.params['freq_low'],
                    freq_high=self.params['freq_high'],
                    amplification=self.params['amplification'],
                    levels=self.params['levels'],
                    skip_levels_at_top=2
                )
            else:  # hybrid
                self.progress.emit("应用混合模式算法...")
                # 先运动放大
                motion_frames = evm.magnify_motion(
                    frames,
                    evm.fps,
                    freq_low=self.params['freq_low'],
                    freq_high=self.params['freq_high'],
                    amplification=self.params['amplification'] * 0.7,
                    levels=self.params['levels'],
                    skip_levels_at_top=2
                )
                # 再色彩放大
                processed_frames = evm.magnify_color(
                    motion_frames,
                    evm.fps,
                    freq_low=self.params['freq_low'],
                    freq_high=self.params['freq_high'],
                    amplification=self.params['amplification'] * 1.5,
                    levels=self.params['levels'],
                    skip_levels_at_top=2
                )

            self.progress.emit("保存视频...")
            audio_source = self.video_path if self.params['keep_audio'] else None
            evm.save_video_from_frames(
                processed_frames,
                audio_source=audio_source,
                output_format=self.params['output_format'],
                mode=self.params['mode'],
                freq_low=self.params['freq_low'],
                freq_high=self.params['freq_high'],
                amplification=self.params['amplification']
            )

            self.finished.emit(True, "处理完成")

        except Exception as e:
            import traceback
            error_msg = f"处理失败: {str(e)}\n{traceback.format_exc()}"
            self.finished.emit(False, error_msg)


class EVMMainWindow(QMainWindow):
    """欧拉视频放大主窗口"""

    def __init__(self):
        super().__init__()
        self.is_processing = False
        self.input_video_path = ""
        self.output_video_path = ""
        self.processing_thread = None
        self.preview_window = None

        self._init_styles()
        self.setup_ui()
        self.setup_styles()

    def _init_styles(self):
        """初始化样式"""
        self.common_styles = {
            'label_style': "color: rgb(200, 200, 200); font-size: 18px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 8px 0px;",
            'button_style': """
                QPushButton {
                    background-color: rgb(45, 45, 50);
                    color: rgb(220, 220, 220);
                    border: 2px solid rgb(80, 120, 180);
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: bold;
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                    padding: 12px 20px;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: rgb(60, 60, 65);
                    border-color: rgb(100, 140, 200);
                }
                QPushButton:pressed {
                    background-color: rgb(35, 35, 40);
                    border-color: rgb(60, 100, 160);
                }
                QPushButton:disabled {
                    background-color: rgb(30, 30, 30);
                    color: rgb(80, 80, 80);
                    border-color: rgb(50, 50, 50);
                }
            """,
            'combobox_style': """
                QComboBox {
                    background-color: rgb(45, 45, 50);
                    color: rgb(220, 220, 220);
                    border: 2px solid rgb(80, 80, 80);
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 15px;
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                    min-height: 20px;
                }
                QComboBox:hover {
                    border-color: rgb(100, 140, 200);
                }
                QComboBox QAbstractItemView {
                    background-color: rgb(45, 45, 50);
                    color: rgb(220, 220, 220);
                    border: 2px solid rgb(80, 80, 80);
                    selection-background-color: rgb(80, 120, 180);
                    font-size: 15px;
                }
            """,
            'slider_style': """
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
                QSlider::handle:horizontal:hover {
                    background: rgb(100, 140, 200);
                    border-color: rgb(120, 160, 220);
                }
            """,
            'spinbox_style': """
                QSpinBox, QDoubleSpinBox {
                    background-color: rgb(45, 45, 50);
                    color: rgb(220, 220, 220);
                    border: 2px solid rgb(80, 80, 80);
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 15px;
                    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                    min-height: 20px;
                }
                QSpinBox:hover, QDoubleSpinBox:hover {
                    border-color: rgb(100, 140, 200);
                }
            """,
            'file_label_style': "color: rgb(180, 180, 180); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; padding: 8px; background-color: rgb(35, 35, 40); border: 1px solid rgb(60, 60, 60); border-radius: 4px;"
        }

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("欧拉视频放大器")
        self.setMinimumSize(1600, 900)
        self.resize(1920, 1080)
        self.setStyleSheet("background-color: rgb(30, 30, 35);")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 水平分割
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 左侧控制面板
        left_panel = QWidget()
        left_panel.setFixedWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # 标题
        self.setup_header(left_layout)
        self.add_separator(left_layout)

        # 文件选择
        self.setup_file_selection(left_layout)
        self.add_separator(left_layout)

        # 处理模式
        self.setup_mode_selection(left_layout)
        self.add_separator(left_layout)

        # 参数设置
        self.setup_parameters(left_layout)
        self.add_separator(left_layout)

        # 控制按钮
        self.setup_control_buttons(left_layout)

        # 进度显示
        self.setup_progress_display(left_layout)

        left_layout.addStretch()

        main_layout.addWidget(left_panel)

        # 右侧预览区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 预览标题
        preview_title = QLabel("预览")
        preview_title.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin-bottom: 5px;")
        preview_title.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(preview_title)

        # 集成预览组件
        from ui.integrated_preview import IntegratedPreviewWidget
        self.preview_widget = IntegratedPreviewWidget()
        right_layout.addWidget(self.preview_widget)

        main_layout.addWidget(right_panel)

    def setup_header(self, layout):
        """设置标题"""
        title_label = QLabel("欧拉视频放大器")
        title_label.setStyleSheet("color: rgb(255, 255, 255); font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

    def setup_file_selection(self, layout):
        """设置文件选择"""
        # 输入文件
        input_label = QLabel("输入视频")
        input_label.setStyleSheet(self.common_styles['label_style'])
        layout.addWidget(input_label)

        input_layout = QHBoxLayout()
        self.input_path_label = QLabel("未选择文件")
        self.input_path_label.setStyleSheet(self.common_styles['file_label_style'])
        input_layout.addWidget(self.input_path_label)

        self.browse_input_btn = QPushButton("浏览")
        self.browse_input_btn.setFixedHeight(40)
        self.browse_input_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.browse_input_btn)

        layout.addLayout(input_layout)

        # 预览和分析按钮行
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.preview_btn = QPushButton("加载预览")
        self.preview_btn.setFixedHeight(40)
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.load_preview)
        action_layout.addWidget(self.preview_btn)

        self.analyze_freq_btn = QPushButton("分析频率")
        self.analyze_freq_btn.setFixedHeight(40)
        self.analyze_freq_btn.setEnabled(False)
        self.analyze_freq_btn.clicked.connect(self.analyze_frequencies)
        action_layout.addWidget(self.analyze_freq_btn)

        layout.addLayout(action_layout)

        # 输出文件
        output_label = QLabel("输出路径")
        output_label.setStyleSheet(self.common_styles['label_style'])
        layout.addWidget(output_label)

        output_layout = QHBoxLayout()
        self.output_path_label = QLabel("未设置路径")
        self.output_path_label.setStyleSheet(self.common_styles['file_label_style'])
        output_layout.addWidget(self.output_path_label)

        self.browse_output_btn = QPushButton("设置")
        self.browse_output_btn.setFixedHeight(40)
        self.browse_output_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(self.browse_output_btn)

        layout.addLayout(output_layout)

    def setup_mode_selection(self, layout):
        """设置处理模式"""
        mode_label = QLabel("处理模式")
        mode_label.setStyleSheet(self.common_styles['label_style'])
        layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["运动放大", "色彩放大", "混合模式"])
        self.mode_combo.setCurrentIndex(0)
        layout.addWidget(self.mode_combo)

    def setup_parameters(self, layout):
        """设置参数"""
        params_label = QLabel("参数设置")
        params_label.setStyleSheet(self.common_styles['label_style'])
        layout.addWidget(params_label)

        # 放大倍数
        amp_layout = QHBoxLayout()
        amp_label = QLabel("放大倍数:")
        amp_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        amp_layout.addWidget(amp_label)
        self.amplification_slider = QSlider(Qt.Horizontal)
        self.amplification_slider.setRange(1, 100)
        self.amplification_slider.setValue(10)
        self.amplification_slider.valueChanged.connect(self.update_amp_label)
        amp_layout.addWidget(self.amplification_slider)
        self.amp_value_label = QLabel("10")
        self.amp_value_label.setFixedWidth(60)
        self.amp_value_label.setStyleSheet("color: rgb(80, 120, 180); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        amp_layout.addWidget(self.amp_value_label)
        layout.addLayout(amp_layout)

        # 频率范围 - 添加智能建议功能
        freq_layout = QHBoxLayout()
        freq_low_label = QLabel("低频:")
        freq_low_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        freq_layout.addWidget(freq_low_label)
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.freq_low_spin = QDoubleSpinBox()
        self.freq_low_spin.setRange(0.1, 10.0)
        self.freq_low_spin.setValue(0.4)
        self.freq_low_spin.setDecimals(1)
        self.freq_low_spin.setSingleStep(0.1)
        self.freq_low_spin.setSuffix(" Hz")
        freq_layout.addWidget(self.freq_low_spin)

        freq_high_label = QLabel("高频:")
        freq_high_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        freq_layout.addWidget(freq_high_label)
        self.freq_high_spin = QDoubleSpinBox()
        self.freq_high_spin.setRange(0.5, 20.0)
        self.freq_high_spin.setValue(3.0)
        self.freq_high_spin.setDecimals(1)
        self.freq_high_spin.setSingleStep(0.1)
        self.freq_high_spin.setSuffix(" Hz")
        freq_layout.addWidget(self.freq_high_spin)

        # 添加智能建议按钮
        self.suggest_freq_btn = QPushButton("智能建议")
        self.suggest_freq_btn.setFixedSize(110, 35)
        self.suggest_freq_btn.setEnabled(False)  # 初始禁用
        self.suggest_freq_btn.clicked.connect(self.apply_frequency_suggestion)
        freq_layout.addWidget(self.suggest_freq_btn)

        layout.addLayout(freq_layout)

        # 频率分析结果显示
        self.freq_analysis_label = QLabel("")
        self.freq_analysis_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")
        self.freq_analysis_label.setWordWrap(True)
        layout.addWidget(self.freq_analysis_label)

        # 其他选项 - 第一行
        options_layout1 = QHBoxLayout()
        self.keep_audio_btn = QPushButton("保留音频")
        self.keep_audio_btn.setCheckable(True)
        self.keep_audio_btn.setChecked(True)
        options_layout1.addWidget(self.keep_audio_btn)

        max_frames_label = QLabel("最大帧数:")
        max_frames_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        options_layout1.addWidget(max_frames_label)
        self.max_frames_spin = QSpinBox()
        self.max_frames_spin.setRange(0, 10000)
        self.max_frames_spin.setValue(0)
        self.max_frames_spin.setSpecialValueText("全部")
        options_layout1.addWidget(self.max_frames_spin)
        layout.addLayout(options_layout1)

        # 输出格式选择 - 第二行
        format_layout = QHBoxLayout()
        format_label = QLabel("输出格式:")
        format_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        format_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "MP4 (H.264)",
            "ProRes Proxy",
            "ProRes LT",
            "ProRes Standard",
            "ProRes HQ",
            "ProRes 4444",
            "ProRes 4444 XQ"
        ])
        self.format_combo.setCurrentIndex(0)
        format_layout.addWidget(self.format_combo)

        # 添加格式说明
        format_info = QLabel("ProRes适合专业后期")
        format_info.setStyleSheet("color: rgb(150, 150, 150); font-size: 13px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        format_layout.addWidget(format_info)

        layout.addLayout(format_layout)

    def setup_control_buttons(self, layout):
        """设置控制按钮"""
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始处理")
        self.start_btn.setFixedHeight(55)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(60, 120, 60);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(80, 140, 80);
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: rgb(80, 140, 80);
                border-color: rgb(100, 160, 100);
            }
            QPushButton:pressed {
                background-color: rgb(50, 100, 50);
            }
            QPushButton:disabled {
                background-color: rgb(40, 40, 40);
                color: rgb(100, 100, 100);
                border-color: rgb(60, 60, 60);
            }
        """)
        self.start_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedHeight(55)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(120, 60, 60);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(140, 80, 80);
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: rgb(140, 80, 80);
                border-color: rgb(160, 100, 100);
            }
            QPushButton:pressed {
                background-color: rgb(100, 50, 50);
            }
            QPushButton:disabled {
                background-color: rgb(40, 40, 40);
                color: rgb(100, 100, 100);
                border-color: rgb(60, 60, 60);
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

    def setup_progress_display(self, layout):
        """设置进度显示"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 15px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 10px 0px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def setup_styles(self):
        """应用样式"""
        self.browse_input_btn.setStyleSheet(self.common_styles['button_style'])
        self.browse_output_btn.setStyleSheet(self.common_styles['button_style'])
        self.mode_combo.setStyleSheet(self.common_styles['combobox_style'])
        self.amplification_slider.setStyleSheet(self.common_styles['slider_style'])
        self.freq_low_spin.setStyleSheet(self.common_styles['spinbox_style'])
        self.freq_high_spin.setStyleSheet(self.common_styles['spinbox_style'])
        self.max_frames_spin.setStyleSheet(self.common_styles['spinbox_style'])
        self.format_combo.setStyleSheet(self.common_styles['combobox_style'])
        self.analyze_freq_btn.setStyleSheet(self.common_styles['button_style'])
        self.suggest_freq_btn.setStyleSheet(self.common_styles['button_style'])
        self.keep_audio_btn.setStyleSheet(self.common_styles['button_style'])
        self.preview_btn.setStyleSheet(self.common_styles['button_style'])
        self.start_btn.setStyleSheet(self.common_styles['button_style'])
        self.stop_btn.setStyleSheet(self.common_styles['button_style'])

    def update_amp_label(self, value):
        """更新放大倍数标签"""
        self.amp_value_label.setText(str(value))

    def browse_input_file(self):
        """浏览输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择输入视频", "", "视频文件 (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            self.input_video_path = file_path
            self.input_path_label.setText(os.path.basename(file_path))

            # 启用预览和分析按钮
            self.preview_btn.setEnabled(True)
            self.analyze_freq_btn.setEnabled(True)

            # 自动设置输出路径
            if not self.output_video_path:
                base_name = os.path.splitext(file_path)[0]
                self.output_video_path = f"{base_name}_magnified.mp4"
                self.output_path_label.setText(os.path.basename(self.output_video_path))

    def browse_output_file(self):
        """设置输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "设置输出路径", "", "视频文件 (*.mp4)"
        )
        if file_path:
            self.output_video_path = file_path
            self.output_path_label.setText(os.path.basename(file_path))

    def start_processing(self):
        """开始处理"""
        if not self.input_video_path:
            self.show_status("请选择输入视频", False)
            return

        if not self.output_video_path:
            self.show_status("请设置输出路径", False)
            return

        # 获取参数
        mode_map = {"运动放大": "motion", "色彩放大": "color", "混合模式": "hybrid"}
        format_map = {
            "MP4 (H.264)": "mp4",
            "ProRes Proxy": "prores_proxy",
            "ProRes LT": "prores_lt",
            "ProRes Standard": "prores_standard",
            "ProRes HQ": "prores_hq",
            "ProRes 4444": "prores_4444",
            "ProRes 4444 XQ": "prores_4444xq"
        }

        params = {
            'mode': mode_map[self.mode_combo.currentText()],
            'amplification': self.amplification_slider.value(),
            'freq_low': self.freq_low_spin.value(),  # 直接使用小数值
            'freq_high': self.freq_high_spin.value(),  # 直接使用小数值
            'levels': 4,
            'blend': 1.0,
            'keep_audio': self.keep_audio_btn.isChecked(),
            'max_frames': self.max_frames_spin.value() if self.max_frames_spin.value() > 0 else None,
            'output_format': format_map[self.format_combo.currentText()]
        }

        # 显示处理提示
        self.show_status("开始处理视频", True)

        # 启动处理线程
        self.processing_thread = ProcessingThread(
            self.input_video_path, self.output_video_path, params
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.start()

        # 更新UI状态
        self.is_processing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

    def stop_processing(self):
        """停止处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait()

        self.processing_finished(False, "处理已停止")

    def update_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
        # 强制刷新UI
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

    def processing_finished(self, success, message):
        """处理完成"""
        self.is_processing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.show_status(message, success)

    def show_status(self, message, is_success=True):
        """显示状态消息"""
        if is_success:
            color = "rgb(100, 200, 100)"
        else:
            color = "rgb(200, 100, 100)"

        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
                margin: 10px 0px;
            }}
        """)
        self.status_label.setText(message)

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.status_label.setText(""))

    def analyze_frequencies(self):
        """分析视频频率"""
        if not self.input_video_path:
            self.show_status("请先选择输入视频", False)
            return

        try:
            self.analyze_freq_btn.setEnabled(False)
            self.analyze_freq_btn.setText("分析中...")
            self.freq_analysis_label.setText("正在分析视频频率，请稍候...")

            # 强制刷新UI
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

            # 创建EVM实例并分析频率
            from core import EulerianVideoMagnification
            evm = EulerianVideoMagnification(self.input_video_path)
            evm.get_video_info()

            # 执行频率分析
            analysis_result = evm.analyze_video_frequencies(max_frames=200)

            if analysis_result and analysis_result['dominant_frequencies']:
                # 保存分析结果
                self.analysis_result = analysis_result

                # 显示简要结果
                dominant_freqs = analysis_result['dominant_frequencies']
                result_text = f"检测到 {len(dominant_freqs)} 个主要频率成分 (点击查看详情)"
                self.freq_analysis_label.setText(result_text)
                self.freq_analysis_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")

                # 启用智能建议按钮
                self.suggest_freq_btn.setEnabled(True)

                # 显示详细分析对话框
                from ui.frequency_analysis_dialog import FrequencyAnalysisDialog
                dialog = FrequencyAnalysisDialog(analysis_result, self)
                if dialog.exec_() == FrequencyAnalysisDialog.Accepted:
                    # 用户点击了"应用建议参数"
                    suggested_params = dialog.get_suggested_params()
                    if suggested_params:
                        self.freq_low_spin.setValue(suggested_params['freq_low'])
                        self.freq_high_spin.setValue(suggested_params['freq_high'])
                        self.amplification_slider.setValue(suggested_params['amplification'])
                        self.show_status(f"已应用建议参数 ({suggested_params['motion_type']})", True)

                self.show_status("频率分析完成", True)
            else:
                self.freq_analysis_label.setText("未检测到明显的频率成分，建议使用默认参数")
                self.freq_analysis_label.setStyleSheet("color: rgb(200, 100, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")
                self.show_status("频率分析未找到明显成分", False)

        except Exception as e:
            self.freq_analysis_label.setText(f"频率分析失败: {str(e)}")
            self.freq_analysis_label.setStyleSheet("color: rgb(200, 100, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")
            self.show_status(f"频率分析出错: {str(e)}", False)

        finally:
            self.analyze_freq_btn.setEnabled(True)
            self.analyze_freq_btn.setText("分析频率")

    def apply_frequency_suggestion(self):
        """应用智能频率建议"""
        if not hasattr(self, 'analysis_result') or not self.analysis_result:
            self.show_status("请先进行频率分析", False)
            return

        try:
            # 创建EVM实例并获取建议
            from core import EulerianVideoMagnification
            evm = EulerianVideoMagnification(self.input_video_path)

            suggestion = evm.suggest_frequency_range(self.analysis_result)

            if suggestion and suggestion['confidence'] == 'high':
                # 应用建议的频率范围（直接使用小数值）
                suggested_low = suggestion['freq_low']
                suggested_high = suggestion['freq_high']

                self.freq_low_spin.setValue(suggested_low)
                self.freq_high_spin.setValue(suggested_high)

                # 显示建议信息
                motion_type = suggestion.get('motion_type', '未知')
                dominant_freq = suggestion.get('dominant_frequency', 0)

                suggestion_text = f"已应用智能建议:\n"
                suggestion_text += f"  检测类型: {motion_type}\n"
                suggestion_text += f"  主频率: {dominant_freq:.2f} Hz\n"
                suggestion_text += f"  建议范围: {suggestion['freq_low']:.1f} - {suggestion['freq_high']:.1f} Hz"

                self.freq_analysis_label.setText(suggestion_text)
                self.freq_analysis_label.setStyleSheet("color: rgb(100, 200, 100); font-size: 14px; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin: 5px 0px;")

                self.show_status("已应用智能频率建议", True)
            else:
                self.show_status("无法生成可靠的频率建议", False)

        except Exception as e:
            self.show_status(f"应用建议时出错: {str(e)}", False)

    def load_preview(self):
        """加载预览"""
        if not self.input_video_path:
            self.show_status("请先选择输入视频", False)
            return

        # 获取当前参数
        mode_map = {"运动放大": "motion", "色彩放大": "color", "混合模式": "hybrid"}
        params = {
            'mode': mode_map[self.mode_combo.currentText()],
            'amplification': self.amplification_slider.value(),
            'freq_low': self.freq_low_spin.value(),
            'freq_high': self.freq_high_spin.value(),
        }

        try:
            self.show_status("正在加载预览...", True)
            self.preview_widget.load_and_process(self.input_video_path, params)
            self.show_status("预览加载完成", True)
        except Exception as e:
            self.show_status(f"预览加载失败: {str(e)}", False)

    def add_separator(self, layout):
        """添加分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("background-color: rgb(9, 9, 9); border: none;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)


def main():
    """主函数"""
    import os
    import sys

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


if __name__ == "__main__":
    main()