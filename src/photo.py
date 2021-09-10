from typing import Any, Optional

from PIL import Image

from utils.type_hinting import Color, Size

count = 0


class Photo:
    """
    Wrapper around Pillow's Image class to overwrite and add functionality
    """

    _avg_color: Optional[Color] = None

    @staticmethod
    def new(mode: str, size: Size, color: Color = 0) -> 'Photo':
        """
        Create a new photo with the given mode and size
        """

        img = Image.new(mode, size, color)
        return Photo(img)

    @staticmethod
    def open(fp: str) -> 'Photo':
        """
        Open and identify the given image file as Photo
        """

        img = Image.open(fp)
        return Photo(img)

    def __init__(self, img: Image.Image = None):
        """
        Initialize with an Image in memory

        :param img: Image of the photo
        """

        self.img = img
        self._avg_color = None

    @property
    def avg_color(self) -> Color:
        """
        Return the average color of the Photo
        """

        if not self._avg_color:
            self._avg_color = self._determine_avg_color()
        return self._avg_color

    def _determine_avg_color(self) -> Color:
        """
        Determine the average color of the Photo
        """

        global count
        count += 1
        print(f'Calculating avg color {count}')
        pixels = list(self.getdata())
        nr_pixels = len(pixels)
        channels = list(zip(*pixels))  # [(R values), (G values), (B values)]
        return (
            round(sum(channels[0]) / nr_pixels),  # R mean
            round(sum(channels[1]) / nr_pixels),  # G mean
            round(sum(channels[2]) / nr_pixels),  # B mean
        )

    def __getattr__(self, item: Any) -> Any:
        """
        To mimic inheritance, any attribute on Photo that cannot be found in this class is redirected to the Image
        associated with this Photo object. Magic methods are not propagated to self.img using __getattr__,
        and hence we have to manually propagate them
        """

        return getattr(self.img, item)

    def __eq__(self, other: 'Photo') -> bool:
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

    def __repr__(self) -> str:
        """
        A less comprehensive, more readable representation than in Image of the Photo
        """

        return f'<{self.__class__.__name__} mode={self.mode} size={self.size[0]}x{self.size[1]}>'
