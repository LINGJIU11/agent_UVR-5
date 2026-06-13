import logging
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from core.model_scanner import file_check
from core.pipeline import run_pipeline
from core.batch_processor import batch_process_folder, AUDIO_SUFFIXES
from .agent_store import load_agents, save_agents

logger = logging.getLogger("uvr5.api")

router = APIRouter()

# 单文件任务存储 + 线程锁
tasks: dict = {}
_tasks_lock = threading.Lock()

# 批量任务存储 + 线程锁
batch_tasks: dict = {}
_batch_tasks_lock = threading.Lock()

FILE_SUFFIXES = ['.pth', '.onnx', '.pt', '.ckpt', '.model', '.pb']

# 需要去掉的引号字符（含中英文）
_PATH_QUOTE_CHARS = {'"', "'", '“', '”', '‘', '’'}


def _sanitize_path(v: str) -> str:
    """清理路径两端可能存在的引号、空格、换行符"""
    if not v:
        return v
    v = v.strip()
    # 循环去掉多层引号（用户可能粘贴了多层嵌套）
    while v and (v[0] in _PATH_QUOTE_CHARS or v[-1] in _PATH_QUOTE_CHARS):
        changed = False
        if v[0] in _PATH_QUOTE_CHARS:
            v = v[1:]
            changed = True
        if v and v[-1] in _PATH_QUOTE_CHARS:
            v = v[:-1]
            changed = True
        if not changed:
            break
        v = v.strip()
    return v


class AgentConfig(BaseModel):
    name: str
    model_load_path: str
    result_output: str
    rounds: list[str]


# ── Agent CRUD ──────────────────────────────────────────────

@router.get("/agents")
def list_agents():
    return load_agents()


@router.post("/agents")
def create_agent(config: AgentConfig):
    agents = load_agents()
    agent_id = str(uuid.uuid4())[:8]
    agents[agent_id] = config.model_dump()
    save_agents(agents)
    logger.info(f"Agent 创建成功: {agent_id} ({config.name}), {len(config.rounds)} 轮")
    return {"id": agent_id}


@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    agents = load_agents()
    if agent_id not in agents:
        raise HTTPException(404, "Agent 不存在")
    del agents[agent_id]
    save_agents(agents)
    logger.info(f"Agent 已删除: {agent_id}")
    return {"ok": True}


# ── 模型扫描 ────────────────────────────────────────────────

@router.get("/models")
def scan_models(path: str):
    path = _sanitize_path(path)
    if not Path(path).exists():
        raise HTTPException(400, f"路径不存在: {path}")
    return file_check(path, FILE_SUFFIXES)


# ── 任务执行 ────────────────────────────────────────────────

class RunRequest(BaseModel):
    agent_id: str
    music_path: str

    @field_validator('music_path')
    @classmethod
    def clean_music_path(cls, v: str) -> str:
        return _sanitize_path(v)


def _run_task(task_id: str, agent: dict, music_path: str):
    with _tasks_lock:
        task = tasks[task_id]
        task["status"] = "running"

    def progress_cb(cur, total, msg):
        with _tasks_lock:
            t = tasks.get(task_id)
            if t:
                t["current_round"] = cur
                t["total_rounds"] = total
                t["progress"] = int(cur / total * 100)
                t["message"] = msg

    logger.info(f"任务 {task_id} 开始: agent={agent.get('name')}, music={music_path}")
    try:
        rounds = [[name] for name in agent["rounds"]]
        result = run_pipeline(
            agent["model_load_path"],
            agent["result_output"],
            music_path,
            rounds,
            progress_cb=progress_cb,
        )
        with _tasks_lock:
            t = tasks.get(task_id)
            if t:
                t["status"] = "done"
                t["task_dir"] = result["task_dir"]
                t["final_file"] = result["final_file"]
                t["progress"] = 100
                t["message"] = "处理完成"
        logger.info(f"任务 {task_id} 完成: {result['final_file']}")
    except Exception as e:
        with _tasks_lock:
            t = tasks.get(task_id)
            if t:
                t["status"] = "error"
                t["error"] = str(e)
                t["message"] = f"错误：{e}"
        logger.error(f"任务 {task_id} 失败: {e}", exc_info=True)


