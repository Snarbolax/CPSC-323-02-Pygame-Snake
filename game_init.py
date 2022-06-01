#!/usr/bin/env python3
"""
The module contains all of the functions and classes
necessary to display scenes to the player and to
save some details of the last time that they've played
to a last_session_info.json file.

If the player performs well enough, this module also
allows the game to update the leaderboard.json file
with the player's score.

snake.py, objects.py, and game_init.py were created
for Spring CPSC 481-04's Snake Game exercise.

The exercise is to write a snake game clone in
Python, using Pygame.

This module requires objects.py to run.

Classes:
MainGame
InstructionScreen
RuleScreen
StartScreen

Functions:
load_image
load_sound
"""

__author__ = "Kenneth Doan"
__email__ = "snarbolax@csu.fullerton.edu"
__version__ = "0.9"
__license__ = "LGPL 2.1"

import datetime
import json
import sys
import os
import pygame
import objects


class _Scene(pygame.Surface):
    """A subclass of Pygame's Surface object to subclass from.

    The Scene class is setup so that future Scene
    subclasses have a default caption, framerate cap,
    resolution, black background, and initialized
    Pygame clock.
    """

    def __init__(self, caption="Insert Caption Here",
                 framerate_cap=60, size=(640, 640)):
        super().__init__(size)
        self._framerate_cap = framerate_cap
        # To be used as self.clock.tick(self.framerate_cap)
        self._clock = pygame.time.Clock()

        self._caption = caption

        self._resolution = size
        self._screen = pygame.display.set_mode(self._resolution)

        if not pygame.display.get_init():
            pygame.display.init()
        pygame.display.set_caption(self._caption)
        pygame.display.set_allow_screensaver(True)

        self._active = True

        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill((0, 0, 0))
        self._background = self._background.convert()
        self._screen.blit(self._background, (0, 0))
        pygame.display.update()


class MainGame(_Scene):
    """A subclass of the Scene class for the player to play in.

    The class is where game objects from objects.py are setup
    to interact with each other, for the player to play the
    game and control the Snake object.

    The framerate cap has been changed from the default of 60 FPS
    to 6 FPS, in order to allow the Snake to visibly move in the
    length of its body while also giving the player a reasonable
    amount of time to react to the movement of the Snake.

    The MainGame class also calls _json_update(), _game_over(),
    and _leaderboard() once the player-controlled Snake is killed.

    The MainGame class is meant to be called after calling the
    RuleScreen, InstructionScreen, and StartScreen classes.

    The player is able to start a new game session by transitioning
    from the displayed leaderboard with any key input.
    """

    def __init__(self, caption="Insert Caption Here",
                 framerate_cap=6, size=(640, 640)):
        super().__init__(caption, framerate_cap, size)
        self._dt = 0
        self._add_time_score = pygame.USEREVENT + 1
        pygame.time.set_timer(self._add_time_score, 3*1000)

        self._snake = objects.Snake()
        self._apple = objects.Apple()
        self._scores = objects.ScoreText(self._screen, self._background)

        self._snake_appr = pygame.sprite.RenderUpdates(self._snake)
        self._food_appr = pygame.sprite.RenderUpdates(self._apple)
        self._body_group = pygame.sprite.RenderUpdates(self._snake.new_body)

        self._time_played = 0

        self._session_info = {
            "Date": datetime.date.today().strftime("%Y/%m/%d"),
            "Time Played (in seconds)": int(self._time_played),
            "Score": 0
        }

        while self._active:
            if not self._snake.alive():
                self._session_info[
                    "Time Played (in seconds)"] = int(self._time_played)
                self._session_info["Score"] = self._scores.score

                _json_update(self._session_info)
                _game_over(self._screen, self._background)
                _leaderboard(self._screen)
                self._active = False

            self._apple._spawn_timer -= self._dt

            self._apple.update(self._snake, self._body_group, self._food_appr,
                               self._screen, self._background, self._scores)

            # key inputs
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                    or (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE)):
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self._snake.moveup()
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self._snake.moveleft()
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self._snake.movedown()
                    elif (event.key == pygame.K_RIGHT
                          or event.key == pygame.K_d):
                        self._snake.moveright()
                elif event.type == self._add_time_score:
                    if self._snake.alive():
                        self._scores.update(self._screen, self._background, 5)

            self._snake_appr.update(self._body_group,
                                    self._snake_appr, self._screen,
                                    self._background)
            self._dt = self._clock.tick(self._framerate_cap) / 1000
            if self._snake.alive():
                self._time_played += self._dt


