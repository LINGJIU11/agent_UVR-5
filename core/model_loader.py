import gc
import logging
import os

import torch
from audio_separator.separator import Separator

logger = logging.getLogger("uvr5.model")

class MODEL_LOAD():   #用于加载模型并执行分离的类，初始化时需要提供模型文件路径、输出目录路径和模型名称列表。提供一个start方法来执行分离，输入原始音频路径，返回分离后的人声文件路径。
    def __init__(self,model_load_path,result_output,model_name:list):
        self.model_load_path = model_load_path
        self.result_output = result_output
        self.model_name = model_name

        self.model_load_()

    def model_load_(self):  #用于加载模型，输入模型文件路径和输出目录路径，返回加载好的Separator对象
        logger.info(f"加载模型: {self.model_name}")
        self.separator = Separator(
            model_file_dir=self.model_load_path,
            output_dir=self.result_output,
            ensemble_algorithm="avg_wave"
        )
        return self.separator.load_model(*self.model_name)

    def start(self,music_path):  #用于执行分离，输入原始音频路径，返回分离后的人声文件路径
        logger.info(f"开始分离: {os.path.basename(str(music_path))}")
        self.output_files = self.separator.separate(str(music_path))
        logger.debug(f"分离输出: {self.output_files}")
        return self.output_files
    
    def exit(self):
        try:
        # 主动清理 separator 内部资源
            if hasattr(self, 'separator') and self.separator is not None:
            # 清理可能的 ONNX session
                if hasattr(self.separator, 'model_instance'):
                    inst = self.separator.model_instance
                    if hasattr(inst, 'model_run'):
                        del inst.model_run
                    if hasattr(inst, 'model'):
                        del inst.model
                    del inst
                del self.separator
                self.separator = None
        except Exception as e:
            print(f"⚠️ exit 清理时警告: {e}")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()    # 进一步释放
            torch.cuda.synchronize() 