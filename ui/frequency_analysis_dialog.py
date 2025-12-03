#!/usr/bin/env python3
"""
Frequency Analysis Result Dialog
频率分析结果对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FrequencyAnalysisDialog(QDialog):
    """频率分析结果对话框"""

    def __init__(self, analysis_result, parent=None):
        super().__init__(parent)
        self.analysis_result = analysis_result
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("频率分析结果")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        self.setStyleSheet("background-color: rgb(30, 30, 35);")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题
        title_label = QLabel("视频频率分析报告")
        title_label.setStyleSheet("""
            color: rgb(255, 255, 255);
            font-size: 22px;
            font-weight: bold;
            font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 分隔线
        self.add_separator(main_layout)

        # 基本信息区域
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(40, 40, 45);
                border: 2px solid rgb(60, 60, 65);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)

        # 视频信息
        video_info_label = QLabel("视频信息")
        video_info_label.setStyleSheet("color: rgb(100, 180, 255); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        info_layout.addWidget(video_info_label)

        fps = self.analysis_result.get('fps', 'N/A')
        total_frames = self.analysis_result.get('total_frames', 'N/A')
        analyzed_frames = self.analysis_result.get('analyzed_frames', 'N/A')

        info_text = f"""
        <div style='color: rgb(200, 200, 200); font-size: 14px; line-height: 1.8; font-family: "Microsoft YaHei", "SimHei", sans-serif;'>
        <b>帧率：</b>{fps} FPS<br>
        <b>总帧数：</b>{total_frames}<br>
        <b>分析帧数：</b>{analyzed_frames}
        </div>
        """
        info_text_label = QLabel(info_text)
        info_text_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(info_text_label)

        main_layout.addWidget(info_frame)

        # 主要频率成分
        freq_label = QLabel("检测到的主要频率成分")
        freq_label.setStyleSheet("color: rgb(100, 180, 255); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif; margin-top: 10px;")
        main_layout.addWidget(freq_label)

        # 频率表格
        self.freq_table = QTableWidget()
        self.freq_table.setColumnCount(4)
        self.freq_table.setHorizontalHeaderLabels(["排名", "频率 (Hz)", "强度", "可能类型"])
        self.freq_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.freq_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.freq_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.freq_table.setSelectionMode(QTableWidget.SingleSelection)
        self.freq_table.setAlternatingRowColors(True)

        self.freq_table.setStyleSheet("""
            QTableWidget {
                background-color: rgb(40, 40, 45);
                color: rgb(200, 200, 200);
                border: 2px solid rgb(60, 60, 65);
                border-radius: 8px;
                gridline-color: rgb(50, 50, 55);
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: rgb(80, 120, 180);
                color: rgb(255, 255, 255);
            }
            QHeaderView::section {
                background-color: rgb(50, 50, 55);
                color: rgb(180, 180, 180);
                border: none;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            }
        """)

        # 填充频率数据
        dominant_freqs = self.analysis_result.get('dominant_frequencies', [])
        self.freq_table.setRowCount(len(dominant_freqs))

        for i, freq_info in enumerate(dominant_freqs):
            # 排名
            rank_item = QTableWidgetItem(f"#{i+1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.freq_table.setItem(i, 0, rank_item)

            # 频率
            freq_item = QTableWidgetItem(f"{freq_info['frequency']:.2f}")
            freq_item.setTextAlignment(Qt.AlignCenter)
            self.freq_table.setItem(i, 1, freq_item)

            # 强度
            magnitude_item = QTableWidgetItem(f"{freq_info['magnitude']:.4f}")
            magnitude_item.setTextAlignment(Qt.AlignCenter)
            self.freq_table.setItem(i, 2, magnitude_item)

            # 可能类型
            motion_type = self.classify_frequency(freq_info['frequency'])
            type_item = QTableWidgetItem(motion_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.freq_table.setItem(i, 3, type_item)

        self.freq_table.setMinimumHeight(250)
        main_layout.addWidget(self.freq_table)

        # 建议区域
        suggestion_frame = QFrame()
        suggestion_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(45, 80, 45);
                border: 2px solid rgb(70, 120, 70);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        suggestion_layout = QVBoxLayout(suggestion_frame)

        suggestion_title = QLabel("智能建议")
        suggestion_title.setStyleSheet("color: rgb(150, 255, 150); font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        suggestion_layout.addWidget(suggestion_title)

        # 生成建议文本
        suggestion_text = self.generate_suggestion_text()
        suggestion_label = QLabel(suggestion_text)
        suggestion_label.setTextFormat(Qt.RichText)
        suggestion_label.setWordWrap(True)
        suggestion_label.setStyleSheet("color: rgb(220, 255, 220); font-size: 14px; line-height: 1.6; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        suggestion_layout.addWidget(suggestion_label)

        main_layout.addWidget(suggestion_frame)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_btn = QPushButton("应用建议参数")
        self.apply_btn.setFixedSize(140, 45)
        self.apply_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: rgb(50, 100, 50);
            }
        """)
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.setFixedSize(100, 45)
        self.close_btn.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: rgb(35, 35, 40);
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        main_layout.addLayout(button_layout)

    def classify_frequency(self, freq):
        """分类频率"""
        if freq < 0.5:
            return "呼吸 (0.2-0.5 Hz)"
        elif 0.5 <= freq < 2.0:
            return "心跳 (0.8-2.0 Hz)"
        elif 2.0 <= freq < 5.0:
            return "快速运动 (2-5 Hz)"
        elif 5.0 <= freq < 10.0:
            return "振动 (5-10 Hz)"
        else:
            return "高频振动 (>10 Hz)"

    def generate_suggestion_text(self):
        """生成建议文本"""
        dominant_freqs = self.analysis_result.get('dominant_frequencies', [])

        if not dominant_freqs:
            return "<b>未检测到明显的频率成分</b><br>建议使用默认参数进行处理。"

        top_freq = dominant_freqs[0]
        freq_val = top_freq['frequency']
        magnitude = top_freq['magnitude']

        # 根据频率生成建议
        if 0.8 <= freq_val <= 2.0:
            motion_type = "心跳"
            suggested_low = max(0.4, freq_val - 0.4)
            suggested_high = min(3.0, freq_val + 0.7)
            suggested_amp = 15
            description = "检测到心跳频率，建议使用运动放大模式。"
        elif 0.2 <= freq_val < 0.8:
            motion_type = "呼吸"
            suggested_low = max(0.1, freq_val - 0.2)
            suggested_high = min(1.0, freq_val + 0.3)
            suggested_amp = 20
            description = "检测到呼吸频率，建议使用较大的放大倍数。"
        elif 2.0 <= freq_val < 5.0:
            motion_type = "快速运动"
            suggested_low = max(1.0, freq_val - 1.0)
            suggested_high = min(8.0, freq_val + 2.0)
            suggested_amp = 10
            description = "检测到快速运动，建议使用中等放大倍数。"
        else:
            motion_type = "其他运动"
            suggested_low = max(0.4, freq_val - 1.0)
            suggested_high = min(10.0, freq_val + 2.0)
            suggested_amp = 12
            description = "检测到运动信号，建议根据实际效果调整参数。"

        suggestion_html = f"""
        <b>检测类型：</b>{motion_type}<br>
        <b>主频率：</b>{freq_val:.2f} Hz (强度: {magnitude:.4f})<br>
        <b>建议频率范围：</b>{suggested_low:.1f} - {suggested_high:.1f} Hz<br>
        <b>建议放大倍数：</b>{suggested_amp}x<br>
        <br>
        <b>说明：</b>{description}
        """

        # 保存建议参数供外部使用
        self.suggested_params = {
            'freq_low': suggested_low,
            'freq_high': suggested_high,
            'amplification': suggested_amp,
            'motion_type': motion_type
        }

        return suggestion_html

    def add_separator(self, layout):
        """添加分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("background-color: rgb(60, 60, 65); border: none;")
        separator.setFixedHeight(2)
        layout.addWidget(separator)

    def get_suggested_params(self):
        """获取建议参数"""
        return getattr(self, 'suggested_params', None)