@router.post("/run")
def run_agent(req: RunRequest):
    agents = load_agents()
    if req.agent_id not in agents:
        raise HTTPException(404, "Agent 不存在")
    if not Path(req.music_path).exists():
        raise HTTPException(400, f"音频文件不存在: {req.music_path}")

    task_id = str(uuid.uuid4())[:8]
    with _tasks_lock:
        tasks[task_id] = {
            "status": "pending",
            "current_round": 0,
            "total_rounds": len(agents[req.agent_id]["rounds"]),
            "progress": 0,
            "message": "排队中...",
            "final_file": None,
            "task_dir": None,
            "error": None,
        }

    threading.Thread(
        target=_run_task,
        args=(task_id, agents[req.agent_id], req.music_path),
        daemon=True,
    ).start()
    logger.info(f"任务 {task_id} 已入队")
    return {"task_id": task_id}


@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    with _tasks_lock:
        if task_id not in tasks:
            raise HTTPException(404, "任务不存在")
        # 返回副本，避免外部修改
        return dict(tasks[task_id])


# ── 批量处理 ────────────────────────────────────────────────

class BatchRunRequest(BaseModel):
    agent_id: str
    folder_path: str

    @field_validator('folder_path')
    @classmethod
    def clean_folder_path(cls, v: str) -> str:
        return _sanitize_path(v)


def _run_batch_task(batch_task_id: str, agent: dict, folder_path: str):
    with _batch_tasks_lock:
        bt = batch_tasks[batch_task_id]
        bt["status"] = "running"

    def progress_cb(cur, total, msg):
        with _batch_tasks_lock:
            bt = batch_tasks.get(batch_task_id)
            if bt:
                bt["completed_files"] = cur
                bt["total_files"] = total
                bt["progress"] = int(cur / total * 100) if total else 0
                bt["message"] = msg

    logger.info(f"批量任务 {batch_task_id} 开始: agent={agent.get('name')}, folder={folder_path}")
    try:
        rounds = [[name] for name in agent["rounds"]]
        results = batch_process_folder(
            input_folder=folder_path,
            model_load_path=agent["model_load_path"],
            output_base=agent["result_output"],
            model_rounds=rounds,
            progress_cb=progress_cb,
        )
        with _batch_tasks_lock:
            bt = batch_tasks.get(batch_task_id)
            if bt:
                bt["status"] = "done"
                bt["results"] = results
                bt["progress"] = 100
                bt["message"] = f"全部完成，共处理 {len(results)} 个文件"
        logger.info(f"批量任务 {batch_task_id} 完成: {len(results)} 个文件")
    except Exception as e:
        with _batch_tasks_lock:
            bt = batch_tasks.get(batch_task_id)
            if bt:
                bt["status"] = "error"
                bt["error"] = str(e)
                bt["message"] = f"错误：{e}"
        logger.error(f"批量任务 {batch_task_id} 失败: {e}", exc_info=True)


@router.post("/batch-run")
def run_batch(req: BatchRunRequest):
    agents = load_agents()
    if req.agent_id not in agents:
        raise HTTPException(404, "Agent 不存在")
    if not Path(req.folder_path).exists():
        raise HTTPException(400, f"文件夹不存在: {req.folder_path}")

    batch_task_id = str(uuid.uuid4())[:8]
    with _batch_tasks_lock:
        batch_tasks[batch_task_id] = {
            "status": "pending",
            "total_files": 0,
            "completed_files": 0,
            "progress": 0,
            "message": "排队中...",
            "results": None,
            "error": None,
        }

    threading.Thread(
        target=_run_batch_task,
        args=(batch_task_id, agents[req.agent_id], req.folder_path),
        daemon=True,
    ).start()
    logger.info(f"批量任务 {batch_task_id} 已入队")
    return {"batch_task_id": batch_task_id}


@router.get("/batch-tasks/{batch_task_id}")
def get_batch_task(batch_task_id: str):
    with _batch_tasks_lock:
        if batch_task_id not in batch_tasks:
            raise HTTPException(404, "批量任务不存在")
        return dict(batch_tasks[batch_task_id])
