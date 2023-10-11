from dosaku.modules.dosaku.ponder import Ponder


def test_ponder():
    ponderer = Ponder()

    new_task_reqs = ('Interface to play a game of tic tac toe, including methods new_game, make_human_move, '
                     'make_ai_move and show_board. The new_game method should start a new game and play through it '
                     'with one human and one AI player. The make_human_move method should request a move from a user '
                     'through the python input command. The make_ai_move should select a move to play on the board '
                     '(for whoever\'s turn it is) automatically. The show_board method should display the board to '
                     'standard out. There may be additional helper methods added (for example to keep score of '
                     'multiple games), if desired.')
    ponderer.write_task(task_reqs=new_task_reqs, write_to_file=True, filename='tic_tac_toe.py')

    new_module_reqs = ('Implementation to play a game of tic tac toe. There should be one human player and one AI '
                       'player. The human player should enter their moves, 1-9, as standard keyboard input. Between'
                       'each move the board should print to screen. At the end of the game the result of the game '
                       'should be shown: either Human Wins, AI Wins, or Draw.')
    conversation = ponderer.write_module_from_task(
        task_filename='tic_tac_toe.py', module_reqs=new_module_reqs, write_to_file=True, filename='tic_tac_toe.py')
