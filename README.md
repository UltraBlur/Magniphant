# 欧拉视频放大 (Eulerian Video Magnification) - VideoArt创作工具

将不可见的微小运动和色彩变化放大，创造超现实的视觉艺术。

## 📖 简介

欧拉视频放大（EVM）是一种计算机视觉技术，可以：
- 🫀 **可视化心跳** - 让皮肤随心跳变色
- 🌬️ **放大呼吸** - 微小的胸部起伏变得明显
- 🏢 **建筑"呼吸"** - 显示建筑物的微小振动
- 🎨 **迷幻艺术** - 创造超现实的色彩和运动效果
- 🎵 **音乐可视化** - 让视觉随节奏跳动

## 🚀 快速开始

### 安装依赖

```bash
pip install numpy opencv-python scipy --break-system-packages

# 安装FFmpeg（如果尚未安装）
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# 从 https://ffmpeg.org/download.html 下载
```

### 基础用法

```bash
# 心跳可视化（拍摄人脸或手腕）
python eulerian_video_magnification.py input.mp4 -o heartbeat.mp4 -m color -a 30 -fl 0.8 -fh 3.0

# 呼吸放大（拍摄睡眠者）
python eulerian_video_magnification.py input.mp4 -o breathing.mp4 -m motion -a 50 -fl 0.2 -fh 0.5

# 迷幻艺术
python eulerian_video_magnification.py input.mp4 -o psychedelic.mp4 -m hybrid -a 80 -fl 0.1 -fh 10.0

# 建筑振动
python eulerian_video_magnification.py input.mp4 -o building.mp4 -m motion -a 20 -fl 0.5 -fh 2.0 -l 6
```

### 使用预设配置

```bash
# 查看所有预设
cat presets.json

# 使用预设（通过手动指定参数）
python eulerian_video_magnification.py input.mp4 -o output.mp4 -m color -a 30 -fl 0.83 -fh 3.0
```

## 📋 命令行参数详解

```
python eulerian_video_magnification.py [输入视频] [选项]

必需参数:
  input                输入视频路径

核心参数:
  -o, --output         输出视频路径 (默认: output.mp4)
  -m, --mode           处理模式:
                       - motion: 运动放大
                       - color: 色彩放大
                       - hybrid: 混合模式
  -a, --amplification  放大倍数 (建议: 5-100)
  -fl, --freq-low      低频截止 (Hz)
  -fh, --freq-high     高频截止 (Hz)

高级参数:
  -l, --levels         金字塔层数 (3-6, 默认: 4)
  -p, --pyramid        金字塔类型 (gaussian/laplacian)
  -f, --max-frames     最大处理帧数（测试用）
  --keep-audio         保留原视频音频
  --blend             与原视频混合比例 (0-1)
  -c, --config         JSON配置文件路径
```

## 🎨 创意应用示例

### 1. 心跳可视化 💓

**拍摄建议**: 人脸、手腕、脖颈，保持静止
```bash
python eulerian_video_magnification.py face.mp4 -o heartbeat.mp4 \
  -m color -a 30 -fl 0.83 -fh 3.0
```

**参数解释**:
- 频率范围: 0.83-3.0 Hz = 50-180 BPM（心跳范围）
- 色彩模式: 能更好地捕捉血液流动引起的微小颜色变化

### 2. 呼吸艺术 🌬️

**拍摄建议**: 睡觉的人、婴儿、宠物
```bash
python eulerian_video_magnification.py sleeping.mp4 -o breathing.mp4 \
  -m motion -a 50 -fl 0.2 -fh 0.5 -l 5
```

**参数解释**:
- 频率范围: 0.2-0.5 Hz = 12-30次/分钟（呼吸范围）
- 运动模式: 放大身体的上下起伏

### 3. 超现实建筑 🏙️

**拍摄建议**: 高楼、桥梁、在风中的树木
```bash
python eulerian_video_magnification.py building.mp4 -o surreal.mp4 \
  -m motion -a 20 -fl 0.5 -fh 2.0 -l 6 -p laplacian
```

**参数解释**:
- 频率范围: 0.5-2.0 Hz（建筑自然振动频率）
- 拉普拉斯金字塔: 更好地保留边缘细节

### 4. 迷幻艺术 🌈

**拍摄建议**: 任何光线变化的场景
```bash
python eulerian_video_magnification.py scene.mp4 -o psychedelic.mp4 \
  -m hybrid -a 100 -fl 0.1 -fh 10.0
```

**参数解释**:
- 宽频段: 捕捉所有频率的变化
- 混合模式: 同时放大色彩和运动
- 高放大倍数: 创造极端效果

### 5. 音乐同步 🎵

**拍摄建议**: 配合音乐节奏的场景
```bash
# 120 BPM = 2 Hz
python eulerian_video_magnification.py music_video.mp4 -o synced.mp4 \
  -m hybrid -a 40 -fl 1.6 -fh 2.4 --keep-audio
```

**BPM转Hz公式**: Hz = BPM / 60
- 120 BPM = 2.0 Hz
- 140 BPM = 2.33 Hz
- 90 BPM = 1.5 Hz

## 🎬 高级创作技巧

### 运行高级示例脚本

```bash
python advanced_examples.py

# 然后选择示例 (1-10):
# 1. 心跳可视化
# 2. 呼吸运动
# 3. 建筑振动
# 4. 迷幻色彩
# 5. 选择性区域放大
# 6. 多频段分层
# 7. 时间对比
# 8. 渐变过渡
# 9. 音乐同步
# 10. 极端抽象
```

