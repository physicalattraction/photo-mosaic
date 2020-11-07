import os.path
import shutil
from unittest import TestCase

from collector.photo_collector import PhotoCollector
from photo import Photo
from utils.path import Path


class PhotoCollectorTestCase(TestCase):
    dirname = 'PhotoCollectorTestCase'
    photos_dir = Path.to_src_photos_dir(dirname)
    raw_dir = Path.to_raw_photos_dir(dirname)

    def setUp(self) -> None:
        """
        Ensure that dirs photos/PhotoCollectorTestCase and raw/PhotoCollectorTestCase do not exist before tests start
        """

        for test_dir in (self.photos_dir, self.raw_dir):
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def tearDown(self) -> None:
        """
        Ensure that dirs photos/PhotoCollectorTestCase and raw/PhotoCollectorTestCase do not exist after tests are done
        """

        for test_dir in (self.photos_dir, self.raw_dir):
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_that_collect_files_gathers_files_from_single_directory(self):
        self.setup_raw_dir_structure()
        collector = PhotoCollector(self.dirname)
        collector._clean_photos_dir()
        collector._collect_files()
        present_files = sorted(entry.name for entry in os.scandir(self.photos_dir))
        self.assertListEqual(['00000001.jpg', '00000002.jpg', '00000003.jpg',
                              '00000004.jpg', '00000005.jpg', '00000006.jpg'], present_files)

    def test_that_split_by_size_ratio_results_in_correct_folder_structure(self):
        self.setup_photo_dir_structure()
        collector = PhotoCollector(self.dirname)
        most_common_resolution = collector._split_by_size_ratio()

        # Five photos are 455x455 (1:1), one photo is 474x296 (1:1.601)
        self.assertEqual(100, most_common_resolution)
        dirname = os.path.join(self.photos_dir, '100')
        nr_files_in_dir = sum(1 for _ in os.scandir(dirname))
        self.assertEqual(5, nr_files_in_dir)
        dirname = os.path.join(self.photos_dir, '160')
        nr_files_in_dir = sum(1 for _ in os.scandir(dirname))
        self.assertEqual(1, nr_files_in_dir)

    def test_that_select_images_selects_all_correct_images(self):
        self.setup_photo_dir_structure()
        collector = PhotoCollector(self.dirname)
        collector._split_by_size_ratio()

        mosaic_dir = os.path.join(self.photos_dir, 'mosaic')
        self.assertFalse(os.path.exists(mosaic_dir))
        collector._select_images(desired_size_ratio=100)

        self.assertTrue(os.path.exists(mosaic_dir))
        nr_files_in_dir = sum(1 for _ in os.scandir(mosaic_dir))
        self.assertEqual(5, nr_files_in_dir)

    def test_that_resize_images_resizes_all_images(self):
        self.setup_photo_dir_structure()
        collector = PhotoCollector(self.dirname)
        collector._split_by_size_ratio()
        collector._select_images(desired_size_ratio=100)

        # Crop the first image, such that the original is not square anymore
        mosaic_dir = os.path.join(self.photos_dir, 'mosaic')
        first_cat = os.path.join(mosaic_dir, '00000001.jpg')
        img = Photo.open(first_cat)
        img = img.crop((0, 0, 400, 200))
        img.save(first_cat)

        collector._resize_images(desired_size_ratio=100, desired_width=100)

        for file in os.scandir(mosaic_dir):
            img = Photo.open(file.path)
            desired_size = (100, 100)
            self.assertTupleEqual(desired_size, img.size)

    def setup_raw_dir_structure(self):
        """
        Create the following directory structure and files inside `raw/PhotoCollectorTestCase`:

          cat_even/
            cat002.JPG
            cat004.JPG
          cat_odd/
            first_cat/
              cat001.JPG
            cat003.JPG
            cat005.JPG
        """

        cat_even = os.path.join(self.raw_dir, 'cat_even')
        cat_odd = os.path.join(self.raw_dir, 'cat_odd')
        first_cat = os.path.join(cat_odd, 'first_cat')
        for raw_dir in (self.raw_dir, cat_even, cat_odd, first_cat):
            os.mkdir(raw_dir)

        cat002 = os.path.join(cat_even, 'cat002.JPG')
        cat004 = os.path.join(cat_even, 'cat004.JPG')
        cat006 = os.path.join(cat_even, 'cat006.JPG')
        cat001 = os.path.join(first_cat, 'cat001.JPG')
        cat003 = os.path.join(cat_odd, 'cat003.JPG')
        cat005 = os.path.join(cat_odd, 'cat005.JPG')
        src_dir = os.path.join(Path.testdata, 'cats')
        shutil.copyfile(os.path.join(src_dir, 'cat001.jpg'), cat001)
        shutil.copyfile(os.path.join(src_dir, 'cat002.jpg'), cat002)
        shutil.copyfile(os.path.join(src_dir, 'cat003.jpg'), cat003)
        shutil.copyfile(os.path.join(src_dir, 'cat004.jpg'), cat004)
        shutil.copyfile(os.path.join(src_dir, 'cat005.jpg'), cat005)
        shutil.copyfile(os.path.join(src_dir, 'cat006.jpg'), cat006)

        with open(os.path.join(self.raw_dir, 'info.txt'), 'w') as f:
            f.write('We now have 5 cat pictures in this directory')

    def setup_photo_dir_structure(self):
        self.setup_raw_dir_structure()
        collector = PhotoCollector(self.dirname)
        collector._clean_photos_dir()
        collector._collect_files()
