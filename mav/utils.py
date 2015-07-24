from django.utils.text import slugify


def slugify_with_underscores(text):
    """
    A slugify that does not tolerate dashes (replaced with underscores)
    :param text: The text to slugify
    :return: The slugified text
    """
    return slugify(text).replace('-', '_')
