from statistics import mean
from typing import Optional

from PIL import Image

from type_hinting import Color


class Photo:
    """
    Wrapper around Pillow's Image to add functionality
    """

    _avg_color: Optional[Color] = None

    def __init__(self, *, filepath: str = None, img: Image.Image = None):
        """
        Initialize with either a path to a file, or an Image in memory

        :param filepath: Full path to the photo file
        :param img: Image of the photo
        """

        assert filepath and not img or img and not filepath
        if filepath:
            self.img = Image.open(filepath)
        else:
            self.img = img

        self._avg_color = None

    @property
    def avg_color(self) -> Color:
        """
        Return the average color of the Photo
        """

        if not self._avg_color:
            pixels = list(self.getdata())
            self._avg_color = tuple(int(round(mean([pixel[channel] for pixel in pixels])))
                                    for channel in (0, 1, 2))
        return self._avg_color

    def __getattr__(self, item):
        """
        To mimic inheritance, any attribute on Photo that cannot be found in this class is redirected to the Image
        associated with this Photo object. Magic methods are not propagated to self.img using __getattr__,
        and hence we have to manually propagate them
        """

        return getattr(self.img, item)

    def __eq__(self, other: 'Photo'):
        """
        A less strict comparison than in Image to see if two photos are equal, to avoid checking metadata
        """

        return (
                self.__class__ is other.__class__
                and self.mode == other.mode
                and self.size == other.size
                and self.tobytes() == other.tobytes()
        )

    def __enter__(self):
        return self.img.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.img.__exit__(exc_type, exc_val, exc_tb)

    def __del__(self):
        """
        When a Photo goes out of memory, we need to close the image,
        and with it the associated file if it was created from a file
        """

        return self.img.close()

    def __repr__(self):
        """
        A less comprehensive, more readable representation than in Image of the Photo
        """

        return f'<{self.__class__.__name__} mode={self.mode} size={self.size[0]}x{self.size[1]}>'
