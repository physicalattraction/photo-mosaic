import json
import os
import shutil
from collections import Counter, defaultdict

import math

from photo import Photo
from utils.image_utils import is_image
from utils.os_utils import ensure_empty_dir
from utils.path import Path
from utils.type_hinting import Size


class PhotoCollector:
    """
    Class responsible for collecting the right photos from an unorganized directory

    When used properly, an unorganized directory `raw/<dirname>` will result in an organized
    directory `photos/<dirname>/mosaic` with all photos ready to be used in mosaic maker.
    """

    # Resize images, even if the aspect ratio distorts by this amount (factor between 0 and 1, i.e. 0.05 means 5%)
    ALLOWED_DISTORTION_RATE = 0.05

    def __init__(self, dirname: str) -> None:
        """
        :param dirname: Directory within the `raw` directory to collect photos from
                        Photos will be collected in this dirname in the `photos` directory
        """

        self.raw_dir = Path.to_raw_photos_dir(dirname)
        self.photos_dir = Path.to_src_photos_dir(dirname)

    def collect(self, desired_width: int = 250) -> None:
        ensure_empty_dir(self.photos_dir)
        self._collect_files()
        most_common_size_ratio = self._split_by_size_ratio()
        self._select_images(most_common_size_ratio)
        self._resize_images(most_common_size_ratio, desired_width)

    def _clean_photos_dir(self) -> None:
        """
        Ensure that photos/<dirname> exists, and is empty
        """

        if os.path.exists(self.photos_dir):
            shutil.rmtree(self.photos_dir)
        os.mkdir(self.photos_dir)

    def _collect_files(self) -> None:
        """
        Store all files in the given directory inside `raw` (and subdirectories) in a single directory inside `photos`

        The filenames in the single directory are normalized: <zero_padded_index>.<extension>

        Before:

        raw/
            cats/
                cat_even/
                    cat002.JPG
                    cat004.JPG
                cat_odd/
                    first_cat/
                        cat001.JPG
                    cat003.JPG
                    cat005.JPG

        After:

        photos/
            cats/
                00000001.jpg
                00000002.jpg
                00000003.jpg
                00000004.jpg
                00000005.jpg
        """

        nr_files = 0
        for dirpath, _, filenames in os.walk(self.raw_dir):
            for filename in filenames:
                if not is_image(filename):
                    continue

                _, ext = os.path.splitext(filename)
                nr_files += 1
                src_full_path = os.path.join(dirpath, filename)
                new_filename = str(nr_files).zfill(8) + ext.lower()
                dst_full_path = os.path.join(self.photos_dir, new_filename)
                shutil.copyfile(src_full_path, dst_full_path)

    def _split_by_size_ratio(self) -> int:
        """
        Split the flat directory structure of images in `photos/<dirname>` into a directory per size ratio

        Size ratio is defined as width/height, multiplied by 100 and rounded to an integer
        In other words: 100 means 1:1, 160 means 8:5, etc.

        As a side effect, we write a file called `size_ratio.json` with per size ratio the
        amount of images with that size ratio. This can be used to manually inspect the
        various size ratios incase you receive surprising results.

        :return: The most common size ratio
        """

        # Exhaust the iterator in order to not iterate over directories created in the for-loop
        files = list(os.scandir(self.photos_dir))
        size_ratio_counter = defaultdict(int)
        for file in files:
            img = Photo.open(file.path)
            w, h = img.size
            resolution = int(round(w / h * 100))
            dst_dirname = str(resolution)
            dst_dir = os.path.join(self.photos_dir, dst_dirname)
            if not os.path.isdir(dst_dir):
                os.mkdir(dst_dir)
            dst_full_path = os.path.join(dst_dir, file.name)
            size_ratio_counter[resolution] += 1
            shutil.move(file.path, dst_full_path)

        # Sort by number of occurrences
        size_ratio_counter = Counter(size_ratio_counter).most_common()
        most_common = size_ratio_counter[0][0]
        size_ratio_counter = dict(size_ratio_counter)

        resolution_file = os.path.join(self.photos_dir, 'size_ratio.json')
        with open(resolution_file, 'w') as f:
            f.write(json.dumps(size_ratio_counter, indent=4))

        return most_common

    def _select_images(self, desired_size_ratio: int) -> None:
        """
        Copy all images with the given desired size ratio to photos/<dirname>/mosaic

        Note that all images with approximately the same size ratio are also selected. What qualifies
        as approximately is defined by the constant self.ALLOWED_DISTORTION_RATE

        :param desired_size_ratio: The desired size ratio for the final images (as defined in split_by_size_ratio)
        """

        mosaic_dir = os.path.join(self.photos_dir, 'mosaic')
        ensure_empty_dir(mosaic_dir)

        min_resolution = int(math.ceil(desired_size_ratio * (1 - self.ALLOWED_DISTORTION_RATE)))
        max_resolution = int(math.floor(desired_size_ratio * (1 + self.ALLOWED_DISTORTION_RATE)))
        for resolution in range(min_resolution, max_resolution + 1):
            img_dir = os.path.join(self.photos_dir, str(resolution))
            if not os.path.isdir(img_dir):
                continue
            files = list(os.scandir(img_dir))
            for file in files:
                dst_file = os.path.join(mosaic_dir, file.name)
                shutil.copy(file, dst_file)

    def _resize_images(self, desired_size_ratio: int, desired_width: int) -> None:
        """
        Resize all images from photos/<dirname>/mosaic to the desired width

        :param desired_size_ratio: The desired size ratio for the final images (as defined in split_by_size_ratio)
        :param desired_width: The width of the final images to use in the MosaicCreator

        Rationale why we do not have desired_height as input: it needs to be calculated in a rather
        tedious way, and we don't want the client to take care of that. The desired_
        """

        # TODO: I have the feeling that this should not be done here.

        desired_height = int(round(desired_width / desired_size_ratio * 100))
        desired_size: Size = (desired_width, desired_height)

        mosaic_dir = os.path.join(self.photos_dir, 'mosaic')

        files = list(os.scandir(mosaic_dir))
        for file in files:
            img = Photo.open(file.path)
            img = img.resize(desired_size)
            img.save(file.path)


if __name__ == '__main__':
    pc = PhotoCollector('test')
    pc.collect()
