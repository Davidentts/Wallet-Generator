import getpass


def get_wallet_count() -> int:
    """Ask the user for the number of wallets to generate and validate input."""
    while True:
        user_input = input("Enter the number of wallets to generate (min 1): ").strip()
        if user_input.isdigit():
            count = int(user_input)
            if count >= 1:
                return count
        print("Invalid input. Please enter a positive integer greater than 0.")


def get_is_convert_to_keepass() -> bool:
    while True:
        yes_or_no = input("Do you want to put wallets into keepass? (y/n) ")
        if yes_or_no == "y":
            return True
        if yes_or_no == "n":
            return False
        print("Please enter 'y' or 'n'")


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


def get_list_of_groups_for_keepass(maximum: int) -> list[str] | None:
    list_of_groups = []
    while True:
        group_name = input(f"Enter group name ('end' to quit, max {maximum} groups): ")
        if group_name == "end":
            break
        if len(group_name) < maximum:
            list_of_groups.append(group_name)
        else:
            break
    if list_of_groups:
        return list_of_groups
    return None
