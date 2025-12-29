from datetime import datetime
from pathlib import Path

from wallet_generator.common.config import BASE_DIR
from wallet_generator.common.encoding_tools.gpg import GPG
from wallet_generator.common.schemas import (
    Wallet,
    WalletRegistry,
)
from wallet_generator.common.utils.input import (
    get_wallet_count,
    ask_user_short,
    get_list_of_groups,
)
from wallet_generator.common.utils.output import (
    save_seed_to_file,
    save_wallets_to_file,
)
from .core import (
    generate_seed_phrase,
    generate_wallets,
    save_wallets_to_keepass,
    save_files_with_secrets,
    parsing_input_parameters,
)


def main():
    try:
        print("Welcome to Tron wallet generator!")

        save_dir = (
            Path(BASE_DIR)
            / f"tron_wallets_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}"
        )
        save_dir.mkdir(parents=True, exist_ok=True)
        encr_pass_file = parsing_input_parameters()

        wallet_count = get_wallet_count()
        registry = WalletRegistry()

        registry.main_group.seed_phrase = generate_seed_phrase()

        wallets: list[Wallet] = generate_wallets(
            registry.main_group.seed_phrase,
            count=wallet_count,
        )

        if ask_user_short("Would you like to distribute wallets into groups?"):
            get_list_of_groups(registry, maximum=wallet_count)
        registry.dist_wallets_into_groups(wallets)

        # gpg = GPG()
        # if ask_user_short(
        #     "Do you want to save wallets and seed to file without encryption?"
        # ):
        #     save_wallets_to_file(
        #         registry=registry,
        #         path=BASE_DIR,
        #         filename="tron_wallets.txt",
        #         add_private_key=True,
        #     )
        #     save_seed_to_file(
        #         seed_phrase=registry.main_group.seed_phrase,
        #         path=BASE_DIR,
        #     )
        #     save_wallets_to_file(
        #         registry=registry,
        #         path=BASE_DIR,
        #     )
        #     print(f"✅ Seed phrase saved to '{BASE_DIR}/seed_phrase.txt'")
        #     print(f"✅ {wallet_count} wallets saved to '{BASE_DIR}/tron_wallets.txt'")
        #     print(
        #         f"✅ {wallet_count} wallets saved to '{BASE_DIR}/tron_wallets_no_private.txt'"
        #     )
        keepass_file: Path | None = None
        if ask_user_short(question="Do you want to put wallets into keepass?"):
            keepass_file = save_wallets_to_keepass(
                registry=registry,
                path=save_dir,
                pass_file=encr_pass_file if encr_pass_file else None,
            )
            print("\n====================================")
            print("✅ KeePass database successfully created!")
            print(f"→ Database file: {save_dir}/wallets.kdbx")
            print("====================================\n")

        save_files_with_secrets(
            registry,
            encr_pass_file,
            save_dir,
            keepass_file=keepass_file if keepass_file is not None else None,
        )
    except KeyboardInterrupt:
        print("\nProcess was interrupted!")


if __name__ == "__main__":
    main()
