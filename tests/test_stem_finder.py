"""测试 stem_finder 模块的关键词匹配逻辑"""
import os
import sys
import tempfile
import pytest

# 将项目根目录加入 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stem_finder import stream_build, KEYWORDS, EXCLUDE


class TestStreamBuild:
    """测试 stream_build 人声文件查找逻辑"""

    def test_find_vocals_file(self):
        """能找到包含 'vocals' 关键词的文件"""
        files = [
            "audio_(Vocals)_model.wav",
            "audio_(Instrumental)_model.wav",
        ]
        result = stream_build(files)
        assert "Vocals" in result

    def test_find_clean_file(self):
        """能找到包含 'clean' 关键词的文件"""
        files = ["output_clean.wav", "output_other.wav"]
        result = stream_build(files)
        assert "clean" in result

    def test_find_no_reverb_file(self):
        """DeEcho 模型输出: 'no reverb' 关键词"""
        files = ["audio_no reverb.wav", "audio_instrumental.wav"]
        result = stream_build(files)
        assert "no reverb" in result

    def test_find_no_crowd_file(self):
        """DeCrowd 模型输出: 'no crowd' 关键词"""
        files = ["audio_no crowd.wav", "audio_other.wav"]
        result = stream_build(files)
        assert "no crowd" in result

    def test_find_no_noise_file(self):
        """DeNoise 模型输出: 'no noise' 关键词"""
        files = ["audio_no noise.wav", "audio_other.wav"]
        result = stream_build(files)
        assert "no noise" in result

    def test_exclude_instrumental(self):
        """排除包含 'instrumental' 的文件"""
        files = [
            "audio_(Instrumental)_model.wav",
            "audio_(Vocals)_model.wav",
        ]
        result = stream_build(files)
        assert "Instrumental" not in result
        assert "Vocals" in result

    def test_exclude_no_vocals(self):
        """排除包含 'no_vocals' 的文件"""
        files = [
            "audio_no_vocals.wav",
            "audio_(Vocals)_model.wav",
        ]
        result = stream_build(files)
        assert "no_vocals" not in result

    def test_exclude_other(self):
        """排除包含 'other' 的文件（Demucs 模型）"""
        files = [
            "audio_(Other)_model.wav",
            "audio_(Vocals)_model.wav",
        ]
        result = stream_build(files)
        assert "Other" not in result

    def test_empty_list_raises(self):
        """空列表抛异常"""
        with pytest.raises(RuntimeError, match="未返回任何文件"):
            stream_build([])

    def test_no_vocals_found_raises(self):
        """找不到人声文件抛异常"""
        with pytest.raises(RuntimeError, match="未找到人声文件"):
            stream_build(["only_instrumental.wav", "some_other.wav"])

    def test_relative_path_with_output_dir(self):
        """相对路径 + output_dir → 返回拼接后的绝对路径"""
        files = ["relative_vocals.wav"]
        with tempfile.TemporaryDirectory() as tmpdir:
            result = stream_build(files, output_dir=tmpdir)
            assert result == os.path.join(tmpdir, "relative_vocals.wav")

    def test_absolute_path_ignores_output_dir(self):
        """绝对路径不受 output_dir 影响"""
        abs_path = os.path.abspath("some_vocals.wav")
        with tempfile.TemporaryDirectory() as tmpdir:
            result = stream_build([abs_path], output_dir=tmpdir)
            assert result == abs_path

    def test_case_insensitive(self):
        """关键词匹配不区分大小写"""
        files = ["Audio_(VOCALS)_Model.wav"]
        result = stream_build(files)
        assert "VOCALS" in result

    def test_first_match_wins(self):
        """多个匹配时，返回第一个匹配到的文件"""
        files = [
            "first_vocals.wav",
            "second_clean.wav",
        ]
        result = stream_build(files)
        assert "first_vocals" in result


class TestConstants:
    """关键词常量的合理性检查"""

    def test_keywords_non_empty(self):
        assert len(KEYWORDS) > 0

    def test_exclude_non_empty(self):
        assert len(EXCLUDE) > 0

    def test_no_overlap_between_keywords_and_exclude(self):
        overlap = set(KEYWORDS) & set(EXCLUDE)
        assert not overlap, f"KEYWORDS 和 EXCLUDE 不应有重叠: {overlap}"
