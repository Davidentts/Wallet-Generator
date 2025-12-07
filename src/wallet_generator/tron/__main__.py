from wallet_generator.common.config import BASE_DIR
from wallet_generator.common.schemas import Wallet
from wallet_generator.common.utils.input import (
    get_wallet_count,
    get_is_convert_to_keepass,
)
from wallet_generator.common.utils.output import (
    save_seed_to_file,
    save_wallets_to_file,
    save_wallets_to_keepass,
)
from .core import generate_seed_phrase, generate_wallets


def main():
    try:
        print("Welcome to Tron wallet generator!")

        # Step 1: Get wallet count from user
        wallet_count = get_wallet_count()

        # Step 2: Generate and save seed phrase
        seed_phrase = generate_seed_phrase()
        save_seed_to_file(
            seed_phrase=seed_phrase,
            path=BASE_DIR,
        )

        # Step 3: Generate wallets
        wallets: list[Wallet] = generate_wallets(seed_phrase, count=wallet_count)

        # Step 4: Save wallets to files (with private keys and without)
        save_wallets_to_file(
            wallets=wallets,
            path=BASE_DIR,
        )
        save_wallets_to_file(
            wallets=wallets,
            path=BASE_DIR,
            add_private_key=False,  # List of wallets will be safe
            filename="tron_wallets_no_private.txt",
        )

        print(f"✅ Seed phrase saved to '{BASE_DIR}/seed_phrase.txt'")
        print(
            f"✅ {wallet_count} wallets saved to '{BASE_DIR}/tron_wallets.txt' and '{BASE_DIR}/tron_wallets_no_private.txt'"
        )

        # Step 5: Convert to KeePass
        if get_is_convert_to_keepass():
            save_wallets_to_keepass(
                seed_phrase=seed_phrase,
                wallets=wallets,
                path=BASE_DIR,
            )
            print("\n====================================")
            print("✅ KeePass database successfully created!")
            print(f"→ Database file: {BASE_DIR}/wallets.kdbx")
            print("====================================\n")
    except KeyboardInterrupt:
        print("\nProcess was interrupted!")


if __name__ == "__main__":
    main()
