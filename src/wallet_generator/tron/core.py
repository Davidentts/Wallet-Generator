from pathlib import Path

from mnemonic import Mnemonic
from tronpy.keys import PrivateKey
from bip32utils import BIP32Key, BIP32_HARDEN

from wallet_generator.common.encoding_tools import KeePass
from wallet_generator.common.schemas import Wallet, WalletRegistry
from wallet_generator.common.utils.input import get_password


def generate_seed_phrase(strength: int = 256) -> str:
    """Generate a new BIP39 seed phrase."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)


def generate_wallets(seed_phrase: str, count: int = 3) -> list[Wallet]:
    """Generate a list of Tron wallets from the seed phrase."""
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(seed_phrase)

    wallets: list[Wallet] = []
    for index in range(count):
        private_key = generate_private_key_from_seed(seed, index)
        address = private_key.public_key.to_base58check_address()
        wallets.append(Wallet(index, address, private_key.hex()))
    return wallets


def generate_private_key_from_seed(seed: bytes, index: int) -> PrivateKey:
    """Derive a private key from the seed using BIP44 path m/44'/195'/0'/0/index."""
    master_key = BIP32Key.fromEntropy(seed)
    path = [44 + BIP32_HARDEN, 195 + BIP32_HARDEN, 0 + BIP32_HARDEN, 0, index]

    key = master_key
    for p in path:
        key = key.ChildKey(p)

    return PrivateKey(key.PrivateKey())


def save_wallets_to_keepass(
    registry: WalletRegistry,
    path: Path,
    filename: str = "wallets.kdbx",
) -> None:
    """Save generated Tron wallets to a KeePass storage file."""
    password = get_password()
    keepass = KeePass(
        password=password,
        registry=registry,
        path=path,
        filename=filename,
    )
    keepass.add_seed_phrase(registry.main_group.seed_phrase)
    for group in registry:
        keepass.fill_group_with_wallets(group)
