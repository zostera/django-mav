from mav.models import add_mav_to


def mav(cls):
    add_mav_to(cls)
    return cls