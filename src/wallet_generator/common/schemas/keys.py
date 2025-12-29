from dataclasses import dataclass, field


@dataclass
class UID:
    validity: str
    name: str
    email: str


@dataclass
class SubKey:
    algo: str
    keyid: str
    created: str
    caps: list[str]


@dataclass
class BaseKey:
    algo: str
    keyid: str
    created: str
    caps: list[str]
    fingerprint: str
    uids: list[UID] = field(default_factory=list)
    ssub: list[SubKey] = field(default_factory=list)


@dataclass
class PublicKey(BaseKey):
    """Class for public gpg keys"""


@dataclass
class SecretKey(BaseKey):
    """Class for private gpg keys"""
