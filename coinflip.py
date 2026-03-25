#!/usr/bin/env python3
import random


def flip_coin():
    """Return a random coin flip result."""
    return random.choice(["Heads", "Tails"])


def play():
    """Play coin flip(s); returns to caller when user declines or EOF."""
    print("Coin Flip")
    play_again = True

    while play_again:
        result = flip_coin()
        print(f"Result: {result}")

        # Keep asking until the user gives a valid replay choice.
        while True:
            try:
                ans = input("Flip again? (y/n): ").strip().lower()
            except EOFError:
                print("\nNo input detected. Returning to menu.")
                return

            if ans in ("y", "yes"):
                play_again = True
                break

            if ans in ("n", "no"):
                play_again = False
                break

            else:
                print("Please enter 'y' or 'n'.")


if __name__ == "__main__":
    play()
