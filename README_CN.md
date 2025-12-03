# 🐘 Magniphant

[English](README.md) | [简体中文](README_CN.md)

> 用大象之力，揭示不可见的世界

放大肉眼无法察觉的微小运动和色彩变化。可视化心跳、呼吸、建筑振动，从普通视频创造迷幻艺术效果。基于欧拉视频放大技术。

## ✨ 功能特性

- 🫀 **可视化心跳** - 让皮肤随心跳变色
- 🌬️ **放大呼吸** - 微小的胸部起伏变得明显
- 🏢 **建筑振动** - 显示建筑物的微小振动
- 🎨 **迷幻艺术** - 创造超现实的色彩和运动效果
- 🎵 **音乐可视化** - 让视觉随节奏跳动

## 🚀 快速开始

### 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（快速的 Python 包管理器）
- FFmpeg（用于视频处理）

### 安装步骤

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# 或
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 克隆仓库
git clone https://github.com/yourusername/magniphant.git
cd magniphant

# 使用 uv 安装依赖
uv sync

# 安装 FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: 从 https://ffmpeg.org/download.html 下载
```

### 使用方法

```bash
# 运行图形界面
uv run evm

# 或使用命令行
uv run python main.py input.mp4 -o output.mp4 -m color -a 30 -fl 0.8 -fh 3.0
```

## 📖 使用示例

### 心跳可视化

```bash
uv run python main.py face.mp4 -o heartbeat.mp4 \
  -m color -a 30 -fl 0.83 -fh 3.0
```

**参数说明：**
- 频率范围：0.83-3.0 Hz = 50-180 BPM（心跳范围）
- 模式：色彩放大，捕捉血液流动引起的颜色变化

### 呼吸放大

```bash
uv run python main.py sleeping.mp4 -o breathing.mp4 \
  -m motion -a 50 -fl 0.2 -fh 0.5
```

**参数说明：**
- 频率范围：0.2-0.5 Hz = 12-30 次/分钟（呼吸范围）
- 模式：运动放大，放大身体的上下起伏

### 迷幻艺术

```bash
uv run python main.py scene.mp4 -o psychedelic.mp4 \
  -m hybrid -a 80 -fl 0.1 -fh 10.0
```

**参数说明：**
- 宽频段：捕捉所有频率的变化
- 混合模式：同时放大色彩和运动
- 高放大倍数：创造极端效果

## 🎛️ 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-m, --mode` | 处理模式：`motion`（运动）、`color`（色彩）、`hybrid`（混合） | `-m color` |
| `-a, --amplification` | 放大倍数（5-100） | `-a 30` |
| `-fl, --freq-low` | 低频截止（Hz） | `-fl 0.8` |
| `-fh, --freq-high` | 高频截止（Hz） | `-fh 3.0` |
| `-l, --levels` | 金字塔层数（3-6） | `-l 4` |
| `--keep-audio` | 保留原视频音频 | `--keep-audio` |

## 📊 频率参考指南

| 现象 | 频率范围 | 参数示例 |
|------|----------|----------|
| 呼吸 | 0.2-0.5 Hz | `--fl 0.2 --fh 0.5` |
| 心跳 | 0.8-3.0 Hz | `--fl 0.8 --fh 3.0` |
| 建筑振动 | 0.5-2.0 Hz | `--fl 0.5 --fh 2.0` |
| 音乐（120 BPM） | 1.6-2.4 Hz | `--fl 1.6 --fh 2.4` |

**BPM 转 Hz 公式：** Hz = BPM / 60

## 🎥 拍摄技巧

**获得最佳效果：**
- 使用三脚架（相机抖动会被极度放大）
- 稳定光源（避免闪烁的灯光）
- 静态主体（用于心跳/呼吸可视化）
- 高帧率（60fps 以上可捕捉更多细节）

**创意效果：**
- 故意手持拍摄创造抽象效果
- 利用光线变化（日落、霓虹灯）
- 结合慢动作拍摄
- 延时摄影捕捉植物生长

## 🔧 开发

```bash
# 运行测试
uv run pytest

# 代码格式化
uv run black .

# 类型检查
uv run mypy .
```

## 📚 参考资料

- MIT 论文：["Eulerian Video Magnification for Revealing Subtle Changes in the World"](http://people.csail.mit.edu/mrub/vidmag/) (2012)
- Phase-based 方法："Phase-Based Video Motion Processing" (2013)

## 📄 许可证

MIT License - 基于 MIT 的开源实现，仅供学习和艺术创作使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**让不可见的世界变得可见。** 🎨✨
