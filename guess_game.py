#!/usr/bin/env python3
import random


def new_game():
    """Create a new guess game state."""
    return {"target": random.randint(1, 100), "attempts": 0}


def evaluate_guess(target, attempts, guess):
    """Evaluate a guess and return feedback, updated attempts, and win state."""
    attempts += 1
    if guess < target:
        return "Higher.", attempts, False
    if guess > target:
        return "Lower.", attempts, False
    return f"Correct! You guessed it in {attempts} attempts.", attempts, True


def play():
    print("Guess the number between 1 and 100!")
    game = new_game()

    while True:
        try:
            guess = int(input("Your guess: "))
        except EOFError:
            print("Exiting game. Goodbye.")
            return
        except ValueError:
            print("Please enter an integer.")
            continue

        message, game["attempts"], won = evaluate_guess(
            game["target"], game["attempts"], guess
        )
        print(message)
        if won:
            return


if __name__ == "__main__":
    play()
