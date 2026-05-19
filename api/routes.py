from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from core.模型权重检索 import file_check
from core.流程创建2 import run_pipeline
from .agent_store import load_agents, save_agents
import uuid, threading

router = APIRouter()
tasks: dict = {}
FILE_SUFFIXES = ['.pth', '.onnx', '.pt', '.ckpt', '.model', '.pb']


class AgentConfig(BaseModel):
    name: str
    model_load_path: str
    result_output: str
    rounds: list[str]


@router.get("/agents")
def list_agents():
    return load_agents()


@router.post("/agents")
def create_agent(config: AgentConfig):
    agents = load_agents()
    agent_id = str(uuid.uuid4())[:8]
    agents[agent_id] = config.model_dump()
    save_agents(agents)
    return {"id": agent_id}


@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    agents = load_agents()
    if agent_id not in agents:
        raise HTTPException(404, "Agent 不存在")
    del agents[agent_id]
    save_agents(agents)
    return {"ok": True}


@router.get("/models")
def scan_models(path: str):
    if not Path(path).exists():
        raise HTTPException(400, f"路径不存在: {path}")
    return file_check(path, FILE_SUFFIXES)


class RunRequest(BaseModel):
    agent_id: str
    music_path: str


def _run_task(task_id: str, agent: dict, music_path: str):
    task = tasks[task_id]
    task["status"] = "running"

    def progress_cb(cur, total, msg):
        task["current_round"] = cur
        task["total_rounds"] = total
        task["progress"] = int(cur / total * 100)
        task["message"] = msg

    try:
        rounds = [[name] for name in agent["rounds"]]  # 包成 list
        result = run_pipeline(
            agent["model_load_path"],
            agent["result_output"],
            music_path,
            rounds,
            progress_cb=progress_cb,
        )
        task["status"] = "done"
        task["task_dir"] = result["task_dir"]
        task["final_file"] = result["final_file"]
        task["progress"] = 100
        task["message"] = "处理完成"
    except Exception as e:
        task["status"] = "error"
        task["error"] = str(e)
        task["message"] = f"错误：{e}"


@router.post("/run")
def run_agent(req: RunRequest):
    agents = load_agents()
    if req.agent_id not in agents:
        raise HTTPException(404, "Agent 不存在")
    if not Path(req.music_path).exists():
        raise HTTPException(400, f"音频文件不存在: {req.music_path}")

    task_id = str(uuid.uuid4())[:8]
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
    return {"task_id": task_id}


@router.get("/tasks/{task_id}")
def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "任务不存在")
    return tasks[task_id]