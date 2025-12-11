from pathlib import Path

from pykeepass import create_database, PyKeePass

from wallet_generator.common.schemas import (
    WalletRegistry,
    WalletGroup,
    MainWalletGroup,
)


class KeePass:

    def __init__(
        self,
        password: str,
        path: Path,
        registry: WalletRegistry = None,
        filename: str = "wallets.kdbx",
    ) -> None:
        self.db: PyKeePass = create_database(
            filename=path / filename,
            password=password,
        )
        self.keepass_groups = {}
        for group in registry.all_groups():
            grp = self.db.add_group(
                self.db.root_group,
                group_name=group.name,
                notes=group.description,
            )
            self.keepass_groups[group.name] = grp

    def fill_group_with_wallets(self, group: WalletGroup | MainWalletGroup) -> None:
        """
        The function copies wallets from the transferred group instance
        to the local group of the KeePass database
        """
        keepass_group = self.keepass_groups.get(group.name, self.db.root_group)
        for wallet in group.wallets:
            title = f"{wallet.address[:4]}...{wallet.address[-4:]}"
            self.db.add_entry(
                destination_group=keepass_group,
                title=title,
                username=wallet.address,
                password=wallet.private_key,
                notes=str(wallet.index),
            )
        self.db.save()

    def add_seed_phrase(self, seed_phrase: str) -> None:
        self.db.add_entry(
            destination_group=self.db.root_group,
            title="Seed phrase",
            username="Seed",
            password=seed_phrase,
        )
        self.db.save()