def _json_update(dict_obj):
    """Update last_session_info.json and leaderboard.json.

    The function updates a 'last_session_info.json' of
    the player's last played session with the date of the
    session, the lifetime (in seconds) of the player's Snake,
    and the score achieved.

    If the player performs well enough, the function will
    also update a 'leaderboard.json' file with the details
    of the player's session by replacing the values of a 'rank'
    (e.g. 'Tenth Place', 'Eighth Place', .etc) dictionary key.

    It is only meant to be called upon by the
    MainGame class.

    Keyword arguments:
    dict_obj - the Dictionary object with details of the player's
               session that MainGame passes to the function to
               dump into a JSON object.
               The JSON object will be written into a
               'last_session_info.json' file.
    """
    json_session = json.dumps(dict_obj, indent=3)
    board_update = False

    with open("last_session_info.json", "w") as outfile:
        outfile.write(json_session)
        outfile.close()

    with open('leaderboard.json', 'r') as openfile:
        input_dictionary = json.load(openfile)
        for place in input_dictionary:
            player_val = dict_obj["Score"]
            board_val = input_dictionary[place]["Score"]
            if player_val > board_val:
                input_dictionary[place]["Date"] = dict_obj["Date"]
                input_dictionary[
                    place]["Time Played (in seconds)"] = dict_obj[
                        "Time Played (in seconds)"]
                input_dictionary[place]["Score"] = dict_obj["Score"]
                board_update = True
                break
        openfile.close()

    if board_update:
        with open("leaderboard.json", "w") as outfile:
            json_input = json.dumps(input_dictionary, indent=10)
            outfile.write(json_input)
            outfile.close()


