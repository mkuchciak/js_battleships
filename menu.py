import pygame
from operator import itemgetter


class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_width = self.game.DISPLAY_WIDTH / 2
        self.mid_height = self.game.DISPLAY_HEIGHT / 2
        self.run_display = True
        self.cursor_rectangle = pygame.Rect(0, 0, 80, 80)
        self.offset = - 100

    def draw_cursor(self):
        self.game.draw_text('*', 15, self.cursor_rectangle.x, self.cursor_rectangle.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)  # access to variables from Menu
        self.state = "Start"
        self.startx, self.starty = self.mid_width, self.mid_height + 30
        self.optionsx, self.optionsy = self.mid_width, self.mid_height + 90
        self.leaderboardx, self.leaderboardy = self.mid_width, self.mid_height + 150
        self.creditsx, self.creditsy = self.mid_width, self.mid_height + 210
        self.cursor_rectangle.midtop = (self.startx + self.offset, self.starty)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            pygame.display.set_caption("Battleships")
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text("BATTLESHIPS", self.game.font_size_title, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 4 - 20)
            self.game.draw_text("Play", self.game.font_size_title, self.startx, self.starty)
            self.game.draw_text("Options", self.game.font_size_title, self.optionsx, self.optionsy)
            self.game.draw_text("Leaderboard", self.game.font_size_title, self.leaderboardx, self.leaderboardy)
            self.game.draw_text("Credits", self.game.font_size_title, self.creditsx, self.creditsy)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Start":
                self.cursor_rectangle.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = "Options"
            elif self.state == "Options":
                self.cursor_rectangle.midtop = (self.leaderboardx + self.offset, self.leaderboardy)
                self.state = "Leaderboard"
            elif self.state == "Leaderboard":
                self.cursor_rectangle.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = "Credits"
            elif self.state == "Credits":
                self.cursor_rectangle.midtop = (self.startx + self.offset, self.starty)
                self.state = "Start"
        elif self.game.UP_KEY:
            if self.state == "Start":
                self.cursor_rectangle.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = "Credits"
            elif self.state == "Options":
                self.cursor_rectangle.midtop = (self.startx + self.offset, self.starty)
                self.state = "Start"
            elif self.state == "Leaderboard":
                self.cursor_rectangle.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = "Options"
            elif self.state == "Credits":
                self.cursor_rectangle.midtop = (self.leaderboardx + self.offset, self.leaderboardy)
                self.state = "Leaderboard"

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == "Start":
                self.game.playing = True
            elif self.state == "Options":
                self.game.current_menu = self.game.options
            elif self.state == "Leaderboard":
                self.game.current_menu = self.game.leaderboard
            elif self.state == "Credits":
                self.game.current_menu = self.game.credits
            self.run_display = False


class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "ON"
        self.volumex, self.volumey = self.mid_width, self.mid_height + 30
        self.onx, self.ony = self.mid_width, self.mid_height + 80
        self.offx, self.offy = self.mid_width, self.mid_height + 130
        self.cursor_rectangle.midtop = (self.onx + self.offset, self.ony)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill((0, 0, 0))
            self.game.draw_text("Options", self.game.font_size_title, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 4 - 20)
            self.game.draw_text("Volume", self.game.font_size_title, self.volumex, self.volumey)
            self.game.draw_text("ON", self.game.font_size_basic, self.onx, self.ony)
            self.game.draw_text("OFF", self.game.font_size_basic, self.offx, self.offy)

            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            self.game.current_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state == "ON":
                self.state = "OFF"
                self.cursor_rectangle.midtop = (self.offx + self.offset, self.offy)
            elif self.state == "OFF":
                self.state = "ON"
                self.cursor_rectangle.midtop = (self.onx + self.offset, self.ony)
        elif self.game.START_KEY:
            if self.state == "ON":
                self.game.sounds = True
            elif self.state == "OFF":
                self.game.sounds = False


class LeaderboardMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.data = []
        self.results_file = "results.txt"
        self.open_file()

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.ESC_KEY:
                self.game.current_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLACK)
            self.sort_best_scores()
            self.blit_screen()

    def open_file(self):
        with open(self.results_file, "r", encoding="utf-8") as file:
            for line in file:
                elements = line.split("\t")
                winner = elements[0]
                moves = elements[1]
                date = elements[2]
                self.data.append((winner, moves, date))

    # sorting and drawing 10 best scores from the file
    def sort_best_scores(self):
        self.data.sort(key=itemgetter(1), reverse=False)
        self.game.draw_text("Leaderboard", self.game.font_size_title, self.game.DISPLAY_WIDTH / 2,
                            self.game.DISPLAY_HEIGHT / 4 - 100)
        for i in range(10):
            self.game.draw_text(str(i+1) + ". " + str(self.data[i][0]) + "    " + str(self.data[i][1]) + "    " + str(self.data[i][2])[0:10], self.game.font_size_basic, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 4 - 20 + 50 * i)


class CreditsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.ESC_KEY:
                self.game.current_menu = self.game.main_menu
                self.run_display = False
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text("Credits", self.game.font_size_title, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 4 - 20)
            self.game.draw_text("Made by Marta Kuchciak", self.game.font_size_basic, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2 + 30)
            self.game.draw_text("JS PWR 2021", self.game.font_size_basic, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2 + 80)
            self.blit_screen()
