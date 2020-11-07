import os.path
import shutil
from unittest import TestCase

from utils.os_utils import ensure_empty_dir
from utils.path import Path


class OsUtilsTestCase(TestCase):
    dirname = 'OsUtilsTestCase'
    photos_dir = Path.to_src_photos_dir(dirname)

    def setUp(self) -> None:
        if os.path.exists(self.photos_dir):
            shutil.rmtree(self.photos_dir)

    def test_that_ensure_empty_dir_creates_dir(self):
        self.assertFalse(os.path.exists(self.photos_dir))
        ensure_empty_dir(self.photos_dir)
        self.assertTrue(os.path.exists(self.photos_dir))

    def test_that_ensure_empty_dir_empties_dir(self):
        # Place a file in the directory to be emptied
        os.mkdir(self.photos_dir)
        src_full_path = Path.to_testphoto('wolf_low_res.jpg')
        dst_full_path = os.path.join(self.photos_dir, 'wolf.jpg')
        shutil.copyfile(src_full_path, dst_full_path)
        present_files = [entry.name for entry in os.scandir(self.photos_dir)]
        self.assertListEqual(['wolf.jpg'], present_files)

        ensure_empty_dir(self.photos_dir)
        present_files = [entry.name for entry in os.scandir(self.photos_dir)]
        self.assertListEqual([], present_files)
