from pathlib import Path

from .input import get_password, get_list_of_groups_for_keepass
from wallet_generator.common.schemas import Wallet
from wallet_generator.common.encoding_tools import KeePass


def save_wallets_to_keepass(
    seed_phrase: str,
    wallets: list[Wallet],
    path: Path,
) -> None:
    """Save generated Tron wallets to a KeePass storage file."""
    password = get_password()
    groups = get_list_of_groups_for_keepass(maximum=len(wallets))
    keepass = KeePass(
        password=password,
        groups=groups,
        path=path,
    )
    keepass.add_seed_phrase(seed_phrase)
    if groups:
        chunk_size = len(wallets) // len(groups)
        chunks = [
            wallets[i : i + chunk_size] for i in range(0, len(wallets), chunk_size)
        ]
        for i in range(0, len(groups)):
            keepass.add_wallets_to_group(group_name=groups[i], wallets=chunks[i])
    else:
        keepass.add_wallets_to_group(wallets=wallets)


def save_wallets_to_file(
    wallets: list[Wallet],
    path: Path,
    filename: str = "tron_wallets.txt",
    add_private_key: bool = True,
) -> None:
    """Save generated Tron wallets to a file."""
    with open(path / filename, "w") as f:
        f.write("Main wallet:\n")
        f.write(f"Address: {wallets[0].address}\n")
        if add_private_key:
            f.write(f"Private key: {wallets[0].private_key}\n\n")

        f.write("Additional wallets:\n")
        for wallet in wallets[1:]:
            f.write(f"Address {wallet.index}: {wallet.address}\n")
            if add_private_key:
                f.write(f"Private key {wallet.index}: {wallet.private_key}\n\n")


def save_seed_to_file(
    seed_phrase: str,
    path: Path,
    filename: str = "seed_phrase.txt",
) -> None:
    """Save the seed phrase to a text file."""
    with open(path / filename, "w") as f:
        f.write(seed_phrase)
