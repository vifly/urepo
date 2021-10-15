from typing import Union


def pretty_size(
    file_size: Union[str, int, float],
    units: list = [" bytes", " KB", " MB", " GB", " TB", " PB", " EB"],
) -> str:
    """Get human readable size, it keep two decimal places.
       For example, 12345 -> 12.06 KB.
       Ref: https://stackoverflow.com/a/43750422

    Args:
        file_size (float): File size.
        units (list, optional): List of size units. Defaults to
         [" bytes", " KB", " MB", " GB", " TB", " PB", " EB"].

    Returns:
        str: Human readable size.
    """
    return (
        "{:.2f}{}".format(float(file_size), units[0])
        if file_size < 1024
        else pretty_size(file_size / 1024, units[1:])
    )
