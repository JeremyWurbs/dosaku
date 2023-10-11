import random

from dosaku import Module


class TicTacToeModule(Module):
    name = 'TicTacToeModule'
    board = [' ' for _ in range(9)]

    def __init__(self):
        super().__init__()

    def new_game(self):
        self.board = [' ' for _ in range(9)]

    def make_human_move(self):
        move = input("Enter your move (1-9): ")
        if self.board[int(move)-1] == ' ':
            self.board[int(move)-1] = 'X'
        else:
            print("Invalid move!")

    def make_ai_move(self):
        while True:
            move = random.randint(1,9)
            if self.board[move-1] == ' ':
                self.board[move-1] = 'O'
                break

    def show_board(self):
        print('---------')
        for i in range(0,9,3):
            print('|', ' '.join(self.board[i:i+3]), '|')
        print('---------')
    
    def check_winner(self):
        winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for combination in winning_combinations:
            if self.board[combination[0]] == self.board[combination[1]] == self.board[combination[2]] != ' ':
                return self.board[combination[0]]
        if ' ' not in self.board:
            return 'Draw'
        return None

    def play_game(self):
        self.new_game()
        while True:
            self.show_board()
            self.make_human_move()
            winner = self.check_winner()
            if winner:
                print('Human Wins' if winner == 'X' else ('AI Wins' if winner == 'O' else 'Draw'))
                break
            self.make_ai_move()
            winner = self.check_winner()
            if winner:
                print('Human Wins' if winner == 'X' else ('AI Wins' if winner == 'O' else 'Draw'))
                break


TicTacToeModule.register_task(task='TicTacToe')
