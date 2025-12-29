import getpass
from collections.abc import Callable
from typing import TypeVar

from wallet_generator.common.schemas import WalletRegistry, WalletGroup


def get_wallet_count() -> int:
    """Ask the user for the number of wallets to generate and validate input."""
    while True:
        user_input = input("Enter the number of wallets to generate (min 1): ").strip()
        if user_input.isdigit():
            count = int(user_input)
            if count >= 1:
                return count
        print("Invalid input. Please enter a positive integer greater than 0.")


def ask_user_short(question: str) -> bool:
    """Ask the user for saving the wallets to a file without encryption."""
    while True:
        yes_or_no = input(f"{question} (y/n) ").strip()
        if yes_or_no == "y":
            return True
        if yes_or_no == "n":
            return False
        print("Please enter 'y' or 'n'")


T = TypeVar("T")
V = TypeVar("V")


def ask_user(
    question: str,
    options: list,
    func_for_print: Callable[[T], str],
    func_for_result: Callable[[T], V],
) -> V:
    options_dict = {i + 1: options[i] for i in range(len(options))}
    print(question)
    for num, option in options_dict.items():
        print(f"{num}. {func_for_print(option)}")
    while True:
        user_input = input(f"Please, enter a number from 1 to {len(options)}: ").strip()
        if user_input.isdigit():
            user_number = int(user_input)
            if 0 < user_number <= len(options):
                return func_for_result(options_dict.get(user_number))
        print("Invalid input.")


def get_password() -> str:
    while True:
        try:
            password = getpass.getpass("Enter password: ")
            confirm = getpass.getpass("Confirm password: ")
        except (getpass.GetPassWarning, Exception):
            print("⚠️ Ввод пароля скрыт недоступен, используется обычный ввод.")
            password = input("Enter password (visible): ")
            confirm = input("Confirm password (visible): ")

        if password != confirm:
            print("❌ Пароли не совпадают. Попробуйте снова.\n")
        elif not password.strip():
            print("⚠️ Пароль не может быть пустым.\n")
        else:
            print("✅ Пароль успешно установлен.")
            return password


def get_list_of_groups(registry: WalletRegistry, maximum: int) -> None:
    while True:
        group_name = input(
            f"Enter group name (Press 'Enter' to quit, max {maximum} groups): "
        )
        if group_name == "":
            break
        description = input(f"Enter description (Press 'Enter' to skip): ")
        registry.add_group(
            WalletGroup(
                name=group_name,
                description=description,
            )
        )
        if len(registry.all_groups()) == maximum:
            break
    return None
