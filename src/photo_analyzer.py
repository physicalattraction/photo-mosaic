import os.path
from typing import Dict, Optional

from photo import Photo
from type_hinting import Color


class PhotoAnalyzer:
    """
    Class responsible for determining which photo to pick to create a mosaic, based on average color
    """

    _photos: Optional[Dict[str, Photo]]

    def __init__(self, src_dir: str):
        self.src_dir = src_dir
        self._photos = None

    @property
    def photos(self) -> Dict[str, Photo]:
        if not self._photos:
            self._photos = {
                filename: Photo(filepath=os.path.join(self.src_dir, filename))
                for filename in sorted(os.listdir(self.src_dir))
            }
        return self._photos

    def select_best_photo(self, color: Color) -> Photo:
        """
        Select the photo that most closely matches the input color
        """

        return NotImplemented()
