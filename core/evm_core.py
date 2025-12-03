#!/usr/bin/env python3
"""
Eulerian Video Magnification Core Module - Windows Compatible Version
欧拉视频放大核心模块 - Windows兼容版本
"""

import numpy as np
import cv2
import subprocess
import os
from scipy import signal
from collections import deque
import concurrent.futures
import threading
import warnings
warnings.filterwarnings('ignore')

# 集成eulerian-magnification库用于频率分析
try:
    import eulerian_magnification as em
    HAS_EM_LIB = True
    print("eulerian-magnification库已加载")
except ImportError:
    HAS_EM_LIB = False
    print("eulerian-magnification库未安装，频率分析功能不可用")

# 启用numpy优化
np.seterr(all='ignore')


class EulerianVideoMagnification:
    """欧拉视频放大核心类 - Windows兼容高性能版本"""

    def __init__(self, video_path, output_path="output.mp4", buffer_size=150, num_workers=None):
        self.video_path = video_path
        self.output_path = output_path
        self.fps = None
        self.width = None
        self.height = None
        self.total_frames = None
        # 大幅减少缓冲区避免内存溢出 - 64GB都不够说明有严重问题
        self.buffer_size = min(30, buffer_size)  # 最多30帧，防止内存爆炸
        # 使用所有CPU核心，但在Windows上使用ThreadPoolExecutor更稳定
        import multiprocessing as mp
        self.num_workers = num_workers or mp.cpu_count()
        # 创建持久线程池避免重复创建开销
        self.executor = None
        print(f"初始化处理器，使用 {self.num_workers} 个工作线程")

    def __del__(self):
        """析构函数 - 确保线程池被清理"""
        self._cleanup_executor()

    def _init_executor(self):
        """初始化持久线程池"""
        if self.executor is None:
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers)

    def _cleanup_executor(self):
        """清理线程池"""
        if self.executor is not None:
            self.executor.shutdown(wait=True)
            self.executor = None

    def get_video_info(self):
        """获取视频基本信息并检测超高分辨率"""
        cap = cv2.VideoCapture(self.video_path)
        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # 计算分辨率等级和内存需求
        total_pixels = self.width * self.height
        frame_size_mb = (total_pixels * 3 * 4) / (1024 * 1024)  # float32 RGB

        print(f"视频: {self.width}x{self.height}, {self.fps}FPS, {self.total_frames}帧")
        print(f"每帧内存: {frame_size_mb:.1f}MB")

        # 超高分辨率检测和警告
        if total_pixels > 33177600:  # 8K (7680x4320)
            print(f"⚠️ 检测到超高分辨率视频 ({self.width}x{self.height})")
            print("自动启用超高分辨率优化模式...")

            # 强制减少缓冲区到最小
            self.buffer_size = min(10, self.buffer_size)
            self.is_ultra_high_res = True

            if total_pixels > 100663296:  # 12K+
                print("🚨 12K+分辨率检测！强制启用极限内存模式")
                self.buffer_size = 5  # 最小缓冲区
                self.extreme_mode = True
        else:
            self.is_ultra_high_res = False
            self.extreme_mode = False

        return self.fps, self.width, self.height

    def analyze_video_frequencies(self, max_frames=300):
        """使用eulerian-magnification库分析视频频率"""
        if not HAS_EM_LIB:
            print("eulerian-magnification库未安装，无法进行频率分析")
            return None

        try:
            print(f"\n开始频率分析...")
            print(f"分析帧数: {min(max_frames, self.total_frames)} 帧")

            # 使用OpenCV直接加载视频进行频率分析
            cap = cv2.VideoCapture(self.video_path)
            frames = []
            frame_count = 0

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # 转换为浮点数并归一化
                frame_float = frame.astype(np.float32) / 255.0
                frames.append(frame_float)
                frame_count += 1

            cap.release()

            if len(frames) < 10:
                print("视频帧数太少，无法进行频率分析")
                return None

            vid = np.array(frames)
            print(f"视频数据: {vid.shape}, FPS: {self.fps}")

            # 使用自定义频率分析函数（修复库的Python 3兼容性问题）
            print("正在分析频率成分...")
            frequency_data = self._analyze_frequencies_custom(vid, self.fps)

            # 解析频率分析结果
            if frequency_data is not None:
                # 找到主要频率成分
                dominant_frequencies = self._extract_dominant_frequencies(frequency_data, self.fps)

                print(f"\n频率分析结果:")
                for freq_info in dominant_frequencies:
                    print(f"  主要频率: {freq_info['frequency']:.2f} Hz (强度: {freq_info['magnitude']:.3f})")

                return {
                    'fps': self.fps,
                    'dominant_frequencies': dominant_frequencies,
                    'raw_data': frequency_data,
                    'analyzed_frames': len(vid)
                }
            else:
                print("频率分析失败")
                return None

        except Exception as e:
            print(f"频率分析出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _analyze_frequencies_custom(self, vid, fps):
        """自定义频率分析函数（修复Python 3兼容性问题）"""
        try:
            # 将视频转换为灰度并计算每个像素的时间序列
            if len(vid.shape) == 4:  # (frames, height, width, channels)
                # 转换为灰度
                vid_gray = np.mean(vid, axis=3)
            else:
                vid_gray = vid

            # 计算全局平均亮度的时间序列
            temporal_signal = np.mean(vid_gray, axis=(1, 2))

            # 应用FFT分析频率
            n_frames = len(temporal_signal)
            fft_result = np.fft.fft(temporal_signal)

            # 计算频率轴（修复整数除法问题）
            freqs = np.fft.fftfreq(n_frames, 1.0/fps)

            # 只取正频率部分（修复slice indices问题）
            positive_idx = n_frames // 2 + 1  # 使用整数除法
            freqs = freqs[:positive_idx]
            fft_magnitude = np.abs(fft_result[:positive_idx])

            return {
                'frequencies': freqs,
                'magnitudes': fft_magnitude,
                'temporal_signal': temporal_signal
            }

        except Exception as e:
            print(f"自定义频率分析出错: {e}")
            return None

    def _extract_dominant_frequencies(self, frequency_data, fps, top_n=5):
        """从频率数据中提取主要频率成分"""
        try:
            # 处理自定义频率分析的返回格式
            if isinstance(frequency_data, dict) and 'frequencies' in frequency_data:
                freqs = frequency_data['frequencies']
                magnitudes = frequency_data['magnitudes']

                # 过滤掉DC分量和过低频率
                valid_indices = np.where((freqs > 0.1) & (freqs < fps/2))[0]

                if len(valid_indices) == 0:
                    print("未找到有效的频率成分")
                    return []

                valid_freqs = freqs[valid_indices]
                valid_magnitudes = magnitudes[valid_indices]

                # 找到最强的频率成分
                peak_indices = np.argsort(valid_magnitudes)[-top_n:][::-1]

                dominant_frequencies = []
                for idx in peak_indices:
                    if idx < len(valid_freqs):
                        dominant_frequencies.append({
                            'frequency': valid_freqs[idx],
                            'magnitude': valid_magnitudes[idx],
                            'index': valid_indices[idx]
                        })

                return dominant_frequencies
            else:
                print("未知的频率数据格式")
                return []

        except Exception as e:
            print(f"提取主要频率时出错: {e}")
            import traceback
            traceback.print_exc()
            return []

    def suggest_frequency_range(self, analysis_result=None):
        """基于频率分析结果建议最佳频率范围"""
        if analysis_result is None:
            analysis_result = self.analyze_video_frequencies()

        if analysis_result is None or not analysis_result['dominant_frequencies']:
            print("⚠️ 无频率分析数据，使用默认范围")
            return {'freq_low': 0.4, 'freq_high': 3.0, 'confidence': 'low'}

        dominant_freqs = analysis_result['dominant_frequencies']

        # 找到最强的频率成分
        strongest_freq = dominant_freqs[0]['frequency']

        # 基于最强频率建议范围
        if strongest_freq < 1.0:
            # 低频运动 (如呼吸)
            suggested_low = max(0.1, strongest_freq - 0.3)
            suggested_high = min(2.0, strongest_freq + 0.5)
            motion_type = "呼吸或慢速运动"
        elif strongest_freq < 3.0:
            # 中频运动 (如心跳)
            suggested_low = max(0.5, strongest_freq - 0.5)
            suggested_high = min(4.0, strongest_freq + 1.0)
            motion_type = "心跳或中速运动"
        else:
            # 高频运动
            suggested_low = max(1.0, strongest_freq - 1.0)
            suggested_high = min(8.0, strongest_freq + 2.0)
            motion_type = "快速运动或振动"

        print(f"\n建议的频率范围:")
        print(f"  检测到主要频率: {strongest_freq:.2f} Hz ({motion_type})")
        print(f"  建议范围: {suggested_low:.1f} - {suggested_high:.1f} Hz")

        return {
            'freq_low': suggested_low,
            'freq_high': suggested_high,
            'dominant_frequency': strongest_freq,
            'motion_type': motion_type,
            'confidence': 'high'
        }

    def build_gaussian_pyramid(self, frame, levels=4):
        """构建高斯金字塔 - cv2优化版本"""
        pyramid = [frame.astype(np.float32)]
        current = frame.astype(np.float32)

        # 使用cv2.pyrDown，比scipy更快且更稳定
        for i in range(levels - 1):
            current = cv2.pyrDown(current)
            pyramid.append(current)
        return pyramid

    def build_laplacian_pyramid(self, frame, levels=4):
        """构建拉普拉斯金字塔 - 正确的运动放大方法"""
        # 先构建高斯金字塔
        gaussian_pyramid = self.build_gaussian_pyramid(frame, levels)

        # 构建拉普拉斯金字塔
        laplacian_pyramid = []

        for i in range(levels - 1):
            # 上采样下一层
            size = (gaussian_pyramid[i].shape[1], gaussian_pyramid[i].shape[0])
            upsampled = cv2.pyrUp(gaussian_pyramid[i + 1], dstsize=size)

            # 拉普拉斯层 = 当前高斯层 - 上采样的下一层
            laplacian = gaussian_pyramid[i] - upsampled
            laplacian_pyramid.append(laplacian)

        # 最后一层就是高斯金字塔的最后一层（最粗糙的层）
        laplacian_pyramid.append(gaussian_pyramid[-1])

        return laplacian_pyramid

    def apply_temporal_bandpass_filter_fft(self, data, fps, freq_low, freq_high, amplification=1):
        """使用FFT进行时域带通滤波 - 参考eulerian_magnification库的正确实现"""
        try:
            # data shape: (frames, height, width, channels)
            print(f"应用FFT带通滤波: {freq_low}-{freq_high} Hz, 放大倍数: {amplification}x")

            # 使用实数FFT（更高效）
            fft = np.fft.rfft(data, axis=0)
            frequencies = np.fft.fftfreq(data.shape[0], d=1.0 / fps)

            # 找到频率边界的索引
            bound_low = (np.abs(frequencies - freq_low)).argmin()
            bound_high = (np.abs(frequencies - freq_high)).argmin()

            # 创建带通滤波器：只保留指定频率范围
            fft[:bound_low] = 0
            fft[bound_high:-bound_high] = 0
            fft[-bound_low:] = 0

            # 逆FFT恢复时域信号
            result = np.fft.irfft(fft, n=data.shape[0], axis=0)

            # 应用放大系数
            result = result.real * amplification

            return result.astype(np.float32)

        except Exception as e:
            print(f"FFT滤波出错: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros_like(data)

    def create_laplacian_video_pyramid(self, video_frames, levels=4):
        """创建整个视频的拉普拉斯金字塔 - 参考库的正确实现"""
        print(f"构建拉普拉斯视频金字塔，层数: {levels}")

        vid_pyramid = []
        frame_count = len(video_frames)

        # 对每一帧构建金字塔
        for frame_idx, frame in enumerate(video_frames):
            frame_pyramid = self.build_laplacian_pyramid(frame, levels)

            # 初始化金字塔结构
            if frame_idx == 0:
                for level in range(levels):
                    h, w = frame_pyramid[level].shape[:2]
                    vid_pyramid.append(np.zeros((frame_count, h, w, 3), dtype=np.float32))

            # 将当前帧的每层添加到对应的视频金字塔层
            for level in range(levels):
                vid_pyramid[level][frame_idx] = frame_pyramid[level]

            if (frame_idx + 1) % 50 == 0:
                print(f"  已处理 {frame_idx + 1}/{frame_count} 帧")

        return vid_pyramid

    def collapse_laplacian_pyramid(self, image_pyramid):
        """坍缩拉普拉斯金字塔为单张图像 - 参考库实现"""
        # 从最粗糙的层开始
        img = image_pyramid[-1].copy()

        # 逐层上采样并累加
        for level in range(len(image_pyramid) - 2, -1, -1):
            target_shape = image_pyramid[level].shape
            size = (target_shape[1], target_shape[0])
            img = cv2.pyrUp(img, dstsize=size)
            img = img + image_pyramid[level]

        return img

    def collapse_laplacian_video_pyramid(self, vid_pyramid):
        """坍缩拉普拉斯视频金字塔 - 参考库实现"""
        print("坍缩拉普拉斯视频金字塔...")
        frame_count = vid_pyramid[0].shape[0]
        result_frames = []

        for frame_idx in range(frame_count):
            # 提取当前帧的所有金字塔层
            img_pyramid = [vid[frame_idx] for vid in vid_pyramid]

            # 坍缩金字塔
            collapsed = self.collapse_laplacian_pyramid(img_pyramid)
            result_frames.append(collapsed)

            if (frame_idx + 1) % 50 == 0:
                print(f"  已坍缩 {frame_idx + 1}/{frame_count} 帧")

        return np.array(result_frames)

    def eulerian_magnification_correct(self, video_frames, fps, freq_low, freq_high,
                                      amplification, levels=4, skip_levels_at_top=2):
        """正确的欧拉视频放大实现 - 完全参考eulerian_magnification库"""
        print(f"\n=== 欧拉视频放大（正确实现） ===")
        print(f"帧数: {len(video_frames)}, FPS: {fps}")
        print(f"频率范围: {freq_low}-{freq_high} Hz")
        print(f"放大倍数: {amplification}x")
        print(f"金字塔层数: {levels}, 跳过顶层: {skip_levels_at_top}")

        # 1. 构建拉普拉斯视频金字塔
        vid_pyramid = self.create_laplacian_video_pyramid(video_frames, levels)

        # 2. 对每层金字塔进行时域带通滤波和放大
        for level_idx in range(len(vid_pyramid)):
            # 跳过顶层（噪声太多）和底层（高斯表示）
            if level_idx < skip_levels_at_top or level_idx >= len(vid_pyramid) - 1:
                print(f"  跳过第 {level_idx} 层")
                continue

            print(f"  处理第 {level_idx} 层...")

            # 应用FFT带通滤波
            bandpassed = self.apply_temporal_bandpass_filter_fft(
                vid_pyramid[level_idx], fps, freq_low, freq_high, amplification
            )

            # 将滤波后的信号加回原始金字塔层
            vid_pyramid[level_idx] = vid_pyramid[level_idx] + bandpassed

        # 3. 坍缩金字塔重建视频
        result_frames = self.collapse_laplacian_video_pyramid(vid_pyramid)

        # 4. 裁剪到有效范围
        result_frames = np.clip(result_frames, 0, 1)

        print("✅ 欧拉视频放大完成")
        return result_frames

    def _process_frame_batch_memory_safe(self, frame_batch, pyramid_buffers, mode, levels,
                                       freq_low, freq_high, amplification):
        """流式处理已废弃 - 直接返回原始帧"""
        # 注意：流式处理方法已废弃，请使用批处理方法（load_video + magnify_motion/color）
        # 这里只是为了兼容性，直接返回原始帧
        print("⚠️ 警告：流式处理方法已废弃，请使用批处理方法以获得正确的运动放大效果")
        return frame_batch

    def process_streaming(self, mode='motion', freq_low=0.4, freq_high=3.0,
                         amplification=10, levels=4, max_frames=None,
                         progress_callback=None):
        """内存安全流式处理视频"""
        print(f"\n开始{mode}放大处理...")
        print(f"频率范围: {freq_low}-{freq_high} Hz, 放大倍数: {amplification}x")

        # 单帧处理避免内存积累
        batch_size = 1

        # 内存监控
        import psutil
        import gc
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024

        # 打开输入视频
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")

        # 创建临时输出文件 - 12K分辨率需要特殊处理
        temp_video = self.output_path.replace('.mp4', '_temp.mp4')

        # 超高分辨率使用更稳定的编码器
        if hasattr(self, 'extreme_mode') and self.extreme_mode:
            print("🚨 12K模式：使用无损编码器避免数据损坏")
            fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # 无损编码器
        elif hasattr(self, 'is_ultra_high_res') and self.is_ultra_high_res:
            print("⚠️ 8K+模式：使用高质量编码器")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 更稳定的编码器
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        out = cv2.VideoWriter(temp_video, fourcc, self.fps, (self.width, self.height))

        # 验证VideoWriter是否成功初始化
        if not out.isOpened():
            print("❌ VideoWriter初始化失败，尝试备用编码器...")
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # 备用编码器
            out = cv2.VideoWriter(temp_video, fourcc, self.fps, (self.width, self.height))

            if not out.isOpened():
                raise ValueError(f"无法创建输出视频文件: {temp_video}")

        # 初始化缓冲区 - 为每个金字塔层级创建缓冲区
        pyramid_buffers = [deque(maxlen=self.buffer_size) for _ in range(levels)]

        frame_count = 0
        max_process = max_frames if max_frames else self.total_frames

        # 添加时间统计
        import time
        start_time = time.time()
        last_update_time = start_time

        print(f"开始高效并行处理，批大小: {batch_size}...")

        try:
            frame_batch = []

            while True:
                # 读取帧
                ret, frame = cap.read()
                if not ret:
                    # 处理剩余批次
                    if frame_batch:
                        print(f"\n处理最后 {len(frame_batch)} 帧...")
                        results = self._process_frame_batch_memory_safe(
                            frame_batch, pyramid_buffers, mode, levels,
                            freq_low, freq_high, amplification
                        )
                        # 写入结果
                        for result in results:
                            output_uint8 = np.clip(result * 255, 0, 255).astype(np.uint8)
                            out.write(output_uint8)
                    print(f"\n读取帧完成，共处理 {frame_count} 帧")
                    break

                if frame_count >= max_process:
                    # 处理剩余批次
                    if frame_batch:
                        print(f"\n处理最后 {len(frame_batch)} 帧...")
                        results = self._process_frame_batch_memory_safe(
                            frame_batch, pyramid_buffers, mode, levels,
                            freq_low, freq_high, amplification
                        )
                        # 写入结果
                        for result in results:
                            output_uint8 = np.clip(result * 255, 0, 255).astype(np.uint8)
                            out.write(output_uint8)
                    print(f"\n达到最大帧数限制: {max_process}")
                    break

                # 转换帧格式
                frame_float = frame.astype(np.float32) / 255.0
                frame_batch.append(frame_float)

                # 更新缓冲区（单线程更新，避免竞争条件）
                self._update_buffers(frame_float, pyramid_buffers, mode, levels)

                frame_count += 1
                # 超高分辨率模式下更频繁的垃圾回收
                if hasattr(self, 'extreme_mode') and self.extreme_mode:
                    if frame_count % 1 == 0:  # 每帧都清理
                        gc.collect()
                elif hasattr(self, 'is_ultra_high_res') and self.is_ultra_high_res:
                    if frame_count % 2 == 0:  # 每2帧清理
                        gc.collect()
                else:
                    if frame_count % 5 == 0:
                        gc.collect()

                # 当批次满了时处理
                if len(frame_batch) >= batch_size:
                    # 内存安全批处理
                    results = self._process_frame_batch_memory_safe(
                        frame_batch, pyramid_buffers, mode, levels,
                        freq_low, freq_high, amplification
                    )

                    # 写入结果
                    for result in results:
                        output_uint8 = np.clip(result * 255, 0, 255).astype(np.uint8)
                        out.write(output_uint8)

                    frame_batch = []
                    current_time = time.time()

                    # 更频繁的进度更新
                    if progress_callback and (current_time - last_update_time >= 2.0):
                        try:
                            progress = (frame_count / max_process) * 100
                            elapsed = current_time - start_time
                            fps = frame_count / elapsed if elapsed > 0 else 0
                            eta = (max_process - frame_count) / fps if fps > 0 else 0

                            progress_msg = f"并行处理: {frame_count}/{max_process} ({progress:.1f}%) - {fps:.1f} FPS - ETA: {eta:.0f}s"
                            progress_callback(progress_msg)
                            last_update_time = current_time
                            print(f"\n进度更新: {progress_msg}")
                        except Exception as e:
                            print(f"\n进度更新出错: {e}")

                    # 进度显示和内存管理
                    if frame_count % 50 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        memory_growth = current_memory - initial_memory
                        elapsed = current_time - start_time
                        fps = frame_count / elapsed if elapsed > 0 else 0

                        print(f"已处理: {frame_count}/{max_process} 帧 - {fps:.1f} FPS")

                        # 内存超过阈值时清理
                        if memory_growth > 1000:
                            gc.collect()
                            for buf in pyramid_buffers:
                                buf.clear()

        except KeyboardInterrupt:
            print("\n用户中断处理")
        finally:
            cap.release()
            out.release()
            # 清理线程池
            self._cleanup_executor()

        # 最终统计
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0

        print(f"高效并行处理完成: {frame_count} 帧")
        print(f"总耗时: {total_time:.1f}秒, 平均速度: {avg_fps:.1f} FPS")
        print(f"线程数: {self.num_workers}, 理论加速比: {self.num_workers}x")
        print(f"实际加速比: {avg_fps / max(1, avg_fps / self.num_workers):.1f}x")
        return temp_video

    def _update_buffers(self, frame_float, pyramid_buffers, mode, levels):
        """更新缓冲区（线程安全）- 使用拉普拉斯金字塔"""
        if mode == 'color':
            frame_ycrcb = cv2.cvtColor(frame_float, cv2.COLOR_BGR2YCrCb)
            pyramid_buffers[0].append(frame_ycrcb)
        else:
            # 使用拉普拉斯金字塔而不是高斯金字塔
            pyramid = self.build_laplacian_pyramid(frame_float, levels)
            for level in range(levels):
                pyramid_buffers[level].append(pyramid[level])

    def magnify_motion_streaming(self, fps, freq_low=0.4, freq_high=3.0,
                               amplification=10, levels=4, max_frames=None,
                               progress_callback=None):
        """高效并行流式运动放大"""
        temp_video = self.process_streaming(
            mode='motion', freq_low=freq_low, freq_high=freq_high,
            amplification=amplification, levels=levels, max_frames=max_frames,
            progress_callback=progress_callback
        )
        return temp_video

    def magnify_color_streaming(self, fps, freq_low=0.4, freq_high=3.0,
                              amplification=20, max_frames=None,
                              progress_callback=None):
        """高效并行流式色彩放大"""
        temp_video = self.process_streaming(
            mode='color', freq_low=freq_low, freq_high=freq_high,
            amplification=amplification, levels=4, max_frames=max_frames,
            progress_callback=progress_callback
        )
        return temp_video

    def generate_output_filename(self, mode, freq_low, freq_high, amplification, output_format='mp4'):
        """生成带时间戳和参数的输出文件名"""
        import os
        from datetime import datetime

        # 获取原始文件名（不含扩展名）
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 生成参数字符串
        params = f"{mode}_amp{amplification}_freq{freq_low}-{freq_high}"

        # 根据格式设置扩展名
        format_extensions = {
            'mp4': 'mp4',
            'prores_proxy': 'mov',
            'prores_lt': 'mov',
            'prores_standard': 'mov',
            'prores_hq': 'mov',
            'prores_4444': 'mov',
            'prores_4444xq': 'mov'
        }

        ext = format_extensions.get(output_format, 'mp4')
        filename = f"{base_name}_{timestamp}_{params}.{ext}"

        # 更新输出路径
        output_dir = os.path.dirname(self.output_path)
        self.output_path = os.path.join(output_dir, filename)

        return self.output_path

    def _validate_temp_video(self, temp_video_path):
        """验证临时视频文件完整性"""
        try:
            if not os.path.exists(temp_video_path):
                return False

            # 检查文件大小
            file_size = os.path.getsize(temp_video_path)
            if file_size == 0:
                return False

            # 尝试用OpenCV读取第一帧验证文件完整性
            cap = cv2.VideoCapture(temp_video_path)
            if not cap.isOpened():
                return False

            ret, frame = cap.read()
            cap.release()

            return ret and frame is not None

        except Exception as e:
            print(f"验证临时文件时出错: {e}")
            return False

    def save_video(self, temp_video_path, audio_source=None, output_format='mp4', mode='motion',
                   freq_low=0.4, freq_high=3.0, amplification=10):
        """保存最终视频（支持多种格式）"""

        # 生成自定义文件名
        final_path = self.generate_output_filename(mode, freq_low, freq_high, amplification, output_format)
        print(f"\n保存视频到: {final_path}")

        # ProRes编码器配置
        prores_configs = {
            'prores_proxy': ['-c:v', 'prores_ks', '-profile:v', '0'],  # ProRes Proxy
            'prores_lt': ['-c:v', 'prores_ks', '-profile:v', '1'],     # ProRes LT
            'prores_standard': ['-c:v', 'prores_ks', '-profile:v', '2'], # ProRes Standard
            'prores_hq': ['-c:v', 'prores_ks', '-profile:v', '3'],     # ProRes HQ
            'prores_4444': ['-c:v', 'prores_ks', '-profile:v', '4'],   # ProRes 4444
            'prores_4444xq': ['-c:v', 'prores_ks', '-profile:v', '5']  # ProRes 4444 XQ
        }

        try:
            # 检测超高分辨率并添加FFmpeg优化参数
            is_ultra_high_res = hasattr(self, 'is_ultra_high_res') and self.is_ultra_high_res
            is_extreme_mode = hasattr(self, 'extreme_mode') and self.extreme_mode

            # 超高分辨率FFmpeg优化参数
            ultra_high_res_params = []
            if is_extreme_mode:
                print("🚨 12K模式：使用FFmpeg极限优化参数")
                ultra_high_res_params = [
                    '-threads', '0',  # 使用所有CPU线程
                    '-thread_type', 'frame+slice',  # 帧级和片级并行
                    '-max_muxing_queue_size', '9999',  # 增大缓冲区
                    '-bufsize', '20M',  # 增大编码缓冲区
                    '-maxrate', '200M'  # 增大最大码率
                ]
            elif is_ultra_high_res:
                print("⚠️ 8K+模式：使用FFmpeg高分辨率优化参数")
                ultra_high_res_params = [
                    '-threads', '0',
                    '-max_muxing_queue_size', '4096',
                    '-bufsize', '10M'
                ]

            if output_format in prores_configs:
                # ProRes格式 - 超高分辨率优化
                video_codec = prores_configs[output_format]
                if audio_source:
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_video_path, '-i', audio_source,
                        *ultra_high_res_params,
                        *video_codec, '-c:a', 'pcm_s16le', '-shortest',
                        final_path
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_video_path,
                        *ultra_high_res_params,
                        *video_codec,
                        final_path
                    ]
            else:
                # MP4格式 - 超高分辨率优化
                h264_params = ['-preset', 'medium', '-crf', '23']
                if is_extreme_mode:
                    # 12K模式使用更快的预设和更高的CRF
                    h264_params = ['-preset', 'ultrafast', '-crf', '28']
                elif is_ultra_high_res:
                    # 8K模式使用快速预设
                    h264_params = ['-preset', 'fast', '-crf', '25']

                if audio_source:
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_video_path, '-i', audio_source,
                        *ultra_high_res_params,
                        '-c:v', 'libx264', *h264_params, '-c:a', 'aac', '-shortest',
                        final_path
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_video_path,
                        *ultra_high_res_params,
                        '-c:v', 'libx264', *h264_params,
                        final_path
                    ]

            print(f"执行FFmpeg命令: {' '.join(cmd[:8])}...")  # 只显示前8个参数避免过长
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"FFmpeg错误: {result.stderr}")

                # 检查是否是超高分辨率导致的问题
                if "Invalid data found when processing input" in result.stderr:
                    print("🚨 检测到超高分辨率数据损坏问题，尝试修复...")

                    # 验证临时文件完整性
                    if self._validate_temp_video(temp_video_path):
                        print("✅ 临时文件完整，使用备用转换方法...")
                        # 使用更保守的FFmpeg参数重试
                        fallback_cmd = [
                            'ffmpeg', '-y', '-err_detect', 'ignore_err',
                            '-i', temp_video_path,
                            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '30',
                            '-avoid_negative_ts', 'make_zero',
                            final_path
                        ]
                        fallback_result = subprocess.run(fallback_cmd, capture_output=True, text=True)

                        if fallback_result.returncode == 0:
                            print("✅ 备用转换成功")
                        else:
                            print("❌ 备用转换也失败，直接复制临时文件")
                            import shutil
                            shutil.copy2(temp_video_path, final_path)
                    else:
                        print("❌ 临时文件损坏，处理失败")
                        raise ValueError("临时视频文件损坏，可能是内存不足或分辨率过高")
                else:
                    # 其他FFmpeg错误，直接复制临时文件
                    import shutil
                    shutil.copy2(temp_video_path, final_path)
                    print("使用临时文件作为输出")
            else:
                print("✅ FFmpeg转换成功")

            # 验证最终输出文件
            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                print(f"✅ 输出文件验证通过: {os.path.getsize(final_path)} 字节")
            else:
                print("❌ 输出文件验证失败")

            # 删除临时文件
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

        except Exception as e:
            print(f"保存视频时出错: {e}")
            # 如果出错，尝试直接复制临时文件
            try:
                import shutil
                shutil.copy2(temp_video_path, self.output_path)
                print("使用临时文件作为输出")
            except:
                print("无法保存视频文件")
                raise

        print(f"完成! 视频已保存: {self.output_path}")

    # 保留旧的接口以兼容现有代码
    def load_video(self, max_frames=None):
        """加载视频帧到内存"""
        print(f"加载视频: {self.video_path}")
        if max_frames and max_frames > 500:
            print(f"⚠️ 帧数过多({max_frames})，强制限制为500帧以避免内存溢出")
            max_frames = 500

        cap = cv2.VideoCapture(self.video_path)
        frames = []
        frame_count = 0
        max_load = max_frames if max_frames else min(500, self.total_frames)

        while True:
            ret, frame = cap.read()
            if not ret or frame_count >= max_load:
                break
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)
            frame_count += 1

            if frame_count % 50 == 0:
                print(f"  已加载 {frame_count}/{max_load} 帧")

        cap.release()
        print(f"✅ 加载完成: {len(frames)} 帧")
        return np.array(frames)

    def magnify_motion(self, frames, fps, freq_low=0.4, freq_high=3.0,
                       amplification=10, levels=4, skip_levels_at_top=2):
        """运动放大 - 使用正确的欧拉视频放大算法"""
        print(f"\n=== 运动放大 ===")
        return self.eulerian_magnification_correct(
            frames, fps, freq_low, freq_high, amplification, levels, skip_levels_at_top
        )

    def magnify_color(self, frames, fps, freq_low=0.4, freq_high=3.0,
                     amplification=20, levels=4, skip_levels_at_top=2):
        """色彩放大 - 使用正确的欧拉视频放大算法"""
        print(f"\n=== 色彩放大 ===")
        # 色彩放大通常使用更高的放大倍数和更宽的频率范围
        return self.eulerian_magnification_correct(
            frames, fps, freq_low, freq_high, amplification, levels, skip_levels_at_top
        )

    def save_video_from_frames(self, frames, audio_source=None, output_format='mp4', mode='motion',
                              freq_low=0.4, freq_high=3.0, amplification=10):
        """从帧数组保存视频"""
        print(f"\n保存视频...")

        # 生成输出文件名
        final_path = self.generate_output_filename(mode, freq_low, freq_high, amplification, output_format)

        # 创建临时视频文件
        temp_video = final_path.replace('.mp4', '_temp.mp4').replace('.mov', '_temp.mov')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, self.fps, (self.width, self.height))

        if not out.isOpened():
            raise ValueError(f"无法创建临时视频文件: {temp_video}")

        # 写入帧
        for idx, frame in enumerate(frames):
            output_uint8 = np.clip(frame * 255, 0, 255).astype(np.uint8)
            out.write(output_uint8)

            if (idx + 1) % 50 == 0:
                print(f"  已写入 {idx + 1}/{len(frames)} 帧")

        out.release()
        print(f"✅ 临时视频已创建: {temp_video}")

        # 使用FFmpeg转换为最终格式
        self.save_video(temp_video, audio_source, output_format, mode, freq_low, freq_high, amplification)

        return final_path