### 自定义Python脚本

```python
from eulerian_video_magnification import EulerianVideoMagnification

# 创建实例
evm = EulerianVideoMagnification("input.mp4", "output.mp4")
evm.get_video_info()

# 加载视频
frames = evm.load_video(max_frames=600)

# 运动放大
processed = evm.magnify_motion(
    frames, evm.fps,
    freq_low=0.5,
    freq_high=3.0,
    amplification=20
)

# 保存
evm.save_video(processed, audio_source="input.mp4")
```

### 局部区域处理

```python
from eulerian_video_magnification import create_circular_mask
import numpy as np

# 创建圆形遮罩（只放大中心）
mask = create_circular_mask(width, height, radius=200)

# 应用遮罩
mask_3d = mask[:, :, np.newaxis]
final = original * (1 - mask_3d) + processed * mask_3d
```

### 多频段混合

```python
# 分别处理不同频率
low_freq = evm.magnify_motion(frames, fps, 0.1, 0.5, 30)
mid_freq = evm.magnify_motion(frames, fps, 0.5, 2.0, 25)
high_freq = evm.magnify_motion(frames, fps, 2.0, 5.0, 15)

# 混合
final = low_freq * 0.3 + mid_freq * 0.4 + high_freq * 0.3
```

## 📊 参数调优指南

### 放大倍数 (Amplification)

| 倍数 | 效果 | 适用场景 |
|------|------|----------|
| 5-10 | 微妙增强 | 纪录片、自然观察 |
| 10-30 | 明显效果 | 心跳、呼吸可视化 |
| 30-60 | 强烈效果 | 艺术创作、MV |
| 60-100+ | 极端/抽象 | 实验艺术 |

### 频率范围 (Hz)

| 现象 | 频率范围 | 示例参数 |
|------|----------|----------|
| 植物生长 | 0.001-0.01 Hz | --fl 0.001 --fh 0.01 |
| 呼吸 | 0.2-0.5 Hz | --fl 0.2 --fh 0.5 |
| 建筑振动 | 0.5-2 Hz | --fl 0.5 --fh 2.0 |
| 心跳 | 0.8-3 Hz | --fl 0.8 --fh 3.0 |
| 微表情 | 1-5 Hz | --fl 1.0 --fh 5.0 |
| 高频振动 | 2-10 Hz | --fl 2.0 --fh 10.0 |

### 金字塔层数 (Levels)

| 层数 | 效果 | 适用场景 |
|------|------|----------|
| 3 | 快速，粗糙 | 高频运动、快速测试 |
| 4 | 平衡 | 大多数场景 |
| 5-6 | 精细，慢速 | 低频运动、呼吸 |

### 金字塔类型

- **Gaussian**: 适合色彩放大和一般运动
- **Laplacian**: 更好的边缘保留，适合建筑等硬边缘物体

## 🎥 拍摄技巧

### ✅ 推荐做法

1. **使用三脚架** - 任何相机抖动都会被极度放大
2. **稳定光源** - 避免闪烁的灯光
3. **静态主体** - 对于心跳/呼吸可视化
4. **高帧率** - 60fps或更高可捕捉更多细节
5. **良好对比度** - 清晰的主体和背景

### 🎨 创意突破

1. **故意手持** - 创造抽象晃动效果
2. **利用光线变化** - 日落、闪烁霓虹灯
3. **慢动作** - 先拍高帧率，再慢放+EVM
4. **延时摄影** - 捕捉植物生长等极慢运动
5. **多重曝光** - 与EVM结合创造叠影效果

## 🔧 故障排除

### 问题: 结果太噪杂

**解决方案**:
- 降低放大倍数
- 增加金字塔层数
- 确保拍摄时相机稳定
- 使用更稳定的光源

### 问题: 看不到效果

**解决方案**:
- 检查频率范围是否正确
- 增加放大倍数
- 确保拍摄对象有该频率的运动/变化
- 先用预设参数测试

### 问题: 色彩失真

**解决方案**:
- 使用motion模式代替color
- 降低放大倍数
- 使用--blend参数与原视频混合

### 问题: 处理太慢

**解决方案**:
- 减少金字塔层数
- 使用--max-frames参数先测试短片段
- 降低视频分辨率（预处理）
- 减少处理的帧数

## 🎓 原理简述

1. **空间分解** - 将视频分解为多个频率层（金字塔）
2. **时域分析** - 对每个像素位置分析其时间序列
3. **频率滤波** - 提取感兴趣的频率成分
4. **信号放大** - 将提取的信号乘以放大因子
5. **重建合成** - 将放大后的信号加回原视频

**关键区别**:
- **拉格朗日视角**: 追踪像素的运动轨迹（光流法）
- **欧拉视角**: 观察固定位置的变化（本方法）

## 📚 参考资源

### 学术论文
- MIT原始论文: "Eulerian Video Magnification for Revealing Subtle Changes in the World" (2012)
- Phase-based方法: "Phase-Based Video Motion Processing" (2013)

### 艺术参考
- Bill Viola - 慢动作情绪表达
- Granular Synthesis - 数字视频解构
- Ryoji Ikeda - 微观数据可视化

### 在线资源
- MIT原始实现: http://people.csail.mit.edu/mrub/vidmag/
- OpenCV教程: https://opencv.org/

## 🤝 贡献与反馈

欢迎提交问题和改进建议！

## 📄 许可

本工具基于MIT论文的开源实现，仅供学习和艺术创作使用。

---

**享受创作！把不可见的世界变得可见。** 🎨✨
