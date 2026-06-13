import os
KEYWORDS = ["vocals", "clean", "no reverb", "no crowd", "no noise"]
EXCLUDE = ["instrumental", "other", "no_vocals", "no vocals"]


def stream_build(output_files: list, output_dir: str = None):
    if not output_files:
        raise RuntimeError("分离器未返回任何文件")
    
    for file_path in output_files:
        name = os.path.basename(file_path).lower()
        if any(ex in name for ex in EXCLUDE):
            continue
        if any(k in name for k in KEYWORDS):
            # 如果 separator 返回的是相对路径，需要拼上 output_dir
            if output_dir and not os.path.isabs(file_path):
                return os.path.join(output_dir, file_path)
            return file_path
    raise RuntimeError(f"❌ 未找到人声文件，输出列表为: {output_files}")