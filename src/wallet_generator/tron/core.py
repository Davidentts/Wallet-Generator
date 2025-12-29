import argparse
from dataclasses import dataclass
import sys
from pathlib import Path

from mnemonic import Mnemonic
from tronpy.keys import PrivateKey
from bip32utils import BIP32Key, BIP32_HARDEN

from wallet_generator.common.encoding_tools import KeePass
from wallet_generator.common.encoding_tools.gpg import GPG
from wallet_generator.common.schemas import Wallet, WalletRegistry
from wallet_generator.common.utils.input import get_password, ask_user_short, ask_user


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


def parsing_input_parameters() -> Path:
    parser = argparse.ArgumentParser(
        description="Processing the input file with password."
    )
    parser.add_argument(
        "--encrypted-password",
        "-p",
        type=str,
        help="Path to file with encrypted password.",
    )

    args = parser.parse_args()
    filepath = Path(args.encrypted_password).resolve()

    if not filepath.is_file():
        print(f"Error: file '{filepath}' not found", file=sys.stderr)
        sys.exit(1)

    return filepath


def save_files_with_secrets(
    registry: WalletRegistry,
    pass_file: Path,
    save_dir: Path,
    keepass_file: Path,
) -> None:

    @dataclass
    class FileParam:
        name: str
        filename: str
        data: str | None = None
        path_file: Path | None = None

    files_params = [
        FileParam(
            name="seed phrase",
            filename="seed_phrase",
            data=registry.main_group.seed_phrase,
        ),
        FileParam(
            name="wallets with private keys",
            filename="tron_wallets_SECRET",
            data=registry.to_str(verbose=True),
        ),
        FileParam(
            name="list of wallets", filename="tron_wallets", data=registry.to_str()
        ),
        FileParam(
            name="KeePass file", filename=keepass_file.name, path_file=keepass_file
        ),
    ]
    verbose = [
        "Save without encryption (not recommended)",
        "Encrypt using symmetric encryption",
        "Encrypt using asymmetric encryption",
        "Do not save",
    ]
    gpg = GPG()
    for params in files_params:
        result = ask_user(
            f"How do you want to save {params.name}?",
            verbose,
            func_for_print=lambda x: x,
            func_for_result=lambda x: x,
        )
        file_data: str | None = None
        match result:
            case "Save without encryption (not recommended)":
                file_data = params.data
                params.filename = params.filename + ".txt"
            case "Encrypt using symmetric encryption":
                if params.data is not None:
                    file_data = gpg.encrypt_message_symmetric(
                        message=params.data, password=gpg.decrypt_from_file(pass_file)
                    )
                    params.filename = params.filename + ".sym"
                elif params.path_file is not None:
                    gpg.encrypt_file_symmetric(
                        file=params.path_file, password=gpg.decrypt_from_file(pass_file)
                    )
            case "Encrypt using asymmetric encryption":
                public_key = ask_user(
                    f"What key would you like to use?",
                    gpg.public_keys,
                    func_for_print=lambda x: f"UID: {x.uids[0].name}, {x.uids[0].email} 0x{x.keyid} {x.created}",
                    func_for_result=lambda x: x,
                )
                if params.data is not None:
                    file_data = gpg.encrypt_message(
                        message=params.data, recipient=public_key
                    )
                    params.filename = params.filename + ".asc"
                elif params.path_file is not None:
                    gpg.encrypt_file(file=params.path_file, recipient=public_key)
        if file_data:
            file = save_dir / params.filename
            file.write_text(file_data)


def save_wallets_to_keepass(
    registry: WalletRegistry,
    path: Path,
    filename: str = "wallets.kdbx",
    pass_file: Path | None = None,
) -> Path:
    """Save generated Tron wallets to a KeePass storage file."""
    if pass_file:
        gpg = GPG()
        password = gpg.decrypt_from_file(pass_file)
    else:
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

    return path / filename
