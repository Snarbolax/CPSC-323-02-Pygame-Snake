#!/usr/bin/env python3
"""
The module contains all of the objects needed to
setup the scenes the player can view and interact
with.

snake.py, objects.py, and game_init.py were created
for Spring CPSC 481-04's Snake Game exercise.

The exercise is to write a snake game clone in
Python, using Pygame.

This module requires game_init.py to run.

Classes:
Body - Extends the Snake if it collides with an Apple.
Snake - Represent the Snake the player controls.
Apple - Give the player points if they collide with this.
ScoreText - Keeps track and display the player's score.
"""

__author__ = "Kenneth Doan"
__email__ = "snarbolax@csu.fullerton.edu"
__version__ = "0.9"
__license__ = "LGPL 2.1"

import random
import pygame
import game_init


class Body(pygame.sprite.Sprite):
    """A subclass of Pygame's Sprite class used to represent the Snake's body.

    It is meant to be structured as a doubly-linked list,
    where the _head member refers to the preceding Body object and
    the _tail member refers to the succeeding Body object.

    It currently doesn't append more than 1 Body object properly.
    Instead, it will spawn a static, persisting Body object at
    the Body object that is following Snake properly, each time the
    Snake collides with an Apple object.

    Public methods:
    update() - override the update method of Pygame's Sprite class.
    add_tail()

    Public instance variables:
    self.image
    self.rect
    self.area
    self.tail_rect
    """

    def __init__(self, head):
        """Body's class constructor.

        Keyword arguments:
        self - the Body object itself
        head - a Sprite that the Body is meant
               to follow and gain movement from.

        Return:
        Body (sprite) object

        Public instance variables:
        self.image
        self.rect
        self.area
        self.tail_rect
        """
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = game_init.load_image('snake_body.png',
                                                     0, (49, 49))

        self._head = head

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self._has_tail = False

        self.rect = self._head.tail_rect
        self.tail_rect = self.rect

    def update(self, body_group, game_display, background, count):
        """Override the update method of Pygame's Sprite class.

        Meant to blit and update the Body object upon a display
        surface and append another Body object to itself by
        calling the add_tail() method.

        Keyword arguments:
        self - the Body object itself
        body_group - the group that the body object
                     adds itself to upon initializing.
        game_display - the display surface that the
                       Body object blits and updates onto.
        background - the surface that the Body object uses
                     to blit and update more efficiently on
                     the display surface.
        count - a counter to keep track of how many Body
                objects succeed the current Body. A count of
                0 implies that the Body is the tail of the chain.
        """
        if not self.alive():
            self.add(body_group)

        if count == 0:
            game_display.blit(background, self.rect)

        self.tail_rect = self.rect

        if count > 0:
            if self._has_tail:
                # self.new_body.rect = self.tail_rect
                self.new_body.update(
                    body_group, game_display, background, count-1)
        else:
            self.add_tail()
        self.rect = self._head.tail_rect

        if count == 0:
            game_display.blit(self.image, self.rect)
            pygame.display.update((self.rect, self.tail_rect))

    def add_tail(self):
        """Append a tail by initializing a new Body object"""
        if not self._has_tail:
            self.new_body = Body(self)
            self._has_tail = True


