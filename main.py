from core.pipeline import process_stream
from pathlib import Path
import os

if __name__ == "__main__":
    model_load_path = r"E:\UVR5-UI\models"

    model_path = Path(model_load_path)
    model_names = []
    def model_chooser(model_path):
        for model in model_path.rglob("*"):
            if model.is_file() and model.suffix.lower() in [".pth", ".onnx", ".ckpt"]:
                model_names.append([model.name])
    
        model_sort = {}
        for i in range(len(model_names)):
            print(f"{i}: {model_names[i][0]}")
            model_sort[i] = model_names[i]

        return model_sort
    def model_select(model_load_path,result_output,music_path,s:int):
        for i in range(s):
            print(":#^20".format("第{}轮选择".format(i+1)))
            model_sort = model_chooser(model_path)
            while True:
                try:
                    model_index = int(input("请输入要使用的模型序号: ").strip())
                    if model_index in model_sort:
                        print(f"✅ 已选择模型: {model_sort[model_index]}")
                        process = process_stream(model_load_path, result_output,music_path,model_sort[model_index])
                        try:
                           vocals_file = process.start()

                           process.exit()
                        except Exception as e:
                            print(f"❌ 处理过程中发生错误: {e}")
                        finally:
                            process.exit()
                        music_path = vocals_file
                        break
                    else:
                        print("❌ 输入的序号无效，请重新输入。")
                except ValueError:
                    print("❌ 请输入一个有效的整数序号。")

    music_path = input("请输入原始音频文件的绝对路径: ").strip().strip("\"")
    result_output = r"E:\剪辑专用\rvc训练集\result"
    s = int(input("请输入处理轮数（建议5轮）: ").strip())
    model_select(model_load_path,result_output,music_path,s)
