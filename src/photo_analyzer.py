import os.path
from typing import Dict, List, Tuple

import math

from photo import Photo
from type_hinting import Color, Size


class PhotoAnalyzer:
    """
    Class responsible for determining which photo to pick to create a mosaic, based on average color
    """

    _photos: Dict[str, Photo]
    _resized_photos: Dict[Tuple[str, int, int], Photo]  # Resized image, where key is (filename, width, height)
    _photos_to_choose_from: List[str]

    def __init__(self, src_dir: str, nr_photo_pixels: int):
        self.src_dir = src_dir
        self.nr_photo_pixels = nr_photo_pixels

        self._photos = {}
        self._resized_photos = {}
        self._photos_to_choose_from = []

    @property
    def photos_to_choose_from(self) -> List[str]:
        """
        Return a list of photo filenames that are not used yet in the photo mosaic
        """

        if not self._photos_to_choose_from:
            nr_photos = len(self.photos.keys())
            nr_required_photos = self.nr_photo_pixels
            duplicate_per_photo = int(math.ceil(nr_required_photos / nr_photos))
            self._photos_to_choose_from = list(self.photos.keys()) * duplicate_per_photo
        return self._photos_to_choose_from

    @property
    def photos(self) -> Dict[str, Photo]:
        if not self._photos:
            self._photos = {
                filename: Photo.open(os.path.join(self.src_dir, filename))
                for filename in sorted(os.listdir(self.src_dir))
                if self._is_image(filename)
            }
            if not self._photos:
                msg = f'No photos found in directory {self.src_dir}'
                raise FileNotFoundError(msg)
        return self._photos

    def select_best_photo(self, color: Color, desired_size: Size = None) -> Photo:
        """
        Select the photo that most closely matches the input color
        """

        # TODO: I hacked in to determine the average co

        unique_photos_to_choose_from = set(self.photos_to_choose_from)
        distances = [
            (self._distance(color, self._get_resized_photo(filename, desired_size).avg_color), filename)
            for filename in unique_photos_to_choose_from
        ]
        best_photo_filename = min(distances)[1]
        self._photos_to_choose_from.remove(best_photo_filename)
        if desired_size:
            return self._get_resized_photo(best_photo_filename, desired_size)
        else:
            return self.photos[best_photo_filename]

    def _is_image(self, filename: str) -> bool:
        """
        Return whether the given file is an image or not, based on the extension
        """

        _, ext = os.path.splitext(filename)
        image_extensions = {'.jpg', '.jpeg', '.bmp', '.png'}
        return ext.lower() in image_extensions

    def _get_resized_photo(self, filename: str, size: Size) -> Photo:
        """
        Look up the resized photo with the given filename and size

        If it has not been resized yet, resize it on the spot and cache it in the dictionary _resized_photos
        """

        key = (filename, *size)
        if key not in self._resized_photos:
            photo = self.photos[filename]
            self._resized_photos[key] = Photo(img=photo.resize(size))
        return self._resized_photos[key]

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
