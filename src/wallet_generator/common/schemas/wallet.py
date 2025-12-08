from dataclasses import dataclass


@dataclass
class Wallet:
    index: int
    address: str
    private_key: str
