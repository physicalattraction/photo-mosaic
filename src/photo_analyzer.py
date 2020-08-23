import math
import os.path
from typing import Dict, List

from PIL import Image

from photo import Photo
from type_hinting import Color


class PhotoAnalyzer:
    """
    Class responsible for determining which photo to pick to create a mosaic, based on average color
    """

    _photos: Dict[str, Photo]
    _photos_to_choose_from: List[str]

    def __init__(self, src_dir: str, nr_photo_pixels: int):
        self.src_dir = src_dir
        self.nr_photo_pixels = nr_photo_pixels

        self._photos = {}
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
            print(duplicate_per_photo)
            self._photos_to_choose_from = list(self.photos.keys()) * duplicate_per_photo
        return self._photos_to_choose_from

    @property
    def photos(self) -> Dict[str, Photo]:
        if not self._photos:
            self._photos = {
                filename: Photo.open(os.path.join(self.src_dir, filename))
                for filename in sorted(os.listdir(self.src_dir))
            }
        return self._photos

    def select_best_photo(self, color: Color) -> Photo:
        """
        Select the photo that most closely matches the input color
        """

        unique_photos_to_choose_from = set(self.photos_to_choose_from)
        distances = [
            (self._distance(color, self.photos[filename].avg_color), filename)
            for filename in unique_photos_to_choose_from
        ]
        best_photo_filename = sorted(distances)[0][1]
        self._photos_to_choose_from.remove(best_photo_filename)
        return self.photos[best_photo_filename]

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
    norm = 3.25
    x = math.pow(norm * math.pow(127, 3), 1 / norm)
    print(x)
    box_1 = Image.new(mode='RGB', color=(0, 0, 0), size=(50, 50))
    box_2 = Image.new(mode='RGB', color=(127, 127, 127), size=(50, 50))
    box_3 = Image.new(mode='RGB', color=(int(x), 0, 0), size=(50, 50))
    box_4 = Image.new(mode='RGB', color=(0, int(x), 0), size=(50, 50))
    box_5 = Image.new(mode='RGB', color=(0, 0, int(x)), size=(50, 50))
    result = Image.new(mode='RGB', size=(150, 150))
    result.paste(box_1, box=(50, 50))
    result.paste(box_2, box=(100, 50))
    result.paste(box_3, box=(0, 50))
    result.paste(box_4, box=(50, 0))
    result.paste(box_5, box=(50, 100))
    result.show()
