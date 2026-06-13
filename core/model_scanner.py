import os
from pathlib import Path

model_load_file = r"E:\UVR5-UI\models"
file_name_suffix = ['.pth', '.onnx', '.pt', '.ckpt', '.model', '.pb']

def file_check(path,file_name):
    model_files = []
    folder = Path(path) #folder是一个path对象
    if not folder.exists():
        print(f"错误！路径{path}不存在")
        return {}
    for file in folder.rglob("*"): #检索该对象的下的文件，遍历
        if file.is_file() and file.suffix.lower() in file_name:
            model_files.append(str(file))
    model_files_items = {}
    for i in range(len(model_files)):
        model_files_items[i] = model_files[i]

    return model_files_items

"""if __name__ == "__main__":
    model = file_check(model_load_file,file_name_suffix)
    print(model)"""