def _leaderboard(scene_screen):
    """Display the leaderboard of the game to the player.

    It loads the top 10 scores from a 'leaderboard.json'
    file with the date each score was achieved, the
    lifetime (in seconds) of the Snake of the respective
    score, and the rank of the score in descending order.

    The function also prompts the player to try again
    by pressing any key after transitioning from the
    leaderboard.
    It is only meant to be called upon by the
    MainGame class.

    Keyword arguments:
    scene_screen - the display surface that the function
                   renders text onto.
    """
    background = pygame.Surface(scene_screen.get_size())
    background.fill((220, 220, 220))
    background = background.convert()

    header_font = pygame.font.Font(None, 86)
    text_font = pygame.font.Font(None, 28)
    prompt_font = pygame.font.Font(None, 36)

    prompt_font.set_underline(True)

    box_rect = scene_screen.get_rect()
    box_rect.size = (box_rect.width*0.65, box_rect.height*0.65)
    box_rect.center = scene_screen.get_rect().center

    header = header_font.render("Leaderboard", 1, (0, 0, 0),
                                (220, 220, 220)).convert()
    header.set_colorkey((220, 220, 220))
    header_pos = header.get_rect(midtop=box_rect.midtop)
    scene_screen.blit(background, header_pos)
    scene_screen.blit(header, header_pos)

    # Place, Score, Played, Date
    display_text = text_font.render("Score", 1, (0, 0, 0),
                                    (220, 220, 220)).convert()
    display_text.set_colorkey((220, 220, 220))
    display_text_pos = display_text.get_rect(center=box_rect.center)
    display_text_pos.y -= 137
    display_text_pos.x -= 40
    scene_screen.blit(background, display_text_pos)
    scene_screen.blit(display_text, display_text_pos)

    display_text = text_font.render("Lifetime", 1, (0, 0, 0),
                                    (220, 220, 220)).convert()
    display_text_pos = display_text.get_rect(center=box_rect.center)
    display_text_pos.y -= 137
    display_text_pos.x += 40
    scene_screen.blit(background, display_text_pos)
    scene_screen.blit(display_text, display_text_pos)

    display_text = text_font.render("Date", 1, (0, 0, 0),
                                    (220, 220, 220)).convert()
    display_text_pos = display_text.get_rect(center=box_rect.center)
    display_text_pos.y -= 137
    display_text_pos.x += 150
    scene_screen.blit(background, display_text_pos)
    scene_screen.blit(display_text, display_text_pos)
    with open('leaderboard.json', 'r') as openfile:
        input_dictionary = json.load(openfile)

        display_text = text_font.render("1st Place", 1, (0, 0, 0),
                                        (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y -= 107
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(input_dictionary["First Place"]["Score"]), 1,
            (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y -= 107
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["First Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y -= 107
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["First Place"]["Date"]), 1,
            (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y -= 107
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render("2nd Place", 1, (0, 0, 0),
                                        (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 81
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Second Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 81
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Second Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 81
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Second Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 81
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "3rd Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 55
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Third Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 55
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Third Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 55
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Third Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 55
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "4th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 29
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fourth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 29
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fourth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 29
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fourth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 29
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "5th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 3
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fifth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 3
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fifth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 3
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Fifth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y -= 3
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "6th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y += 23
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Sixth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 23
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Sixth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 23
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Sixth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 23
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "7th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y += 49
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Seventh Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 49
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Seventh Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 49
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Seventh Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 49
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "8th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y += 75
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Eighth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 75
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Eighth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 75
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Eighth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 75
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "9th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y += 101
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Ninth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 101
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Ninth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 101
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(input_dictionary["Ninth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 101
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "10th Place", 1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(center=box_rect.center)
        display_text_pos.y += 127
        display_text_pos.x -= 150
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Tenth Place"]["Score"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 127
        display_text_pos.x -= 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(
                input_dictionary["Tenth Place"]["Time Played (in seconds)"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 127
        display_text_pos.x += 40
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

        display_text = text_font.render(
            "{0}".format(input_dictionary["Tenth Place"]["Date"]),
            1, (0, 0, 0), (220, 220, 220)).convert()
        display_text_pos = display_text.get_rect(
            center=box_rect.center)
        display_text_pos.y += 127
        display_text_pos.x += 148
        scene_screen.blit(background, display_text_pos)
        scene_screen.blit(display_text, display_text_pos)

    prompt = prompt_font.render(
        "Press Any Key to Continue", 1, (0, 0, 0),
        (220, 220, 220)).convert()
    prompt.set_colorkey((220, 220, 220))
    prompt_pos = prompt.get_rect(midbottom=box_rect.midbottom)
    prompt_pos.y -= 10
    scene_screen.blit(background, prompt_pos)
    scene_screen.blit(prompt, prompt_pos)

    pygame.display.update((box_rect, header_pos, prompt_pos))

    while header_pos.y <= 382:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE)):
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                background.fill((0, 0, 0))
                scene_screen.blit(background, (0, 0))

                prompt = prompt_font.render(
                    "Press Any Key to Try Again", 1,
                    (255, 255, 255), (0, 0, 0)).convert()
                prompt.set_colorkey((0, 0, 0))
                prompt_pos = prompt.get_rect(
                    center=scene_screen.get_rect().center)
                scene_screen.blit(background, prompt_pos)
                scene_screen.blit(prompt, prompt_pos)

                display_text = text_font.render(
                    "Press the Escape Key to Exit the Game", 1,
                    (255, 255, 255), (0, 0, 0)).convert()
                display_text.set_colorkey((0, 0, 0))
                display_text_pos = display_text.get_rect(
                    center=scene_screen.get_rect().center)
                display_text_pos.y += 152
                scene_screen.blit(background, display_text_pos)
                scene_screen.blit(display_text, display_text_pos)

                pygame.display.update((box_rect, prompt_pos))
                header_pos.y += 200


class InstructionScreen(_Scene):
    """A subclass of the Scene class to display controls to the player.

    The class calls _instructions() to blit the controls of the
    game on and update the display surface, while using the default
    settings of the Scene class.

    The InstructionScreen class is meant to be called after calling
    the RuleScreen class and before calling the MainGame and
    StartScreen classes.

    The player can transition from this scene with
    any key input.
    """

    def __init__(self, caption="Insert Caption Here",
                 framerate_cap=60, size=(640, 640)):
        super().__init__(caption, framerate_cap, size)

        _instructions(self._screen, self._background)
        while self._active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    self._active = False


class RuleScreen(_Scene):
    """A subclass of the Scene class to display the rules to the player.

    The class calls _rules() to blit the rules of the
    game on and update the display surface, while using the default
    settings of the Scene class.

    The RuleScreen class is meant to be called first, before
    calling any of the other Scene classes.

    The player can transition from this scene with
    any key input.
    """

    def __init__(self, caption="Insert Caption Here",
                 framerate_cap=60, size=(640, 640)):
        super().__init__(caption, framerate_cap, size)

        _rules(self._screen, self._background)
        while self._active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    self._screen.blit(self._background, (0, 0))
                    self._active = False


class StartScreen(_Scene):
    """A subclass of the Scene class to prompt to start the game.

    The class blits the title of the game, the Snake, and the
    prompt to start the game (i.e. 'Press Any Key to Start') on
    and update the display surface, while using the default
    settings of the Scene class.

    The StartScreen class is meant to be called after
    calling the RuleScreen and InstructionScreen classes and
    before calling the MainGame class.

    The player can transition from this scene with
    any key input.
    """

    def __init__(self, caption="Insert Caption Here",
                 framerate_cap=60, size=(640, 640)):
        super().__init__(caption, framerate_cap, size)

        self._area = self._background.get_rect()
        self._header_font = pygame.font.Font(None, 86)
        self._prompt_font = pygame.font.Font(None, 36)

        self._prompt_font.set_underline(True)

        self._title_snake, self._title_snake_pos = load_image(
            "snake.png", 0, (300, 300))
        self._title_snake_pos.center = self._area.center
        self._screen.blit(self._title_snake, self._title_snake_pos)

        header = self._header_font.render(
            "SNAKE GAME", 1, (255, 255, 255)).convert_alpha()
        header_pos = header.get_rect(center=self._area.center)
        self._screen.blit(header, header_pos)

        prompt = self._prompt_font.render(
            "Press Any Key to Start", 1, (255, 255, 255), (0, 0, 0)).convert()
        prompt.set_colorkey((0, 0, 0))
        prompt_pos = prompt.get_rect(midbottom=self._area.midbottom)
        prompt_pos.y -= 152
        self._screen.blit(self._background, prompt_pos)
        self._screen.blit(prompt, prompt_pos)

        pygame.display.update((self._title_snake_pos, header_pos, prompt_pos))

        while self._active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    self._screen.blit(self._background, (0, 0))
                    self._active = False


def _game_over(scene_screen, background):
    """Display this screen if the Snake object is killed.

    Signifies the end of the game.
    The player can transition from this screen by
    pressing any key.
    It is only meant to be called upon by the
    MainGame class.

    Keyword arguments:
    scene_screen - the display surface that the function
                   renders text onto.
    background - the surface that the function uses
                 to render text more efficiently on
                 the display surface.
    """
    pygame.display.set_caption("Snake Game - Game Over")
    area = background.get_rect()

    header_font = pygame.font.Font(None, 86)
    prompt_font = pygame.font.Font(None, 36)

    prompt_font.set_underline(True)

    player_death_sound = load_sound("church_bell.wav")
    player_death_sound.set_volume(0.14)

    header = header_font.render("GAME OVER", 1, (255, 255, 255),
                                (0, 0, 0)).convert()
    header.set_colorkey((0, 0, 0))
    header_pos = header.get_rect(center=area.center)
    scene_screen.blit(background, header_pos)
    scene_screen.blit(header, header_pos)

    prompt = prompt_font.render("Press Any Key to Continue", 1,
                                (255, 255, 255), (0, 0, 0)).convert()
    prompt.set_colorkey((0, 0, 0))
    prompt_pos = prompt.get_rect(midbottom=area.midbottom)
    prompt_pos.y -= 152
    scene_screen.blit(background, prompt_pos)
    scene_screen.blit(prompt, prompt_pos)

    pygame.mixer.Sound.play(player_death_sound, 0)
    pygame.display.update((header_pos, prompt_pos))

    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                active = False


def _rules(scene_screen, background):
    """Display the rules of the game to the player.

    It is only meant to be called upon by the
    RuleScene class.

    Keyword arguments:
    scene_screen - the display surface that the function
                   renders text onto.
    background - the surface that the function uses
                 to render text more efficiently on
                 the display surface.
    """
    header_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 28)
    prompt_font = pygame.font.Font(None, 36)

    header_font.set_underline(True)
    prompt_font.set_bold(True)

    header = header_font.render("RULES", 1,
                                (255, 255, 255), (0, 0, 0)).convert()
    header.set_colorkey((0, 0, 0))
    header_pos = header.get_rect(midtop=background.get_rect().midtop)
    header_pos.y += 4
    scene_screen.blit(header, header_pos)

    test_display = text_font.render(
        "1) Score points by keeping the snake alive and eating apples.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display.set_colorkey((0, 0, 0))
    test_display_pos = test_display.get_rect(
        center=background.get_rect().center)
    test_display_pos.y -= 98
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "2) The game ends when the snake's head touches", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 52
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "     its own body or moves outside the window screen.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 26
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "3) Eating apples will elongate the snake's body.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 52
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "4) The player (snake) only has one life.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 52
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "     Ending the game requires the player to", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 26
    scene_screen.blit(test_display, test_display_pos)

    test_display = text_font.render(
        "     start from the beginning again.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    test_display_pos.y += 26
    scene_screen.blit(test_display, test_display_pos)

    prompt = prompt_font.render(
        "     Press Any Key (except for Escape) to Continue", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    prompt_pos = prompt.get_rect(
        midbottom=background.get_rect().midbottom)
    prompt_pos.y -= 4
    scene_screen.blit(prompt, prompt_pos)

    example_image, example_rect = load_image('snake.png', 0, (110, 110))
    example_rect.x = background.get_rect().centerx * 0.92
    example_rect.y = background.get_rect().centery * 0.38
    scene_screen.blit(example_image, example_rect)

    example_image, example_rect = load_image('apple.png', 0, (110, 110))
    example_rect.x = background.get_rect().centerx * 1.6
    example_rect.y = background.get_rect().centery * 0.34
    scene_screen.blit(example_image, example_rect)

    pygame.display.update()


def _instructions(scene_screen, background):
    """Display the controls of the game to the player.

    It is only meant to be called upon by the
    InstructionScene class.

    Keyword arguments:
    scene_screen - the display surface that the function
                   renders text onto.
    background - the surface that the function uses
                 to render text more efficiently on
                 the display surface.
    """
    header_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 28)
    or_font = pygame.font.Font(None, 28)
    prompt_font = pygame.font.Font(None, 36)

    header_font.set_underline(True)
    or_font.set_italic(True)
    prompt_font.set_bold(True)

    header = header_font.render(
        "CONTROLS", 1, (255, 255, 255), (0, 0, 0)).convert()
    header.set_colorkey((0, 0, 0))
    header_pos = header.get_rect(
        midtop=background.get_rect().midtop)
    header_pos.y += 4
    scene_screen.blit(header, header_pos)

    text_display = text_font.render(
        "W = Up", 1, (255, 255, 255), (0, 0, 0)).convert()
    text_display.set_colorkey((0, 0, 0))
    text_display_pos = text_display.get_rect(
        center=background.get_rect().center)
    text_display_pos.y -= 98
    scene_screen.blit(text_display, text_display_pos)

    text_display = text_font.render("A = Left, S = Down, D = Right", 1,
                                    (255, 255, 255), (0, 0, 0)).convert()
    text_display_pos = text_display.get_rect(
        center=background.get_rect().center)
    text_display_pos.y -= 72
    scene_screen.blit(text_display, text_display_pos)

    or_text = or_font.render("or", 1, (255, 255, 255), (0, 0, 0)).convert()
    or_text.set_colorkey((0, 0, 0))
    or_text_pos = or_text.get_rect(
        center=background.get_rect().center)
    or_text_pos.y -= 36
    scene_screen.blit(or_text, or_text_pos)

    text_display = text_font.render(
        "Up Arrow = Up", 1, (255, 255, 255), (0, 0, 0)).convert()
    text_display_pos = text_display.get_rect(
        center=background.get_rect().center)
    scene_screen.blit(text_display, text_display_pos)

    text_display = text_font.render(
        "Left Arrow = Left, Down Arrow = Down, Right Arrow = Right", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    text_display_pos = text_display.get_rect(
        center=background.get_rect().center)
    text_display_pos.y += 26
    scene_screen.blit(text_display, text_display_pos)

    text_display = text_font.render(
        "Press the \"Escape\" key to quit from the game any time.", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    text_display_pos = text_display.get_rect(
        center=background.get_rect().center)
    text_display_pos.y += 104
    scene_screen.blit(text_display, text_display_pos)

    prompt = prompt_font.render(
        "Press Any Key (except for Escape) to Continue", 1,
        (255, 255, 255), (0, 0, 0)).convert()
    prompt.set_colorkey((0, 0, 0))
    prompt_pos = prompt.get_rect(
        midbottom=background.get_rect().midbottom)
    prompt_pos.y -= 4
    scene_screen.blit(prompt, prompt_pos)

    pygame.display.update()


def load_image(name, is_alpha=1, resize=(0, 0), colorkey=None):
    """Load and return a specified image file if able.

    Keyword argument:
    name - the name of the file to load. It is
           expected to be found in the 'images'
           subdirectory.

    Optional arguments:
    is_alpha - tells the function if the image is meant
               to be returned as a per pixel alpha surface.
               Nonzero arguments indicate that the image is
               to not be returned as a per pixel alpha surface.
               The default argument is a nonzero (i.e. 1).
    resize - resizes the surface to be returned if given a
             dimensions argument.
             Default is (0, 0) (i.e. no resizing),
    colorkey - Specifies the colorkey of the surface if given
               an argument.
               Default is None.

    Return:
    a Pygame surface object of the requested image
    and the pygame rect object of the surface.

    Exception:
    Raise SystemExit - if the specified file is not
                       found within the 'images'
                       subdirectory, the program will
                       exit the user from Python with
                       a 'Cannot load image:' message.
    """
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit from message

    if resize != (0, 0):
        image = pygame.transform.smoothscale(image, resize)

    if is_alpha == 0:
        image = image.convert_alpha()
    elif is_alpha != 0:
        image = image.convert()
    if is_alpha != 0 and colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    """Load and return a specified sound file if able.

    Keyword argument:
    name - the name of the file to load. It is
           expected to be found in the 'sounds'
           subdirectory.

    Return:
    a Pygame Sound object of the requested sound

    Exception:
    Raise SystemExit - if the specified file is not
                       found within the 'sounds'
                       subdirectory, the program will
                       exit the user from Python with
                       a 'Cannot load sound:' message.
    """
    fullname = os.path.join('sounds', name)

    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound:', fullname)
        raise SystemExit from message
    return sound
