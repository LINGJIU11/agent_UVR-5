from core.模型加载类 import MODEL_LOAD
from core.流程逻辑基础 import stream_build
import os
import shutil
import uuid
import gc
import torch


def create_task_folder(base_path: str, name: str = "task") -> str:
    """在 base_path 下创建一个随机子文件夹，返回完整路径"""
    os.makedirs(base_path, exist_ok=True)
    while True:
        folder_name = f"{name}_{uuid.uuid4().hex[:12]}"
        folder_path = os.path.join(base_path, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=False)
            return folder_path
        except FileExistsError:
            continue


class process_stream:
    """单轮处理封装"""
    def __init__(self, model_load_path, result_output, music_path, model_name: list):
        self.model_load_path = model_load_path
        self.result_output = result_output
        self.music_path = music_path
        self.model_name = model_name

    def start(self):
        self.med = MODEL_LOAD(self.model_load_path, self.result_output, self.model_name)
        out_files = self.med.start(self.music_path)
        vocals_file = stream_build(out_files, self.result_output)
        return vocals_file

    def exit(self):
        if hasattr(self, 'med'):
            try:
                self.med.exit()
            finally:
                del self.med
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()


def run_pipeline(model_load_path: str,
                 base_output_dir: str,
                 music_path: str,
                 model_rounds: list,
                 progress_cb=None) -> dict:
    """
    多轮处理主流程。
    - base_output_dir: 用户提供的总输出目录，会在其中创建子文件夹
    - model_rounds: [[model1], [model2], ...] 每轮使用的模型
    - progress_cb: 回调函数 progress_cb(round_idx, total, message)
    返回 dict: {"task_dir": ..., "final_file": ...}
    """
    task_dir = create_task_folder(base_output_dir, name="audio_task")
    total = len(model_rounds)
    current_input = music_path

    for i, model_name in enumerate(model_rounds):
        if progress_cb:
            progress_cb(i + 1, total, f"第 {i+1}/{total} 轮：加载模型 {model_name}")

        proc = process_stream(model_load_path, task_dir, current_input, model_name)
        try:
            vocals_file = proc.start()
        finally:
            proc.exit()

        # 关键：把本轮人声文件重命名为干净的中间文件名，避免下一轮关键词污染
        step_file = os.path.join(task_dir, f"step_{i+1}.wav")
        if os.path.abspath(vocals_file) != os.path.abspath(step_file):
            if os.path.exists(step_file):
                os.remove(step_file)
            shutil.move(vocals_file, step_file)

        # 同时清理本轮其它产物（伴奏等），节省空间（可选）
        # 如果想保留中间产物给用户检查，可以注释掉这段
        for f in os.listdir(task_dir):
            full = os.path.join(task_dir, f)
            if os.path.isfile(full) and full != step_file and not f.startswith("step_"):
                try:
                    os.remove(full)
                except OSError:
                    pass

        current_input = step_file
        if progress_cb:
            progress_cb(i + 1, total, f"第 {i+1}/{total} 轮完成")

    # 最终重命名一下
    final_file = os.path.join(task_dir, "final_vocals.wav")
    shutil.move(current_input, final_file)

    if progress_cb:
        progress_cb(total, total, "全部完成")

    return {"task_dir": task_dir, "final_file": final_file}