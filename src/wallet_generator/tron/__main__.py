from wallet_generator.common.config import BASE_DIR
from wallet_generator.common.schemas import (
    Wallet,
    WalletRegistry,
)
from wallet_generator.common.utils.input import (
    get_wallet_count,
    ask_user,
    get_list_of_groups,
)
from wallet_generator.common.utils.output import (
    save_seed_to_file,
    save_wallets_to_file,
)
from .core import generate_seed_phrase, generate_wallets, save_wallets_to_keepass


def main():
    try:
        print("Welcome to Tron wallet generator!")

        wallet_count = get_wallet_count()
        registry = WalletRegistry()

        registry.main_group.seed_phrase = generate_seed_phrase()

        wallets: list[Wallet] = generate_wallets(
            registry.main_group.seed_phrase,
            count=wallet_count,
        )

        if ask_user("Would you like to distribute wallets into groups?"):
            get_list_of_groups(registry, maximum=wallet_count)
        registry.dist_wallets_into_groups(wallets)

        if ask_user("Do you want to save wallets and seed to file without encryption?"):
            save_wallets_to_file(
                registry=registry,
                path=BASE_DIR,
                filename="tron_wallets.txt",
                add_private_key=True,
            )
            save_seed_to_file(
                seed_phrase=registry.main_group.seed_phrase,
                path=BASE_DIR,
            )
            save_wallets_to_file(
                registry=registry,
                path=BASE_DIR,
            )
            print(f"✅ Seed phrase saved to '{BASE_DIR}/seed_phrase.txt'")
            print(f"✅ {wallet_count} wallets saved to '{BASE_DIR}/tron_wallets.txt'")
            print(
                f"✅ {wallet_count} wallets saved to '{BASE_DIR}/tron_wallets_no_private.txt'"
            )

        if ask_user(question="Do you want to put wallets into keepass?"):
            save_wallets_to_keepass(
                registry=registry,
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
