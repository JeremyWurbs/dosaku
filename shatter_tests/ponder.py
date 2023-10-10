from dosaku.modules.dosaku.ponder import Ponder


def test_ponder():
    ponderer = Ponder()

    new_task_reqs = ('Interface to play a game of tic tac toe, including methods new_game, make_human_move and '
                     'make_ai_move. The make_human_move method should request a move from a user through the python '
                     'input command. The make_ai_move should select a move to play on the board (for whoever\'s turn '
                     'it is) automatically. There may be additional helper methods added (for example to show_board) '
                     'as desired.')
    ponderer.write_task(task_reqs=new_task_reqs, write_to_file=True)
