import random
import string

def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    characters = ""

    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters:
        return None

    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def main():
    print("===== Password Generator =====")

    try:
        length = int(input("Enter password length: "))

        if length <= 0:
            print("Password length must be greater than 0.")
            return

        upper = input("Include Uppercase? (y/n): ").lower() == 'y'
        lower = input("Include Lowercase? (y/n): ").lower() == 'y'
        digits = input("Include Numbers? (y/n): ").lower() == 'y'
        symbols = input("Include Special Characters? (y/n): ").lower() == 'y'

        password = generate_password(length, upper, lower, digits, symbols)

        if password:
            print("\nGenerated Password:")
            print(password)
        else:
            print("Select at least one character type.")

    except ValueError:
        print("Invalid input.")


if __name__ == "__main__":
    main()