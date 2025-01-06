from nip.typings import Config

config: Config = {
    "tags": [
        "hello--2.10",
    ],
    "defaults": {
        "hello": "2.10",
        "openjdk": "21.0.3+9",
    },
    "osBindings": {
        "hello": "hello",
        "openjdk": "@",
    },
    "ports": [""]
}
