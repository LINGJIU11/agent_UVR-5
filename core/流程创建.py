from core.模型加载类 import MODEL_LOAD
import os
import shutil
import gc
import torch
import uuid
load_name = [["model_bs_roformer_ep_317_sdr_12.9755.ckpt"],["5_HP-Karaoke-UVR.pth"],["UVR-DeEcho-DeReverb.pth"],["UVR-MDX-NET_Crowd_HQ_1.onnx"],["UVR-DeNoise.pth"]]

def process_build(model_load_path, output_dir, input_music_file):
    """
    input_music_file: 原始音频的绝对路径
    """
    os.makedirs(output_dir, exist_ok=True)

    current_input = input_music_file

    for i in range(5):
        print(f"\n========== 🚀 正在执行第 {i + 1}/5 轮处理 ==========")
        print(f"使用的模型: {load_name[i]}")

        med = MODEL_LOAD(model_load_path, output_dir, model_name=load_name[i])

        out_files = med.start(current_input)

        vocals_file = None
        for file_name in out_files:
            lower_name = file_name.lower()
            # 兼容 UVR 不同模型的输出命名习惯
            if "vocals" in lower_name or "clean" in lower_name or "no reverb"  in lower_name or "no crowd" in lower_name or "no noise" in lower_name:
                # 返回的通常是相对文件名，需要和输出目录拼接
                vocals_file = os.path.join(output_dir, file_name)
                break

        if vocals_file is None:
            raise RuntimeError(f"❌ 第 {i + 1} 轮未找到人声文件，本轮输出列表为: {out_files}")

        step_temp_file = os.path.join(output_dir, f"step_{i+1}_temp_.wav")
        shutil.move(vocals_file, step_temp_file)

        current_input = step_temp_file
        print(f"✅ 第 {i + 1} 轮完成！本轮纯净人声已准备为 -> {step_temp_file}")

        del med
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    print(f"\n🎉 所有处理完毕！最终的纯净人声文件路径为: {current_input}")
    return current_input

def create_random_folder_uuid(base_path,name):
    """
    在 base_path 下创建一个随机名称的文件夹。
    返回创建成功的文件夹完整路径。
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)  # 确保基础路径存在
    while True:
        folder_name = "_".join([name,uuid.uuid4().hex])  # 生成32位随机十六进制字符串
        folder_path = os.path.join(base_path, folder_name)
        try:
            os.makedirs(folder_path, exist_ok=False)  # exist_ok=False 可防止覆盖
            print(f"文件夹创建成功：{folder_path}")
            break
        except FileExistsError:
            # 如果小概率重名，重新生成
            continue
    return folder_path
