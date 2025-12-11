from pathlib import Path

from wallet_generator.common.schemas import WalletRegistry


def save_wallets_to_file(
    registry: WalletRegistry,
    path: Path,
    filename: str = "tron_wallets_no_private.txt",
    add_private_key: bool = False,
) -> None:
    """Save generated Tron wallets to a file."""
    with open(path / filename, "w") as f:
        f.write(registry.to_str(add_private_key))


def save_seed_to_file(
    seed_phrase: str,
    path: Path,
    filename: str = "seed_phrase.txt",
) -> None:
    """Save the seed phrase to a text file."""
    with open(path / filename, "w") as f:
        f.write(seed_phrase)