class Snake(pygame.sprite.Sprite):
    """A subclass of Pygame's Sprite class used to represent the Snake's head.

    Snake calls update() to change its (rect)position,
    blit and updates itself upon a surface, and kills itself if it
    moves out of the dimensions of the window screen display or if
    it collides with a Body object.

    Public methods:
    update() - override the update method of Pygame's Sprite class.
    moveup()
    moveleft()
    movedown()
    moveright()
    grow_body()

    Public instance variables:
    self.image
    self.rect
    self.area
    self.state
    self.movepos
    self.tail_rect
    self.body
    """

    def __init__(self):
        """Head's class constructor.

        Return:
        Snake (sprite) object

        Public instance variables:
        self.image
        self.rect
        self.area
        self.tail_rect
        """
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = game_init.load_image('snake.png', 0, (49, 49))

        self._vertical_move_sound = game_init.load_sound("whiish.wav")
        self._horizontal_move_sound = game_init.load_sound("whoosh.wav")

        self._vertical_move_sound.set_volume(0.11)
        self._horizontal_move_sound.set_volume(0.11)

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self._updated = False

        self.state = "movedown"
        self.movepos = [0, 0]
        # sub 20 fps allows the snake to "jump" the length of its body.
        self.movepos[1] = self.movepos[1] + self.rect.width
        self.rect.midtop = self.area.midtop

        self._has_tail = False
        self.tail_rect = self.rect

        self._add_tail = 0
        self._tail_count = 0

        self.new_body = Body(self)

    def update(self, body_group, self_group, game_display, background):
        """Override the update method of Pygame's Sprite class.

        Blit and update the Snake object upon a display
        surface, updates the Snake's position by calling
        moveup(), movedown(), moveleft(), or moveright(), and
        kills itself if the Snake's position is entirely
        within the dimensions of the window screen display or if
        the Snake collides with a Body object.

        Keyword arguments:
        self - the Body object itself
        body_group - the sprite group that the Snake adds the first
                     body object to upon colliding with an Apple.
        self_group - the sprite group that the Snake is in. Used to
                     detect if Snake is alive or dead.
        game_display - the display surface that the
                       Snake object blits and updates onto.
        background - the surface that the Snake object uses
                     to blit and update more efficiently on
                     the display surface.
        """
        if self.alive():
            game_display.blit(background, self.rect)
            if self._has_tail:
                self.tail_rect = self.rect
                if self._tail_count > 0:
                    self._tail_count = self._add_tail
                self.new_body.update(body_group, game_display,
                                     background, self._tail_count)
                self._tail_count = 0
            newpos = self.rect.move(self.movepos)
            self.rect = newpos
            self._updated = True

            if not game_display.get_rect().contains(self.rect):
                pygame.display.update(self_group.draw(game_display))
                self.kill()
                game_display.blit(background, self.rect)
            if pygame.sprite.spritecollideany(self, body_group) is not None:
                pygame.display.update(self_group.draw(game_display))
                self.kill()
                game_display.blit(background, self.rect)
            pygame.display.update(self_group.draw(game_display))

    def moveup(self):
        """Subtract the Snake's height from its y position to move up."""
        if not (self.state == "movedown" or self.state == "moveup"):
            if self._updated:  # Prevents the snake from moving backwards.
                if self.alive():
                    self.movepos[1] = self.movepos[1] - self.rect.height
                    self.movepos[0] = 0
                    self.state = "moveup"
                    pygame.mixer.Sound.play(self._vertical_move_sound)
                    self._updated = False

    def moveleft(self):
        """Subtract the Snake's width from its x position to move left."""
        if not (self.state == "moveright" or self.state == "moveleft"):
            if self._updated:
                if self.alive():
                    self.movepos[0] = self.movepos[0] - self.rect.width
                    self.movepos[1] = 0
                    self.state = "moveleft"
                    pygame.mixer.Sound.play(self._horizontal_move_sound)
                    self._updated = False

    def movedown(self):
        """Add the Snake's height to its y position to move down."""
        if not (self.state == "moveup" or self.state == "movedown"):
            if self._updated:
                if self.alive():
                    self.movepos[1] = self.movepos[1] + self.rect.height
                    self.movepos[0] = 0
                    self.state = "movedown"
                    pygame.mixer.Sound.play(self._vertical_move_sound)
                    self._updated = False

    def moveright(self):
        """Add the Snake's width from its x position to move right."""
        if not (self.state == "moveleft" or self.state == "moveright"):
            if self._updated:
                if self.alive():
                    self.movepos[0] = self.movepos[0] + self.rect.width
                    self.movepos[1] = 0
                    self.state = "moveright"
                    pygame.mixer.Sound.play(self._horizontal_move_sound)
                    self._updated = False

    def grow_body(self):
        """Tell Snake to append a Body object to itself."""
        if self._has_tail:
            self._add_tail += 1
            self._tail_count = self._add_tail
        self._has_tail = True


