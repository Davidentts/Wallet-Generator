from pathlib import Path

from pykeepass import create_database, PyKeePass

from wallet_generator.common.schemas import Wallet


class KeePass:

    def __init__(
        self,
        password: str,
        path: Path,
        groups: list[str] | None = None,
        filename: str = "wallets.kdbx",
    ) -> None:
        self.db: PyKeePass = create_database(
            filename=path / filename,
            password=password,
        )
        self.groups = {}
        if groups:
            for name in groups:
                grp = self.db.add_group(self.db.root_group, name)
                self.groups[name] = grp

    def add_wallets_to_group(
        self, wallets: list[Wallet], group_name: str | None = None
    ) -> None:
        group = self.groups.get(group_name) if group_name else self.db.root_group
        for wallet in wallets:
            title = f"{wallet.address[:4]}...{wallet.address[-4:]}"
            self.db.add_entry(
                destination_group=group,
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
