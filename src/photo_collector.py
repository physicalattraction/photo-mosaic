import json
import os
import shutil
from collections import Counter, defaultdict

import math

from photo import Photo
from type_hinting import Size
from utils import Path


class PhotoCollector:
    """
    Class responsible for collecting the right photos from an unorganized directory
    """

    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
    # Resize images, even if the aspect ratio distorts by this amount
    ALLOWED_DISTORTION_RATE = 0.05

    def __init__(self, dirname: str):
        """
        :param dirname: Directory within the raw directory to collect photos from
        """

        self.raw_dir = Path.to_raw_photos_dir(dirname)
        self.photos_dir = Path.to_src_photos_dir(dirname)

    def collect(self):
        # self._clean_photos_dir()
        # self._collect_files()
        # self._filter_image_files()
        # most_common_resolution = self._split_by_resolution()
        most_common_resolution = 1779
        self._resize_images(most_common_resolution, desired_width=250)

    def _clean_photos_dir(self):
        if os.path.exists(self.photos_dir):
            shutil.rmtree(self.photos_dir)
        os.mkdir(self.photos_dir)

    def _collect_files(self):
        """
        Store all files in the given directory and subdirectories in a single directory
        """

        nr_files = 0
        for x, y, z in os.walk(self.raw_dir):
            for file in z:
                _, ext = os.path.splitext(file)
                nr_files += 1
                src_full_path = os.path.join(x, file)
                new_filename = str(nr_files).zfill(8) + ext.lower()
                dst_full_path = os.path.join(self.photos_dir, new_filename)
                shutil.copyfile(src_full_path, dst_full_path)

    def _filter_image_files(self):
        for filename in os.scandir(self.photos_dir):
            _, ext = os.path.splitext(filename)
            if ext not in self.IMAGE_EXTENSIONS:
                os.unlink(filename)

    def _split_by_resolution(self) -> int:
        """

        :return: The most common resolution
        """

        # Exhaust the iterator in order to not iterate over directories created in the for-loop
        files = list(os.scandir(self.photos_dir))
        resolution_counter = defaultdict(int)
        for file in files:
            img = Photo.open(file.path)
            w, h = img.size
            resolution = int(round(w / h * 1000))
            dst_dirname = str(resolution)
            dst_dir = os.path.join(self.photos_dir, dst_dirname)
            if not os.path.isdir(dst_dir):
                os.mkdir(dst_dir)
            dst_full_path = os.path.join(dst_dir, file.name)
            resolution_counter[resolution] += 1
            shutil.move(file.path, dst_full_path)
        resolution_counter = Counter(resolution_counter).most_common()
        most_common = resolution_counter[0][0]
        resolution_counter = dict(resolution_counter)

        resolution_file = os.path.join(self.photos_dir, 'resolution.json')
        with open(resolution_file, 'w') as f:
            f.write(json.dumps(resolution_counter, indent=4))

        return most_common

    def _resize_images(self, desired_resolution: int, desired_width: int):
        """
        Resize the selected images

        :param desired_resolution: The directory created by _split_by_resolution to resize
        :param desired_width: The width of the final images to use in the MosaicCreator
        """

        desired_height = int(round(desired_width / desired_resolution * 1000))
        desired_size: Size = (desired_width, desired_height)

        dst_dir = os.path.join(self.photos_dir, 'mosaic')
        if not os.path.isdir(dst_dir):
            os.mkdir(dst_dir)

        min_resolution = int(math.ceil(desired_resolution * (1 - self.ALLOWED_DISTORTION_RATE)))
        max_resolution = int(math.floor(desired_resolution * (1 + self.ALLOWED_DISTORTION_RATE)))
        for resolution in range(min_resolution, max_resolution + 1):
            img_dir = os.path.join(self.photos_dir, str(resolution))
            if not os.path.isdir(img_dir):
                continue
            files = list(os.scandir(img_dir))
            for file in files:
                img = Photo.open(file.path)
                img = img.resize(desired_size)
                dst_full_path = os.path.join(dst_dir, file.name)
                img.save(dst_full_path)

    def _get_files_from_resolution(self, desired_resolution):
        min_resolution = int(math.ceil(desired_resolution * (1 - self.ALLOWED_DISTORTION_RATE)))
        max_resolution = int(math.floor(desired_resolution * (1 + self.ALLOWED_DISTORTION_RATE)))
        for resolution in range(min_resolution, max_resolution + 1):
            img_dir = os.path.join(self.photos_dir, str(resolution))
            if not os.path.isdir(img_dir):
                continue
            yield from os.scandir(img_dir)


if __name__ == '__main__':
    pc = PhotoCollector('test')
    pc.collect()