class Apple(pygame.sprite.Sprite):
    """A subclass of Pygame's Sprite class used to represent an Apple.

    The Apple object blits, updates, and spawns itself within
    the dimensions of the window screen display, while avoiding to
    appear on the edges of the display surface.

    The Apple attempts to spawn every 5 seconds and a limit of 1 can
    only exist on the screen at any given.

    It will kill itself and update the Score sprite by 50 points if
    the Snake object collides with the Apple.

    Public methods:
    update() - override the update method of Pygame's Sprite class.

    Public instance variables:
    self.image
    self.rect
    """

    def __init__(self):
        """Apple's class constructor.

        Return:
        Apple (sprite) object

        Public instance variables:
        self.image
        self.rect
        """
        pygame.sprite.Sprite.__init__(self)  # call Sprite intializer
        self.image, self.rect = game_init.load_image('apple.png', 0, (50, 50))
        self._spawn_sound = game_init.load_sound("baby.wav")
        self._death_sound = game_init.load_sound("sneeze.wav")

        self._spawn_sound.set_volume(0.5)
        self._death_sound.set_volume(0.14)

        screen = pygame.display.get_surface()
        self._spawn_timer = 5

        self._area = screen.get_rect()
        self._pos = [random.randint(self._area.left+self.rect.width,
                                    self._area.right-self.rect.width),
                     random.randint(self._area.top+self.rect.height,
                                    self._area.bottom-self.rect.height)]
        self.rect.centerx, self.rect.centery = self._pos[0], self._pos[1]
        self._old_rect = (0, 0)

    def _spawn(self, snake, bodies):
        """Blit and update an Apple to a random location.

        Intended to only be called while the Apple object
        is not alive. The method will avoid spawning the
        Apple object on a Snake object, Body object, the
        last location of the Apple object before it was
        killed, and the edges of the window screen display.

        Keyword arguments:
        self - the Apple object itself
        snake - the Snake object that the method avoids
                spawning the Apple on
        bodies - the group that Body objects are kept in.
                 The method avoid spawning the Apple on
                 any of the members in this group.
        """
        while True:
            pos_x = random.randint(self._area.left+self.rect.width,
                                   self._area.right-self.rect.width)
            pos_y = random.randint(self._area.top+self.rect.height,
                                   self._area.bottom-self.rect.height)

            self._pos = [pos_x, pos_y]
            self.rect.centerx, self.rect.centery = self._pos[0], self._pos[1]
            if not ((pygame.sprite.collide_rect(snake, self)
                     and (pygame.sprite.spritecollideany(self, bodies))
                     and (self.rect == self._old_rect))):
                pygame.mixer.Sound.play(self._spawn_sound)
                break

    def update(self, snake, bodies, self_group,
               game_display, background, score_sprite):
        """Override the update method of Pygame's Sprite class.

        The Apple object blits, updates, and spawns itself within
        the dimensions of the window screen display, while avoiding to
        appear on the edges of the display surface.

        The Apple attempts to call _spawn() every 5 second and will
        only successfully call _spawn() if the Apple object is not alive.

        The Apple object kill itself and update the Score sprite by
        50 points if the Snake object collides with the Apple.

        Keyword arguments:
        self - the Apple object itself
        snake - the Snake object that is passed to _spawn(),
                to prevent the Apple from spawning on.
        bodies - the sprite group that is passed to _spawn(),
                 to prevent the Apple from spawning on the
                 group's members.
        self_group - the sprite group that the Apple is in.
                     Used to detect if Apple is alive or dead.
        game_display - the display surface that the
                       Apple object blits and updates onto.
        background - the surface that the Apple object uses
                     to blit and update more efficiently on
                     the display surface.
        score_sprite - the score sprite whose update method
                       that Apple calls upon to update the
                       player's score.
        """
        if self.alive():
            if not self.rect == self._old_rect:
                game_display.blit(background, self.rect)
                pygame.display.update(self_group.draw(game_display))
        if pygame.sprite.collide_rect(snake, self):
            if self.alive():
                if snake.alive():
                    snake.grow_body()

                    self.kill()
                    game_display.blit(background, self.rect)
                    pygame.display.update(self.rect)
                    pygame.mixer.Sound.play(self._death_sound)

                    score_sprite.update(game_display, background, 50)
        if self._spawn_timer <= 0:
            if not self.alive():
                self._spawn(snake, bodies)
                self.add(self_group)
                game_display.blit(background, self.rect)
                pygame.display.update(self_group.draw(game_display))
            self._spawn_timer = 5
        self._old_rect = self.rect


