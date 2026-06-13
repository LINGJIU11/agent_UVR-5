# UVR5 音频处理流水线

基于 [audio-separator](https://github.com/karaokenerds/python-audio-separator) 的多轮串联人声分离自动化工具，提供 CLI 和 Web 两种使用方式。

## 功能

- **多轮串联处理** — 依次使用不同模型逐步提纯人声（分离 → 去混响 → 去 crowd → 去噪）
- **可配置 Agent** — 保存不同的模型组合为 Agent，一键复用
- **Web 界面** — 浏览器操作，实时进度条，支持单文件和批量文件夹
- **批量处理** — 一次处理整个文件夹内所有音频

## 架构

```
用户输入音频
    │
    ▼
┌──────────────────────────────────────────┐
│  pipeline.py  (流程调度)                   │
│                                           │
│  第1轮: Roformer 分离人声                   │
│  第2轮: HP-Karaoke 进一步提取               │
│  第3轮: DeEcho 去混响                       │
│  第4轮: DeCrowd 去 crowd                   │
│  第5轮: DeNoise 去噪                        │
│                                           │
│  每轮: 加载模型 → 分离 → 找合格人声 → 清理   │
└──────────────────────────────────────────┘
    │
    ▼
纯净人声文件
```

```
项目结构:
├── server.py              Web 服务入口 (FastAPI + uvicorn)
├── main.py                CLI 交互入口
├── requirements.txt       依赖声明
├── agents.json            Agent 配置存储
├── static/
│   └── index.html         Web 前端界面
├── api/
│   ├── routes.py          REST API (Agent CRUD / 单文件 / 批量)
│   └── agent_store.py     JSON 文件存储
├── core/
│   ├── model_loader.py    封装 audio_separator.Separator
│   ├── model_scanner.py   扫描模型文件目录
│   ├── stem_finder.py     从分离输出中定位人声文件
│   ├── pipeline.py        多轮流水线核心
│   ├── batch_processor.py 批量文件夹处理
│   └── utils.py           工具函数
└── tests/                 单元测试 (29 tests)
```

## 依赖

- Python >= 3.10
- FFmpeg（系统级安装）
- PyTorch + CUDA（GPU 加速）或 CPU 模式

关键 Python 包：`audio-separator >= 0.44.1`、`fastapi`、`uvicorn`

## 安装

```bash
# 克隆仓库
git clone <repo-url>
cd UVR5流程创建

# 安装依赖（GPU 版）
pip install -r requirements.txt

# CPU 版：编辑 requirements.txt，将 audio-separator[gpu] 改为 audio-separator[cpu]
```

## 使用方式

### Web 界面（推荐）

```bash
python server.py
# 浏览器打开 http://127.0.0.1:8000
```

1. 在「扫描模型」卡片输入模型目录路径，点击扫描
2. 在「创建 Agent」卡片配置名称、路径、处理轮次，创建 Agent
3. 在「运行任务」卡片选择 Agent，输入音频路径，点击开始
4. 或在「批量处理」卡片输入整个文件夹路径，一次性处理所有文件

### CLI 命令行

```bash
python main.py
# 按提示输入原始音频路径，交互式选择模型和处理轮数
```

### 批量处理脚本

```bash
python -m core.batch_processor
# 输入文件夹路径、输出目录、模型目录即可批量处理
```

## API 参考

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/agents` | 列出所有 Agent |
| POST | `/api/agents` | 创建 Agent |
| DELETE | `/api/agents/{id}` | 删除 Agent |
| GET | `/api/models?path=` | 扫描模型目录 |
| POST | `/api/run` | 提交单文件处理任务 |
| GET | `/api/tasks/{id}` | 查询任务进度 |
| POST | `/api/batch-run` | 提交批量文件夹任务 |
| GET | `/api/batch-tasks/{id}` | 查询批量任务进度 |

### 创建 Agent 请求体示例

```json
{
  "name": "标准流程",
  "model_load_path": "E:\\UVR5-UI\\models",
  "result_output": "E:\\output",
  "rounds": [
    "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
    "5_HP-Karaoke-UVR.pth",
    "UVR-DeEcho-DeReverb.pth",
    "UVR-MDX-NET_Crowd_HQ_1.onnx",
    "UVR-DeNoise.pth"
  ]
}
```

## 预设模型流程

默认 5 轮流水线，每轮目标：

| 轮次 | 模型 | 作用 |
|---|---|---|
| 1 | `BS-Roformer` | 初次分离人声与伴奏 |
| 2 | `HP-Karaoke-UVR` | 进一步提取人声 |
| 3 | `UVR-DeEcho-DeReverb` | 去除混响/回声 |
| 4 | `UVR-MDX-NET_Crowd_HQ` | 去除 crowd / 和声 |
| 5 | `UVR-DeNoise` | 最终降噪 |

可根据需求在 Web 界面自由增减轮次和替换模型。

## 运行测试

```bash
pip install pytest
python -m pytest tests/ -v
```

---

<sub>本次代码重构与改进由 AI 辅助完成，包括：项目结构规范化、线程安全修复、日志系统引入、模块英文化、单元测试编写、批量处理整合。</sub>
