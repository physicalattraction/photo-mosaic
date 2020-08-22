import os.path


class Dir:
    src = os.path.dirname(__file__)
    root = os.path.dirname(src)
    photos = os.path.join(root, 'photos')
    testdata = os.path.join(root, 'testdata')
