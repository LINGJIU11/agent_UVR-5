"""通用工具函数（无重依赖）"""
import os
import uuid


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
