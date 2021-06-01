from game import Game

game = Game()

while game.running:
    game.current_menu.display_menu()
    game.game_loop()
