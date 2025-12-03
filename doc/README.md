# 欧拉视频放大器 (Eulerian Video Magnification)

一个基于欧拉视频放大技术的视频处理工具，支持运动放大和色彩放大功能。

## 功能特性

- **运动放大**: 放大视频中的微小运动变化
- **色彩放大**: 放大视频中的微小色彩变化
- **混合模式**: 同时应用运动和色彩放大
- **图形界面**: 简洁易用的深色主题界面
- **命令行支持**: 支持批处理和自动化

## 项目结构

```
EVM/
├── core/                   # 核心算法模块
│   ├── __init__.py
│   ├── evm_core.py        # 主要算法实现
│   └── utils.py           # 工具函数
├── ui/                    # 用户界面模块
│   ├── __init__.py
│   └── evm_ui.py          # PyQt5界面
├── doc/                   # 文档
│   └── README.md
├── main.py                # 主程序入口
└── requirements.txt       # 依赖包
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 图形界面模式

```bash
python main.py
```

### 命令行模式

```bash
# 运动放大
python main.py input.mp4 -o output.mp4 -m motion -a 15 -fl 0.8 -fh 1.2

# 色彩放大
python main.py input.mp4 -o output.mp4 -m color -a 50 -fl 0.5 -fh 3.0

# 混合模式
python main.py input.mp4 -o output.mp4 -m hybrid -a 20
```

## 参数说明

- `-m, --mode`: 处理模式 (motion/color/hybrid)
- `-a, --amplification`: 放大倍数
- `-fl, --freq-low`: 低频截止 (Hz)
- `-fh, --freq-high`: 高频截止 (Hz)
- `-l, --levels`: 金字塔层数
- `--keep-audio`: 保留原视频音频
- `--blend`: 与原视频混合比例 (0-1)

## 技术原理

欧拉视频放大基于以下核心技术：

1. **高斯/拉普拉斯金字塔**: 多尺度图像分解
2. **时域带通滤波**: 提取特定频率范围的变化
3. **信号放大**: 放大提取的变化信号
4. **图像重建**: 将放大后的信号叠加回原图像

## 应用场景

- 医学影像分析（心跳、脉搏可视化）
- 工程检测（结构振动分析）
- 艺术创作（视觉效果增强）
- 科学研究（微小变化观察）