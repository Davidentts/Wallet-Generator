import math
import warnings

from .wallet import Wallet
from .group import WalletGroup, MainWalletGroup


class WalletRegistry:

    def __init__(self):
        self._groups: dict[str, WalletGroup | MainWalletGroup] = {
            "main": MainWalletGroup(description="Main group"),
        }

    @property
    def main_group(self) -> MainWalletGroup:
        return self._groups.get("main")

    @staticmethod
    def is_main_group(group: WalletGroup) -> bool:
        return type(group) is MainWalletGroup

    def add_group(self, group: WalletGroup) -> None:
        if group.name in self._groups:
            raise ValueError(f"Group {group.name} already exists")
        self._groups[group.name] = group

    def get_group_by_name(self, name: str) -> WalletGroup | None:
        return self._groups.get(name)

    def remove_group(self, group: WalletGroup) -> None:
        if type(group) is MainWalletGroup:
            raise ValueError("Cannot remove the main group!")
        self._groups.pop(group.name, None)

    def all_groups(self, include_main=False) -> list[WalletGroup]:
        if include_main:
            return list(self._groups.values())
        return [g for g in self._groups.values() if not self.is_main_group(g)]

    def dist_wallets_into_groups(self, wallets: list[Wallet]) -> None:
        """
        Function for distributing the list of wallets into groups.

        If the register contains only the main group, then all wallets
        will be automatically placed in it and a warning will be issued.

        If there are groups in the register other than main, then the
        main group will be ignored during distribution.
        """

        if len(self.all_groups(include_main=True)) == 1:
            warnings.warn("There is only one group!")
            self.main_group.add_wallets(wallets)
            return

        chunk_size = math.ceil(len(wallets) / len(self.all_groups()))
        chunks_wallets = [
            wallets[i : i + chunk_size] for i in range(0, len(wallets), chunk_size)
        ]
        chunks = zip(self.all_groups(), chunks_wallets)
        for group, ch_wallets in chunks:
            group.add_wallets(ch_wallets)

    def find_wallet_by_address(self, address: str) -> Wallet | None:
        """Search for a wallet by its address."""
        for group in self._groups.values():
            w = group.get_wallet_by_address(address)
            if w:
                return w
        return None

    def find_wallet_by_index(self, index: int) -> Wallet | None:
        """Search for a wallet by its index."""
        for group in self._groups.values():
            w = group.get_wallet_by_index(index)
            if w:
                return w
        return None

    def __iter__(self):
        """Iterate over the groups."""
        return iter(self._groups.values())

    def __repr__(self) -> str:
        return f"WalletRegistry(groups={self.all_groups()})"

    def __str__(self) -> str:
        return "\n".join([str(g) for g in self.all_groups(include_main=True)])

    def to_str(self, verbose: bool = False) -> str:
        return "\n\n".join(
            [g.to_str(verbose=verbose) for g in self.all_groups(include_main=True)]
        )
