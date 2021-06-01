from ship import *
import pygame
import math
import random


class Board:
    def __init__(self, game):
        self.game = game
        self.BLACK = (0, 0, 0)
        self.BLUE = (65, 105, 225)  # colour of missed square
        self.RED = (255, 0, 0)  # colour of hit square (previously ship square)
        self.WHITEISH = (255, 254, 220)  # colour of empty square
        self.GREY = (128, 128, 128)  # colour of ship square
        self.board_size = 10
        self.board_square_size = 40
        self.ships_list = []
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # marked colours: whiteish, grey, blue, red (aka hits)
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.empty_square = 0
        self.ship_square = 1
        self.missed_square = 2
        self.hit_square = 3
        self.ship_square_hidden = 4
        self.create_ships_list()

    def create_ships_list(self):
        self.ships_list.append(Ship("Carrier", 5, True))
        self.ships_list.append(Ship("Battleship", 4, True))
        self.ships_list.append(Ship("Cruiser", 3, True))
        self.ships_list.append(Ship("Submarine", 3, True))
        self.ships_list.append(Ship("Destroyer", 2, True))

    # drawing board based on values in board
    def draw_board(self, x, y):
        for row in range(self.board_size):
            for column in range(self.board_size):
                pygame.draw.rect(self.game.display, self.get_colour(row, column),
                                 pygame.Rect(x + row * self.board_square_size, y + column * self.board_square_size,
                                             self.board_square_size, self.board_square_size))
                pygame.draw.line(self.game.display, self.BLACK,
                                 (x + row * self.board_square_size, y + column * self.board_square_size),
                                 (x + (row + 1) * self.board_square_size, y + column * self.board_square_size), 1)
                pygame.draw.line(self.game.display, self.BLACK,
                                 (x + row * self.board_square_size, y + column * self.board_square_size),
                                 (x + row * self.board_square_size, y + (column + 1) * self.board_square_size), 1)

    # getting colour based on value in board
    def get_colour(self, row, column):
        if self.board[column][row] == self.empty_square or self.board[column][row] == self.ship_square_hidden:
            return self.WHITEISH
        if self.board[column][row] == self.ship_square:
            return self.GREY
        if self.board[column][row] == self.missed_square:
            return self.BLUE
        if self.board[column][row] == self.hit_square:
            return self.RED

    # calculating columns and rows in player's boards based on mouse position
    def get_column_on_board(self, x):
        return math.floor(x/40)-1

    def get_row_on_board(self, y):
        return math.floor(y/40)-8

    # checks if ship can be placed in chosen square
    def ship_can_be_placed(self, x, y):
        column = self.get_column_on_board(x)
        row = self.get_row_on_board(y)
        max = self.board_size - self.ships_list[0].length
        if self.ships_list[0].horizontal:
            if column > max:
                return False
            for square in range(self.ships_list[0].length):
                if self.board[row][column + square] == 1:
                    return False
        else:
            if row > max:
                return False
            for square in range(self.ships_list[0].length):
                if self.board[row + square][column] == 1:
                    return False
        return True

    # randomly generating placements of computer's ship
    def generate_computers_board(self):
        for ship in range(len(self.ships_list)):
            placed = False
            while not placed:
                bool = random.randint(1, 2)
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                if bool == 1:
                    self.ships_list[ship].horizontal = True
                    if self.ship_can_be_generated(x, y, self.ships_list[ship]):
                        for square in range(self.ships_list[ship].length):
                            self.board[x][y+square] = self.ship_square_hidden
                        placed = True
                else:
                    self.ships_list[ship].horizontal = False
                    if self.ship_can_be_generated(x, y, self.ships_list[ship]):
                        for square in range(self.ships_list[ship].length):
                            self.board[x+square][y] = self.ship_square_hidden
                        placed = True

    # checks if computer's ship can be generated in a specific place
    def ship_can_be_generated(self, row, column, ship):
        max = self.board_size - ship.length
        if ship.horizontal:
            if column > max:
                return False
            for square in range(ship.length):
                if self.board[row][column + square] == self.ship_square or self.board[row][column + square] == self.ship_square_hidden:
                    return False
        else:
            if row > max:
                return False
            for square in range(ship.length):
                if self.board[row + square][column] == self.ship_square or self.board[row + square][column] == self.ship_square_hidden:
                    return False
        return True
