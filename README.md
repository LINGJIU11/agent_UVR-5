# agent_UVR-5

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

基于 UVR5 模型的**流程化歌曲处理工具**，提供 Web 控制台，支持多模型串联、自由配置处理轮数，一键完成批量音乐清洗。

---

## ✨ 特性

- 🎛️ **Web 控制台** — 浏览器操作，无需命令行
- 🔗 **多模型流水线** — 按需串联多个 UVR5 模型，自定义处理轮数
- ⚡ **GPU 加速** — 支持 NVIDIA CUDA，处理速度大幅提升
- 📂 **批量处理** — 一次输入多个文件，自动逐个清洗
- 🧹 **专注人声/伴奏分离** — 基于 UVR5 的 SOTA 分离效果

---

## 🖥️ 环境要求

| 项目 | 说明 |
|------|------|
| 操作系统 | Windows 11 |
| Python | 3.12.9 |
| GPU | NVIDIA（CUDA 12.1） |
| AMD | 未测试，理论可跑 CPU 模式 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/agent_UVR-5.git
cd agent_UVR-5
```

### 2. 创建虚拟环境

```bash
python -m venv my_venv
my_venv\Scripts\activate.bat
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> ⚠️ 默认安装 CPU 版 PyTorch。如需 GPU 加速，请根据你的 CUDA 版本手动安装对应版本：
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```

### 4. 启动服务

```bash
python server.py
```

### 5. 打开控制台

浏览器访问：**http://127.0.0.1:8000/**

---

## 📖 使用指南

### Step 1 — 配置模型路径

在输入框中填入你本地 UVR5 模型的存储路径。

![模型路径配置](<屏幕截图 2026-05-19 193650-1.png>)

### Step 2 — 搭建处理流水线

按需求依次选择模型，自由控制处理轮数。完成后点击 **「创建 Agent」**。

![模型流水线配置](<屏幕截图 2026-05-19 193703.png>)

### Step 3 — 选择文件并开始

在输入框中填入需要清洗的音乐文件路径（支持多个），点击 **「开始」** 即可。

处理完成后 Web 界面会提示结果，在目标文件夹中获取最终文件。

---

## ⚠️ 注意事项

- **模型流水线未必精细** — 串联处理的效果取决于模型组合，复杂歌曲可能需要手动调参
- **暂不支持模型参数控制** — 当前版本使用模型默认参数，后期混音较重的歌曲可能出现处理效果不佳
- **仅测试 Windows + NVIDIA** — AMD 显卡 / macOS / Linux 未验证

---

## 🗺️ 路线图

- [ ] 模型参数自定义（窗口大小、FFT、阈值等）
- [ ] 处理预设保存/加载
- [ ] 进度条与预估剩余时间
- [ ] 多平台兼容（Linux / macOS）

---

## 📄 许可

[MIT](LICENSE)
