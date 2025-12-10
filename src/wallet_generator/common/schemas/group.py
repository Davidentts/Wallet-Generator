from dataclasses import dataclass, field

from .wallet import Wallet


@dataclass
class WalletGroup:
    name: str
    description: str = ""
    wallets: list[Wallet] = field(default_factory=list)

    @property
    def actual_size(self) -> int:
        return len(self.wallets)

    def add_wallet(self, wallet: Wallet) -> None:
        """Add a wallet to the group."""
        self.wallets.append(wallet)

    def add_wallets(self, wallets: list[Wallet]) -> None:
        """Add multiple wallets to the group."""
        self.wallets.extend(wallets)

    def get_wallet_by_index(self, index: int) -> Wallet | None:
        """Find a wallet by its index."""
        for w in self.wallets:
            if w.index == index:
                return w
        return None

    def get_wallet_by_address(self, address: str) -> Wallet | None:
        """Find a wallet by its address."""
        for w in self.wallets:
            if w.address.lower() == address.lower():
                return w
        return None

    def summary(self) -> str:
        """Short info about the group."""
        return (
            f"Group name: {self.name}\n"
            f"Size: {self.actual_size}\n"
            f"Note: {self.description}"
        )

    def __iter__(self):
        return iter(self.wallets)

    def __repr__(self) -> str:
        return f"WalletGroup(name='{self.name}', size={self.actual_size}, description='{self.description})"


@dataclass
class MainWalletGroup(WalletGroup):
    name: str = field(init=False, default="main")
    seed_phrase: str = field(repr=False, default="")

    def __repr__(self) -> str:
        return f"MainWalletGroup(name='{self.name}', size={self.actual_size}, description='{self.description})"
