"""测试 model_scanner 模块"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.model_scanner import file_check


class TestFileCheck:
    """测试模型文件扫描"""

    SUFFIXES = ['.pth', '.onnx', '.pt', '.ckpt', '.model', '.pb']

    def test_empty_directory(self):
        """空目录返回空结果"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = file_check(tmpdir, self.SUFFIXES)
            assert result == {}

    def test_no_matching_files(self):
        """没有匹配的模型文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "readme.txt"), "w").close()
            open(os.path.join(tmpdir, "notes.md"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert result == {}

    def test_finds_pth_files(self):
        """能找到 .pth 文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "model_v1.pth"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert len(result) == 1

    def test_finds_onnx_files(self):
        """能找到 .onnx 文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "model.onnx"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert len(result) == 1

    def test_finds_multiple_types(self):
        """能找到多种类型文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "a.pth"), "w").close()
            open(os.path.join(tmpdir, "b.onnx"), "w").close()
            open(os.path.join(tmpdir, "c.ckpt"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert len(result) == 3

    def test_ignores_wrong_suffix(self):
        """忽略非模型文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "model.yaml"), "w").close()
            open(os.path.join(tmpdir, "config.json"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert result == {}

    def test_nonexistent_path(self):
        """不存在的路径返回空结果"""
        result = file_check(r"Z:\definitely\not\exist\path", self.SUFFIXES)
        assert result == {}

    def test_result_is_indexed_dict(self):
        """返回的是以数字索引的字典"""
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "m1.pth"), "w").close()
            open(os.path.join(tmpdir, "m2.onnx"), "w").close()
            result = file_check(tmpdir, self.SUFFIXES)
            assert 0 in result
            assert 1 in result
            assert isinstance(result[0], str)
