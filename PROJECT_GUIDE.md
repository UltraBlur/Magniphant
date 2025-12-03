# 欧拉视频放大 VideoArt 工具包

## 📁 文件清单

### 核心程序
- **eulerian_video_magnification.py** - 主程序，包含完整的EVM算法实现
  - 运动放大、色彩放大、混合模式
  - 支持命令行参数和配置文件
  - 灵活的处理选项

### 辅助工具
- **advanced_examples.py** - 10个高级创作示例
  - 心跳可视化
  - 呼吸放大
  - 建筑振动
  - 迷幻艺术
  - 选择性区域处理
  - 多频段分层
  - 时间对比
  - 空间渐变
  - 音乐同步
  - 极端抽象

- **config_generator.py** - 交互式配置生成器
  - 根据拍摄对象自动推荐参数
  - 生成配置文件和命令行
  - 适合初学者快速上手

- **quick_test.py** - 快速测试工具
  - 检查依赖环境
  - 生成测试视频
  - 运行端到端测试
  - 验证安装是否正确

### 配置和文档
- **presets.json** - 预设参数库
  - 15+种预设效果
  - 详细的参数说明
  - 拍摄技巧
  - 故障排除指南

- **README.md** - 完整文档
  - 安装说明
  - 使用教程
  - 参数详解
  - 创意指南
  - 故障排除

- **requirements.txt** - Python依赖列表

## 🚀 快速开始流程

### 1. 安装依赖
```bash
pip install -r requirements.txt --break-system-packages
# 安装FFmpeg (根据你的系统)
```

### 2. 检查环境
```bash
python quick_test.py
# 选择选项1: 检查依赖
```

### 3. 生成配置（推荐新手）
```bash
python config_generator.py
# 根据提示选择你的拍摄对象和效果
```

### 4. 处理视频
```bash
# 方法1: 使用生成的配置
python eulerian_video_magnification.py input.mp4 -c my_config.json

# 方法2: 直接使用命令行参数
python eulerian_video_magnification.py input.mp4 -o output.mp4 -m motion -a 20 -fl 0.5 -fh 3.0

# 方法3: 运行示例脚本
python advanced_examples.py
```

### 5. 测试和实验
```bash
python quick_test.py
# 选择选项4: 全部执行
# 这会生成测试视频并自动处理，让你看到效果
```

## 📖 学习路径

### 初学者
1. 阅读 README.md 了解基本概念
2. 运行 quick_test.py 查看示例效果
3. 使用 config_generator.py 生成适合你的配置
4. 用自己的视频测试

### 进阶用户
1. 研究 presets.json 中的各种预设
2. 运行 advanced_examples.py 学习高级技巧
3. 修改参数进行实验
4. 组合多种效果

### 专业创作
1. 直接修改 eulerian_video_magnification.py
2. 创建自定义处理流程
3. 实现空间遮罩和分层效果
4. 与其他工具结合（After Effects, Premiere等）

## 💡 创意方向

### VideoArt应用场景
- 🎵 音乐MV - 让视觉随节奏律动
- 🎬 实验电影 - 超现实视觉语言
- 🖼️ 艺术装置 - 互动视频展览
- 📺 纪录片 - 可视化不可见的现象
- 🎮 游戏艺术 - 独特的视觉风格
- 💊 医疗可视化 - 生命体征展示
- 🏗️ 建筑分析 - 结构振动检测

### 拍摄建议
- **稳定性**: 三脚架必备（除非故意要抖动效果）
- **光线**: 稳定的照明，避免闪烁
- **帧率**: 越高越好（60fps+）
- **时长**: 至少10秒以上
- **对比度**: 清晰的主体和背景

### 后期组合
- EVM + 慢动作 = 极致的微观世界
- EVM + 延时摄影 = 压缩时间中的隐秘律动
- EVM + 色彩分级 = 增强艺术表现力
- EVM + 音频反应 = 视听同步艺术

## 🛠️ 技术支持

### 常见问题
1. **效果不明显**: 增加放大倍数或检查频率范围
2. **太多噪点**: 降低放大倍数，确保拍摄稳定
3. **处理太慢**: 减少帧数或降低分辨率
4. **色彩失真**: 尝试运动模式或降低参数

### 参数调优
- 从小参数开始（amplification=10）
- 逐步增加观察效果
- 对比不同金字塔层数
- 尝试不同频率范围

### 获取帮助
```bash
# 查看完整帮助
python eulerian_video_magnification.py --help

# 查看示例
python advanced_examples.py

# 交互式配置
python config_generator.py
```

## 📦 文件依赖关系

```
eulerian_video_magnification.py (核心)
    ↑
    ├── advanced_examples.py (使用核心功能)
    ├── quick_test.py (测试核心功能)
    └── config_generator.py (生成核心所需配置)

presets.json (参考数据)
    ↑
    └── config_generator.py (读取预设)

README.md (文档)
requirements.txt (依赖)
```

## 🎨 开始创作！

所有工具已准备就绪，现在可以：

1. **快速测试**: `python quick_test.py`
2. **生成配置**: `python config_generator.py`
3. **运行示例**: `python advanced_examples.py`
4. **处理视频**: `python eulerian_video_magnification.py your_video.mp4 -o output.mp4 [参数]`

祝创作愉快！让不可见的世界变得可见 🌟
