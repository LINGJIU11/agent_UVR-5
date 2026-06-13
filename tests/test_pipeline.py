"""测试 pipeline 模块"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import create_task_folder


class TestCreateTaskFolder:
    """测试 create_task_folder 辅助函数"""

    def test_creates_folder(self):
        """在指定目录下创建随机文件夹"""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = create_task_folder(tmpdir, name="test")
            assert os.path.isdir(folder)
            assert folder.startswith(tmpdir)
            assert "test_" in folder

    def test_unique_folders(self):
        """连续创建得到不同的文件夹"""
        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = create_task_folder(tmpdir)
            f2 = create_task_folder(tmpdir)
            assert f1 != f2

    def test_creates_parent_if_missing(self):
        """父目录不存在时自动创建"""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_base = os.path.join(tmpdir, "sub", "deep")
            folder = create_task_folder(new_base, name="task")
            assert os.path.isdir(folder)

    def test_default_name(self):
        """默认 name=task"""
        with tempfile.TemporaryDirectory() as tmpdir:
            folder = create_task_folder(tmpdir)
            assert "task_" in os.path.basename(folder)
