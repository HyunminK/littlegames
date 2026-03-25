#!/usr/bin/env python3
import guess_game
import coinflip


def main():
    while True:
        print("\nChoose a game:")
        print("1. Guess Game")
        print("2. Coin Flip")
        print("3. Quit")

        try:
            choice = input("Enter your choice: ")
        except EOFError:
            print("\nNo input detected. Exiting.")
            break

        if choice == "1":
            guess_game.play()
        elif choice == "2":
            coinflip.play()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()