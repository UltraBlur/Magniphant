# 🎨 快速上手指南

## 30秒开始使用

### 1️⃣ 下载所有文件
将下面列出的所有文件下载到同一个文件夹

### 2️⃣ 安装依赖
```bash
pip install -r requirements.txt --break-system-packages
```

### 3️⃣ 三种方式开始创作

#### 方式A: 一键启动（推荐）
```bash
bash start.sh
```
然后跟随菜单选择操作

#### 方式B: 交互式配置
```bash
python config_generator.py
```
根据你的拍摄对象自动推荐参数

#### 方式C: 直接处理视频
```bash
python eulerian_video_magnification.py input.mp4 -o output.mp4 -m motion -a 20 -fl 0.5 -fh 3.0
```

## 📋 常用命令速查

### 心跳可视化（拍摄人脸）
```bash
python eulerian_video_magnification.py face.mp4 -o heartbeat.mp4 -m color -a 30 -fl 0.8 -fh 3.0
```

### 呼吸放大（拍摄睡眠者）
```bash
python eulerian_video_magnification.py sleeping.mp4 -o breathing.mp4 -m motion -a 50 -fl 0.2 -fh 0.5
```

### 迷幻艺术
```bash
python eulerian_video_magnification.py scene.mp4 -o psychedelic.mp4 -m hybrid -a 80 -fl 0.1 -fh 10.0
```

### 建筑振动
```bash
python eulerian_video_magnification.py building.mp4 -o output.mp4 -m motion -a 20 -fl 0.5 -fh 2.0 -l 6
```

## 🎯 参数速记

| 参数 | 含义 | 常用值 |
|------|------|--------|
| -m | 模式 | motion, color, hybrid |
| -a | 放大倍数 | 10-30轻微, 30-60强烈, 60+极端 |
| -fl | 低频Hz | 0.2呼吸, 0.8心跳, 0.5建筑 |
| -fh | 高频Hz | 0.5呼吸, 3.0心跳, 2.0建筑 |
| -l | 金字塔层数 | 4通用, 5-6精细 |

## 🎬 拍摄要点

✅ **必须做**:
- 使用三脚架（相机抖动会被放大）
- 稳定的光源
- 至少拍摄10秒以上

🎨 **创意突破**:
- 故意手持→抽象效果
- 利用光线变化→色彩艺术
- 高帧率拍摄→更多细节

## 📚 详细文档

- **README.md** - 完整教程和参数详解
- **PROJECT_GUIDE.md** - 项目结构和学习路径
- **presets.json** - 15+种效果预设

## 🆘 遇到问题？

### 看不到效果
- 增加 `-a` 放大倍数
- 检查 `-fl` 和 `-fh` 频率范围

### 太多噪点
- 降低 `-a` 放大倍数
- 确保拍摄时相机稳定

### 处理太慢
- 添加 `-f 300` 只处理前300帧测试
- 降低视频分辨率

## 🎉 开始创作

1. 拍一段稳定的视频（人脸、建筑、植物等）
2. 运行 `python config_generator.py` 生成配置
3. 处理视频
4. 观看神奇效果！

**让不可见的世界变得可见** ✨