class ScoreText(pygame.sprite.Sprite):
    """A subclass of Pygame's Sprite class used to keep score.

    The ScoreText object represents the player's current score.
    It blits and updates itself at the bottom-left-hand corner
    of the screen.

    Public methods:
    update() - override the update method of Pygame's Sprite class.
    update_text()

    Public instance variables:
    self.score
    self.old_score
    self.font
    self.text
    self.textpos
    """

    def __init__(self, area, background):
        """ScoreText's class constructor.

        Keyword arguments:
        area - the dimensions of the window
               screen display. Used to help
               ScoreText find the bottom-left
               of the screen to blit and
               update itself to.
        background - the surface that ScoreText
                     uses to blit and update
                     itself efficiently.

        Return:
        ScoreText (sprite) object

        Public instance variables:
        self.score
        self.old_score
        self.font
        self.text
        self.textpos
        """
        pygame.sprite.Sprite.__init__(self)
        self.score = 0
        self.old_score = self.score

        self.font = pygame.font.Font(None, 36)

        self.text = self.font.render("Score: {0}".format(self.score), 1,
                                     (255, 255, 255), (0, 0, 0)).convert()
        self.text.set_colorkey((0, 0, 0))
        self.textpos = self.text.get_rect(
            bottomleft=area.get_rect().bottomleft)
        area.blit(background, self.textpos)
        area.blit(self.text, self.textpos)
        pygame.display.update(self.textpos)

    def update(self, area, background, added=0):
        """Override the update method of Pygame's Sprite class.

        This is intended to be called for every 3 seconds of
        the Snake being alive or each time the Snake collides
        with an Apple object. It will successfully update
        the text of ScoreText once it confirms that the
        score has been changed, to avoid unnecessary
        blitting.

        Keyword arguments:
        self - the ScoreText object itself
        area - the dimensions of the window
               screen display. Used to help
               ScoreText find the bottom-left
               of the screen to blit and
               update itself to.
        background - the surface that the ScoreText object uses
                     to blit and update more efficiently on
                     the display surface.

        Optional argument:
        added - the amount of points to be added
                to ScoreText's score count.
        """
        self.score += added
        if self.score != self.old_score:
            self.update_text(area)
            area.blit(background, self.textpos)
            area.blit(self.text, self.textpos)
            pygame.display.update(self.textpos)
            self.old_score = self.score

    def update_text(self, area):
        """Update how ScoreText is rendered with the new score.

        Is successfully called once the update()
        method confirms that the score has
        changed.

        Keyword arguments:
        self - the ScoreText object itself
        area - the dimensions of the window
               screen display. Used to help
               ScoreText find the bottom-left
               of the screen to blit and
               update itself to.
        """
        self.text = self.font.render("Score: {0}".format(self.score), 1,
                                     (255, 255, 255), (0, 0, 0)).convert()
        self.text.set_colorkey((0, 0, 0))
        self.textpos = self.text.get_rect(
            bottomleft=area.get_rect().bottomleft)
