"""批量文件夹音频处理"""
from core.pipeline import run_pipeline
from core.utils import create_task_folder
from pathlib import Path
import os

# 默认5轮处理模型（与 Web 端 Agent 共享同一套配置逻辑）
DEFAULT_MODEL_ROUNDS = [
    ["model_bs_roformer_ep_317_sdr_12.9755.ckpt"],
    ["5_HP-Karaoke-UVR.pth"],
    ["UVR-DeEcho-DeReverb.pth"],
    ["UVR-MDX-NET_Crowd_HQ_1.onnx"],
    ["UVR-DeNoise.pth"],
]

AUDIO_SUFFIXES = [".flac", ".wav", ".mp3", ".m4a", ".ogg"]


def batch_process_folder(input_folder: str,
                         model_load_path: str,
                         output_base: str,
                         model_rounds: list = None,
                         progress_cb=None) -> list[dict]:
    """批量处理文件夹内所有音频文件。

    Returns:
        list[dict]: 每个文件的结果 {"file": ..., "task_dir": ..., "final_file": ...}
    """
    if model_rounds is None:
        model_rounds = DEFAULT_MODEL_ROUNDS

    folder = Path(input_folder)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {input_folder}")

    results = []
    audio_files = [
        f for f in folder.rglob("*")
        if f.is_file() and f.suffix.lower() in AUDIO_SUFFIXES
    ]

    for i, audio_file in enumerate(audio_files):
        task_dir = create_task_folder(output_base, name="audio_task")
        if progress_cb:
            progress_cb(i + 1, len(audio_files),
                         f"处理中: {audio_file.name} ({i+1}/{len(audio_files)})")

        result = run_pipeline(
            model_load_path=model_load_path,
            base_output_dir=output_base,
            music_path=str(audio_file),
            model_rounds=model_rounds,
        )
        results.append({
            "file": str(audio_file),
            "task_dir": result["task_dir"],
            "final_file": result["final_file"],
        })

    return results


if __name__ == "__main__":
    files = input("请输入文件夹路径: ").strip().strip("\"")
    output_dirs = input("请输入输出目录: ").strip().strip("\"")
    model_load_path = input("请输入模型目录: ").strip().strip("\"")

    # 验证路径
    if not Path(files).exists():
        print("❌ 文件夹路径不存在！")
        exit(1)

    results = batch_process_folder(files, model_load_path, output_dirs)
    for r in results:
        print(f"✅ {Path(r['file']).name} → {r['final_file']}")
