import json
import os.path
from pprint import pprint
from typing import Dict, List, Tuple

import math

from photo import Photo
from utils.path import Path
from utils.type_hinting import Color, Size, size_as_string


class PhotoAnalyzer:
    """
    Class responsible for determining which photo to pick to create a mosaic, based on average color
    """

    _photos: Dict[str, Photo]
    _resized_photos: Dict[Tuple[str, Size], Photo]  # Resized image, where key is (filename, (width, height))
    _photos_to_choose_from: List[str]

    def __init__(self, src_dir: str, nr_photo_pixels: int, tile_size: Size):
        self.src_dir = src_dir
        self.nr_photo_pixels = nr_photo_pixels
        self.tile_size = tile_size

        self.originals_dir = os.path.join(self.src_dir, 'original_input_photos')
        self.resizeds_dir = os.path.join(self.src_dir, 'resized_input_photos', size_as_string(self.tile_size))
        os.makedirs(self.resizeds_dir, exist_ok=True)
        self.originals = {filename for filename in sorted(os.listdir(self.originals_dir)) if self._is_image(filename)}

        self._resized_photos: Dict[str, Photo] = {}
        self._photos_to_choose_from: List[str] = []

        self._resize_images()
        self._photo_analysis = self._analyze_photos()

    @property
    def photos_to_choose_from(self) -> List[str]:
        """
        Return a list of photo filenames that are not used yet in the photo mosaic

        Note: this must be a list, since there can be duplicates in it that need to be popped one by one
        """

        if not self._photos_to_choose_from:
            nr_photos = len(self.originals)
            nr_required_photos = self.nr_photo_pixels
            duplicate_per_photo = int(math.ceil(nr_required_photos / nr_photos))
            self._photos_to_choose_from = list(self.originals) * duplicate_per_photo
        return self._photos_to_choose_from

    def select_best_photo(self, color: Color) -> Photo:
        """
        Select the photo that most closely matches the input color
        """

        unique_photos_to_choose_from = set(self.photos_to_choose_from)
        distances = [
            (self._distance(color, self._photo_analysis[filename]), filename)
            for filename in unique_photos_to_choose_from
        ]
        best_photo_filename = min(distances)[1]
        self._photos_to_choose_from.remove(best_photo_filename)
        return self._get_resized_photo(best_photo_filename)

    def _resize_images(self):
        """
        Ensure that all tile images are resized before using them
        """

        resizeds = {filename for filename in sorted(os.listdir(self.resizeds_dir))}

        # Resize images that have not been resized yet
        nr_photos_resized = 0
        for filename in self.originals:
            if filename not in resizeds:
                original_fp = os.path.join(self.originals_dir, filename)
                resized_fp = os.path.join(self.resizeds_dir, filename)
                original_photo = Photo.open(original_fp)
                resized_photo = Photo(img=original_photo.resize(self.tile_size))
                resized_photo.save(resized_fp)
                nr_photos_resized += 1
        if nr_photos_resized > 0:
            print(f'Resized {nr_photos_resized} photos to {size_as_string(self.tile_size)}')

        # Remove resized images that are not in the original
        nr_resized_photos_deleted = 0
        for filename in resizeds:
            if filename not in self.originals:
                resized_fp = os.path.join(self.resizeds_dir, filename)
                os.remove(resized_fp)
                nr_resized_photos_deleted += 1
        if nr_resized_photos_deleted > 0:
            print(f'Deleted {nr_resized_photos_deleted} unused resized photos from {self.resizeds_dir}')

    def _analyze_photos(self) -> Dict[str, Color]:
        """
        Determine the average color of each input photo, and store it on disk for faster reruns
        """

        # Read the existing photo analysis file
        photo_analysis_file = os.path.join(self.src_dir, 'photo_analysis.json')
        if os.path.exists(photo_analysis_file):
            with open(photo_analysis_file) as f:
                photo_analysis = json.load(f)
        else:
            photo_analysis = {}

        if not self.originals.difference(photo_analysis.keys()):
            print(f'Photo analysis of {len(photo_analysis)} photos is up-to-date')
            return photo_analysis

        # Delete analysis of photos that do no longer exist
        keys_to_delete = set()
        for filename in photo_analysis.keys():
            if filename not in self.originals:
                keys_to_delete.add(filename)
        if keys_to_delete:
            for key in keys_to_delete:
                del photo_analysis[key]
            print(f'Deleted analysis of {len(keys_to_delete)} photos that do no longer exist')

        # Add analysis of photos that are not present yet
        nr_photos_analyzed = 0
        for filename in self.originals:
            if filename not in photo_analysis:
                original_fp = os.path.join(self.originals_dir, filename)
                original_photo = Photo.open(original_fp)
                photo_analysis[filename] = original_photo.avg_color
                nr_photos_analyzed += 1
                if nr_photos_analyzed % 100 == 0:
                    # Analyzing thousands of photos can be slow. We therefore want to save the progress after
                    # every 100 photos analyzed, and inform the user of the progress.
                    print(f'Analyzed average color of {nr_photos_analyzed} photos...')
                    with open(photo_analysis_file, 'w') as f:
                        json.dump(photo_analysis, f, indent=2)
        if nr_photos_analyzed > 0:
            print(f'Analyzed average color of {nr_photos_analyzed} photos')

        # Write the photo analysis to disk
        with open(photo_analysis_file, 'w') as f:
            # Sort the result before writing
            result = {
                key: photo_analysis[key]
                for key in sorted(photo_analysis.keys())
            }
            json.dump(result, f, indent=2)

        return photo_analysis

    def _get_resized_photo(self, filename: str) -> Photo:
        """
        Look up the resized photo with the given filename

        Since it could be reused when photos are duplicated, we only want to open the image once.
        We therefore store the opened images in the object variable _resized_photos
        """

        if filename not in self._resized_photos:
            photo_fp = os.path.join(self.resizeds_dir, filename)
            self._resized_photos[filename] = Photo.open(photo_fp)
        return self._resized_photos[filename]

    @staticmethod
    def _is_image(filename: str) -> bool:
        """
        Return whether the given file is an image or not, based on the extension
        """

        _, ext = os.path.splitext(filename)
        image_extensions = {'.jpg', '.jpeg', '.bmp', '.png'}
        return ext.lower() in image_extensions

    @staticmethod
    def _distance(color_1: Color, color_2: Color) -> float:
        """
        Return the distance between two colors

        The distance is defined as the square of the 2-norm. Rationale: the 2-norm penalizes
        large differences in a single channel, which for human eyes are less alike.
        Example: (128, 128, 128) looks more like (127, 127, 127) than (130, 127, 127) does.
        """

        quadratic_errors = (math.pow((color_1[index] - color_2[index]), 2) for index in range(3))
        return math.sqrt(sum(quadratic_errors))


if __name__ == '__main__':
    pa = PhotoAnalyzer(Path.to_src_photos_dir('cats_small'), 16, (100, 100))
    best_photo = pa.select_best_photo((121, 120, 114))
    print(best_photo)
    best_photo.show()
