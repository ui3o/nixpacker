from typing import Required, TypedDict


class Config(TypedDict, total=False):
    tags: Required[list[str]]
    """
    list of pulled docker.io tags.

    example: docker.io tag is hello--2.10

    """
    defaults: Required[dict[str, list[str]]]
    """
    list of available packages on container path

    the **key** is the name of executable in **container**

    the **value** is the version of executable. Normally path is like this:
    hash-bash-1.1.2 **but**
    If the executable has different end in the path than possible to add regex in the
    definition. Example: "2.1.2||-lib"
    """
