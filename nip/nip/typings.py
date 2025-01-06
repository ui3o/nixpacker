from typing import Required, TypedDict


class Config(TypedDict, total=False):
    tags: Required[list[str]]
    """
    list of pulled docker.io tags.

    example: docker.io tag is hello--2.10

    """
    defaults: Required[dict[str, str]]
    """
    list of available packages on container path

    the **key** is the name of executable in **container**

    the **value** is the version of executable. Normally path is like this:
    hash-bash-1.1.2 **but**
    If the executable has different end in the path than possible to add regex in the
    definition. Example: "2.1.2||-lib"
    """
    osBindings: Required[dict[str, str]]
    """
    binding program to host os.

    the **key** is the name of executable file on **host**

    the **value** is the name of executable file in **container**

    this type of definition fixes the duplication

    the **key** can be a key from defaults with `@` value which means bind all
    program from  `program/bin` folder
    """
    ports: Required[[str]]
    """
    define one port(8080) or port range(8090-8095) which can be transparent on both side

    range definition can be:
    - "ports": ["8000-9000", "12345-", "-2000", "10234"] which means ["8000-9000", "12345-65535", "0-2000", "10234"]
    """
