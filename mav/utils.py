from django.utils.text import slugify


def slugify_with_underscores(text):
    return slugify(text).replace('-', '_')
