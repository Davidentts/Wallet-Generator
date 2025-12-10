# from dataclasses import dataclass
#
#
# @dataclass
# class Wallet:
#     index: int
#     address: str
#     private_key: str
from dataclasses import dataclass, field


@dataclass
class Wallet:
    index: int
    address: str
    private_key: str = field(repr=False)

    def __repr__(self) -> str:
        shortened_pk = (
            self.private_key[:6] + "..." + self.private_key[-6:]
            if len(self.private_key) >= 6
            else self.private_key
        )
        return f"Wallet(index={self.index}, address='{self.address}', private_key='{shortened_pk}')"
