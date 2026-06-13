from audio_separator.separator import Separator

music_dir = r"E:\剪辑专用\小组作业\新建文件夹\苏星婕 - 把回忆拼好给你.flac"
OUTPUT_dir = r"E:\剪辑专用\rvc训练集\程序处理文件夹"
model_load_file = r"E:\UVR5-UI\models"

separator = Separator(
    model_file_dir=model_load_file,
    output_dir=OUTPUT_dir,
    ensemble_algorithm="avg_wave"
)

models = "UVR-DeEcho-DeReverb.pth"

separator.load_model(models)

music = separator.separate(music_dir)
