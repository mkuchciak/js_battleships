from board import Board
from menu import *
from datetime import date
import math
import random
import pygame.time
import getpass


class Game:
    def __init__(self):
        pygame.init()
        self.running = True  # true when the game is on
        self.playing = False  # true when player is playing the game, which means he's not in the menu
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.ESC_KEY = False, False, False, False
        self.DISPLAY_WIDTH = 960
        self.DISPLAY_HEIGHT = 800
        self.display = pygame.Surface((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.window = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.font_name = pygame.font.get_default_font()
        self.font_size_title = 40
        self.font_size_basic = 25
        self.square_size = 40
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.main_menu = MainMenu(self)
        self.options = OptionsMenu(self)
        self.leaderboard = LeaderboardMenu(self)
        self.credits = CreditsMenu(self)
        self.current_menu = self.main_menu
        self.player_board = Board(self)
        self.computer_board = Board(self)
        self.computer_board.generate_computers_board()
        self.reverse_icon = pygame.image.load("reverse.jpg")
        self.placing_phase = True
        self.shooting_phase = False
        self.winner = getpass.getuser()
        self.clicks = 0
        self.ending = False
        self.results_file = "results.txt"
        self.result_saved = False
        self.sounds = True
        self.explosion_sound = pygame.mixer.Sound("explosion.wav")

    # basic loop running the app
    def game_loop(self):
        clock = pygame.time.Clock()
        while self.playing:
            clock.tick(60)
            self.check_events()
            if self.ESC_KEY:
                self.playing = False
            self.display.fill(self.BLACK)

            self.player_board.draw_board(self.square_size, 8 * self.square_size)  # drawing player's board
            self.computer_board.draw_board(13 * self.square_size, 8 * self.square_size)  # drawing computer's board
            self.draw_text("Friendly waters", self.font_size_basic, self.DISPLAY_WIDTH / 4, 19 * self.square_size)  # static text
            self.draw_text("Enemy waters", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4, 19 * self.square_size)  # static text
            self.draw_shipbox()  # drawing shipbox - box to reverse ships
            self.draw_text_above_shipbox()
            self.draw_text_next_to_shipbox()

            self.window.blit(self.display, (0, 0))
            pygame.display.update()
            self.reset_keys()

    # handling key and mouse action
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # ending the game
                self.running = False
                self.playing = False
                self.current_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_ESCAPE:
                    self.ESC_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
            if event.type == pygame.MOUSEBUTTONUP:
                position = pygame.mouse.get_pos()
                # if reverse icon clicked
                if 10 * self.square_size < position[0] < 11 * self.square_size and \
                        6 * self.square_size < position[1] < 7 * self.square_size and self.placing_phase:
                    if self.player_board.ships_list[0].horizontal:
                        self.player_board.ships_list[0].horizontal = False
                    else:
                        self.player_board.ships_list[0].horizontal = True
                # if clicked on the player's board and it's placing_phase
                if self.square_size < position[0] < 11 * self.square_size and \
                        8 * self.square_size < position[1] < 18 * self.square_size and self.placing_phase:
                    # checks if ship can be placed on the board (no collisions or end of board), if so updates board
                    if self.player_board.ship_can_be_placed(position[0], position[1]):
                        if self.player_board.ships_list[0].horizontal:
                            for square in range(self.player_board.ships_list[0].length):
                                self.player_board.board[self.player_board.get_row_on_board(position[1])][self.player_board.get_column_on_board(position[0] + square * self.square_size)] = self.player_board.ship_square
                            self.player_board.ships_list.pop(0)
                        else:
                            for square in range(self.player_board.ships_list[0].length):
                                self.player_board.board[self.player_board.get_row_on_board(position[1] + square * self.square_size)][self.player_board.get_column_on_board(position[0])] = self.player_board.ship_square
                            self.player_board.ships_list.pop(0)
                        if len(self.player_board.ships_list) == 0:
                            self.placing_phase = False
                            self.shooting_phase = True
                # if clicked on computer's board and it's shooting_phase
                if 13 * self.square_size < position[0] < 23 * self.square_size and 8 * self.square_size < position[1] < 18 * self.square_size and self.shooting_phase:
                    row = math.floor(position[1]/40)-8
                    column = math.floor(position[0]/40)-13
                    correct_shot = False
                    if self.computer_board.board[row][column] != self.computer_board.hit_square and self.computer_board.board[row][column] != self.computer_board.missed_square:
                        if self.computer_board.board[row][column] == self.computer_board.ship_square_hidden:
                            self.computer_board.board[row][column] = self.computer_board.hit_square
                            if self.sounds:
                                self.explosion_sound.play()
                        if self.computer_board.board[row][column] == self.computer_board.empty_square:
                            self.computer_board.board[row][column] = self.computer_board.missed_square
                        self.clicks = self.clicks + 1
                        correct_shot = True
                    if self.is_gameover():
                        self.shooting_phase = False
                        self.ending = True
                    if correct_shot:
                        self.computer_shot()
                    if self.is_gameover():
                        self.shooting_phase = False
                        self.ending = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.ESC_KEY = False, False, False, False

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)  # drawing text
        text_rectangle = text_surface.get_rect()  # getting size of the rectangle of the text
        text_rectangle.center = (x, y)  # positioning text in the middle of rectangle
        self.display.blit(text_surface, text_rectangle)  # putting text on display

    # text drawn in placing_phase
    def draw_text_above_shipbox(self):
        if self.placing_phase:
            self.draw_text("Place your " + self.player_board.ships_list[0].name + ", length = " + str(self.player_board.ships_list[0].length),
                           self.font_size_basic, self.DISPLAY_WIDTH / 4, 1 * self.square_size)
    # text draw based on current phase
    def draw_text_next_to_shipbox(self):
        if self.placing_phase:
            self.draw_text("Place your ships in friendly waters.", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           3 * self.square_size)
            self.draw_text("To rotate a ship, first click rotation", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           5 * self.square_size)
            self.draw_text("icon and then place your ship.", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           6 * self.square_size)
        if self.shooting_phase:
            self.draw_text("Destroy enemy ships!", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           3 * self.square_size)
            self.draw_text("Click on the enemy waters", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           5 * self.square_size)
            self.draw_text("to bombard chosen square.", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           6 * self.square_size)
        if self.ending:
            if self.winner == "Computer":
                self.draw_text("You lost the battle!", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           3 * self.square_size)
                self.draw_text("Computer won in", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           5 * self.square_size)
                self.draw_text(str(self.clicks) + " moves.", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                           6 * self.square_size)
            else:
                self.draw_text("Congratulations!", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                               3 * self.square_size)
                self.draw_text("You won the battle in", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                               5 * self.square_size)
                self.draw_text(str(self.clicks) + " moves.", self.font_size_basic, self.DISPLAY_WIDTH * 3 / 4,
                               6 * self.square_size)
            # saving result of game to a file
            if not self.result_saved:
                with open(self.results_file, "a") as file:
                    text = self.winner + "\t" + str(self.clicks) + "\t" + str(date.today()) + "\n"
                    file.write(text)
                self.result_saved = True

    # drawing shipbox where ships are being reversed
    def draw_shipbox(self):
        pygame.draw.rect(self.display, self.WHITE,
                         pygame.Rect(self.square_size, 2 * self.square_size, self.player_board.board_size * self.square_size,
                                     5 * self.square_size))  # drawing a shipbox
        self.reverse_icon = pygame.transform.scale(self.reverse_icon, (self.square_size, self.square_size))
        self.display.blit(self.reverse_icon,
                          (10 * self.square_size, 6 * self.square_size))  # adding reverse icon to the ship box
        if self.placing_phase:
            if self.player_board.ships_list[0].horizontal:
                for square in range(self.player_board.ships_list[0].length):
                    pygame.draw.rect(self.display, self.player_board.GREY,
                                     pygame.Rect(3 * self.square_size + square * self.square_size,
                                                 4 * self.square_size, self.square_size,
                                                 self.square_size))
            else:
                for square in range(self.player_board.ships_list[0].length):
                    pygame.draw.rect(self.display, self.player_board.GREY,
                                     pygame.Rect(5.5 * self.square_size,
                                                 2 * self.square_size + square * self.square_size, self.square_size,
                                                 self.square_size))

    # shots aimed by computer onto the player's board
    def computer_shot(self):
        correct_shot = False
        while not correct_shot:
            # generating random coordinates
            row = random.randint(0, 9)
            column = random.randint(0, 9)
            if self.player_board.board[row][column] != self.player_board.hit_square and self.player_board.board[row][column] != self.player_board.missed_square:
                if self.player_board.board[row][column] == self.player_board.ship_square:
                    self.player_board.board[row][column] = self.player_board.hit_square
                    if self.sounds:
                        self.explosion_sound.play()
                    correct_shot = True
                    self.previous_move = True, row, column
                if self.player_board.board[row][column] == self.player_board.empty_square:
                    self.player_board.board[row][column] = self.player_board.missed_square
                    correct_shot = True
                    self.previous_move = False, row, column

    # determines if game should be over based on number of red squares on the boards
    def is_gameover(self):
        red_count_computers_board = 0
        for row in range(self.computer_board.board_size):
            for column in range(self.computer_board.board_size):
                if self.computer_board.board[row][column] == self.computer_board.hit_square:
                    red_count_computers_board = red_count_computers_board + 1
        all_lengths = 0
        for ship in range(len(self.computer_board.ships_list)):
            all_lengths = all_lengths + self.computer_board.ships_list[ship].length
        if red_count_computers_board == all_lengths:
            return True
        red_count_players_board = 0
        for row in range(self.player_board.board_size):
            for column in range(self.player_board.board_size):
                if self.player_board.board[row][column] == self.player_board.hit_square:
                    red_count_players_board = red_count_players_board + 1
        if red_count_players_board == all_lengths:
            self.winner = "Computer"
            return True
        return False
