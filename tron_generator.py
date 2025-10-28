from dataclasses import dataclass

from mnemonic import Mnemonic
from bip32utils import BIP32Key, BIP32_HARDEN
from tronpy.keys import PrivateKey


@dataclass
class Wallet:
    index: int
    address: str
    private_key: str


def main():
    # Step 1: Get wallet count from user
    wallet_count = get_wallet_count()

    # Step 2: Generate and save seed phrase
    seed_phrase = generate_seed_phrase()
    save_seed_to_file(seed_phrase)

    # Step 3: Generate wallets
    wallets: list[Wallet] = generate_wallets(seed_phrase, count=wallet_count)

    # Step 4: Save wallets to files (with private keys and without)
    save_wallets_to_file(wallets)
    save_wallets_to_file(
        wallets=wallets,
        filename="tron_wallets_no_private.txt",
        add_private_key=False,
    )

    print(f"✅ Seed phrase saved to 'seed_phrase.txt'")
    print(
        f"✅ {wallet_count} wallets saved to 'tron_wallets.txt' and tron_wallets_no_private.txt"
    )


def get_wallet_count() -> int:
    """Ask the user for the number of wallets to generate and validate input."""
    while True:
        user_input = input("Enter the number of wallets to generate (min 1): ").strip()
        if user_input.isdigit():
            count = int(user_input)
            if count >= 1:
                return count
        print("Invalid input. Please enter a positive integer greater than 0.")


def generate_seed_phrase(strength: int = 256) -> str:
    """Generate a new BIP39 seed phrase."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)


def save_seed_to_file(seed_phrase: str, filename: str = "seed_phrase.txt") -> None:
    """Save the seed phrase to a text file."""
    with open(filename, "w") as f:
        f.write(seed_phrase)


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


def save_wallets_to_file(
    wallets,
    filename: str = "tron_wallets.txt",
    add_private_key: bool = True,
) -> None:
    """Save generated Tron wallets to a file."""
    with open(filename, "w") as f:
        f.write("Main wallet:\n")
        f.write(f"Address: {wallets[0].address}\n")
        if add_private_key:
            f.write(f"Private key: {wallets[0].private_key}\n\n")

        f.write("Additional wallets:\n")
        for wallet in wallets[1:]:
            f.write(f"Address {wallet.index}: {wallet.address}\n")
            if add_private_key:
                f.write(f"Private key {wallet.index}: {wallet.private_key}\n\n")


if __name__ == "__main__":
    main()
