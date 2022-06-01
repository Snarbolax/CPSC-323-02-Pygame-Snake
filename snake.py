#!/usr/bin/env python3
"""
The module holds the main function to start the game.

snake.py, objects.py, and game_init.py were created
for Spring CPSC 481-04's Snake Game exercise.

The exercise is to write a snake game clone in
Python, using Pygame.

This module requires game_init.py (and objects.py)
to run.

Function:
main - run the game scenes in the appropriate order
"""

__author__ = "Kenneth Doan"
__email__ = "snarbolax@csu.fullerton.edu"
__version__ = "0.9"
__license__ = "LGPL 2.1"

import pygame
import game_init


def main():
    """Run the game scenes in the intended order.
    
    A screen displaying the rules is meant to be displayed
    first, the screen displaying the controls is meant to be
    displayed second, the title / start screen that prompts
    any key presses to start the game is displayed third, and
    the playable part of the game is displayed (and looped) last.
    """
    game_init.RuleScreen("Snake Game - Rules")
    game_init.InstructionScreen("Snake Game - Controls")
    game_init.StartScreen("Snake Game - Main Menu")
    while 1:
        game_init.MainGame("Snake Game")


# import guard
if __name__ == '__main__':
    pygame.init()
    main()
