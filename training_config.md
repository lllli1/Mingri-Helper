# YOLO训练配置文档

## 训练环境配置

**硬件要求**:
- GPU: 支持CUDA的NVIDIA显卡（建议GTX 1060及以上）
- 显存: 至少4GB
- CPU: 多核处理器
- 内存: 16GB RAM

**软件配置**:
- 操作系统: Windows 10/11
- Python: 3.8-3.11
- CUDA: 11.7或11.8
- cuDNN: 8.5+
- PyTorch: GPU版本
- Ultralytics YOLO: 最新版本

## 训练参数设置

**GPU配置**:
- device: 0  # 使用第一个GPU
- workers: 6  # 数据加载线程数
- batch-size: 根据显存大小自动调整

**训练命令示例**:
```bash
yolo train model=yolov8n.pt data=dataset.yaml epochs=100 imgsz=640 device=0 workers=6
```

**注意事项**:
1. 确保已安装正确的CUDA驱动
2. 安装PyTorch GPU版本: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
3. 安装Ultralytics: `pip install ultralytics`
4. 监控GPU使用情况，避免内存溢出
5. 建议使用虚拟环境隔离依赖