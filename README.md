# Dosaku

An open-source, personal AI assistant.

# Installation

Create a virtual environment, and then install all the dependencies.

```commandline
pip install -r requirements.txt
```

# Usage

## Quickstart

The default personal AI assistant agent class is *Agent*.

```python
from dosaku import Agent

agent = Agent()
```

You can see what your agent can do with:

```python
agent.tasks  # []
```

Which will print a notably empty list. Fortunately your agent can learn! Let's learn and try 'Chat':

```python
agent.learn('Chat')
agent.tasks  # ['Chat']
response = agent.Chat.message("Hello, what's your name?")  # "Hi, I'm EchoBot."
```

## Tasks and Actions

Note the way in which we used our agent. Our agent learned the *task* "Chat". This task defines an *action*, "message". 
(As a quick aside: tasks are python classes, and thus get python class naming conventions, i.e. `TheyWillLookLikeThis`.  
Actions are python methods, and thus get python method naming conventions, i.e. `they_will_look_like_this`). In general, 
we get our agent to *do* an action with:

```python
agent_name.TaskName.task_action()
agent_name.TaskName.another_task_action()
```

To find out what *actions* a particular task gives you access to, you can ask your agent for the associated Task API:

```python
agent.api('Chat')  # ['message']
```

Which will list out all the actions associated with that task. For more detailed information on the task, including how
to use each action, you may request any documentation provided by the task creator:

```python
agent.doc('Chat')  # 'Interface for a generic conversational chatbot.'
agent.doc('Chat', action='message')  # "Send a message to the agent and get a response. Args: ... Example: ..."
```

Which is roughly equivalent to the following:

```python
from dosaku.tasks import Chat
Chat.__doc__  # 'Interface for a generic conversational chatbot.'
Chat.message.__doc__  # "Send a message to the agent and get a response. Args: ... Example: ..."
```

## Learning New Tasks

The base Agent will not know any tasks by default. To see what your agent can learn, you may ask it:

```python
agent.learnable_tasks  # ['Chat', 'GradioChat', ...]
```

Which will print out a notably longer list. [Gradio](https://www.gradio.app/) is a library for quickly building machine
learning applications. It provides a ChatInterface which we wrap in Dosaku as its own "GradioChat" task. We can examine 
this task with:

```python
agent.api('GradioChat')  # ['chat', 'predict', ...]
```

The GradioChat task has the same *message* action from before, but now there is an additional *predict* action. You can 
see how to use this action with:

```python
agent.doc('GradioChat', 'predict')
```

The *predict* action is similar to *chat*, but accepts an additional chat *history* argument. There are a few other 
actions defined by the GradioChat task as well. In any case, the GradioChat task defines the task used in the standard
Dosaku chat agent application, and as such it defines the interface that all named Dosaku agents must support (more on 
named Agents later).

## [Old]

```python
dosk.learnable_tasks  # ['SongSerializer', ...]
```

Which will print a notably longer list of tasks that your agent can learn. To learn one of the tasks:

```python
dosk.learn('SongSerializer')
dosk.tasks  # [..., 'SongSerializer']
```

Which will now print `SongSerializer`. The `SongSerializer` task is defined in 
[dosaku.tasks.song_serializer.py](dosaku/tasks/song_serializer.py). This class defines one or more abstract methods 
which must be implemented by any class claiming to be a "SongSerializer" (in this case, it defines a single abstract 
method, *serialize*). As we were able to learn this task, we must have something able to do *serialize*. You may test 
this hypothesis with the following:

```python
from dosaku import Dosaku
from dosaku.tasks.song_serializer import Song

song = Song(song_id='1', title='Billie Jean', artist='Michael Jackson')
dosk = Dosaku()

dosk.SongSerializer.serialize(song)  # AttributeError: 'Agent' object has no attribute 'SongSerializer'
dosk.learn('SongSerializer')
dosk.SongSerializer.serialize(song)  # '{"id": "1", "title": "Billie Jean", "artist": "Michael Jackson"}'
```

## Tasks and Modules

Dosaku is meant to bridge the world of humans and AI. As such, there are two fundamental *spaces* which define the key 
concepts to the Dosaku platform: *tasks* and *modules*.

Tasks live in the human space. They are the things we want our AI assistant to be able to do: "*play chess*", "*extract 
the text from a pdf document*", "*text-to-image*" (i.e. create an image given a text prompt). Each of these *tasks* 
takes a human concept and defines an explicit API. Some tasks, like "Chat", define only a single associated action,
while other tasks, like "PlayGo", define a rather involved API compatible with the 
[go text protocol](https://en.wikipedia.org/wiki/Go_Text_Protocol), including dozens of individual actions and 
maintaining state between actions.

In either case, the task translates a human concept into an explicit machine API interface. Tasks do *not* implement the 
actual code necessary to *do* the task and its actions. In the above example, however, when we learned Chat we 
actually *did* the action "chat". As programmers may have guessed, tasks are abstract interface classes and, at least in 
python, cannot even be instantiated. What, then, is actually *doing* the task? What is it that our agent is learning 
when it "learns"?

The answer is a Module.

Modules live in the machine space. They are programs that do *something*. Modules can be anything, really. To be used by
Dosaku, however, they must register (i.e. claim that they can do) at least one Task. When we ask Dosaku to 
*learn* something, what we are doing is asking Dosaku to *load* (download, install, load into memory, etc.) a Module 
program able to do the *Task*. Later, when Dosaku does the *Task*, what it is actually doing is running the *Module* 
program. 

Following the above Chat example, you can see what Module was loaded with:

```python
agent.loaded_modules  # ['EchoBot']
```

EchoBot is a class defined in [echo_bot.py](dosaku/modules/samples/chat/echo_bot.py) that has registered itself as 
handling the *Chat* task. That is, the EchoBot class implements the actual code necessary to do all the actions (i.e.
abstract methods). 

But EchoBot is not a particularly impressive module. Fortunately, it is not the only module available for Chat. You may
list all the modules that have registered themselves as implementing a given task with:

```python
agent.registered_modules('Chat')  # ['EchoBot', 'RedPajama', ...]
```

**A warning before continuing**: from here on out the modules we will be loading will download large AI models (~5-10GB 
each) and attempt to run them on (a cuda-enabled GPU) on your machine. The process will be automatic, and all the 
models here will be well-known models (RedPajama, Stable Diffusion) from well-known providers 
([Together AI](https://together.ai/), Stability AI) from a well-known model hub (Huggingface). These models are 
well-tested and trustworthy, but if you have not used Huggingface before, or don't have a lot of disk space, or don't 
have a cuda-enabled GPU able to run these models, it may be best to finish reading the following documentation before
attempting to do it yourself.

To learn (load, run) a different Module, we can pass it in explicitly when we learn the task:

```python
dosk.learn('Chat', module='RedPajama')
```

## Services

Services are modules that are run through the interwebs. OpenAI's ChatGPT is a service, as is Stability AI's Clipdrop
(image generation) API. 

To use services, you must provide the appropriate API keys in your [config.ini](dosaku/config/_config.ini) file. To 
use Stable Diffusion through Clipdrop, for example, first go to [https://clipdrop.co/apis](https://clipdrop.co/apis),
sign up and obtain an API key. Place this key in your config file under the CLIPDROP API key. You can access this API 
key programmatically with the following:

```python
from dosaku import Config

config = Config()
config['API_KEYS']['CLIPDROP']  # Should show your API key
```

Once your API key is set up, you may use a service in the same way you'd use a module:

```python
from dosaku import Agent

agent = Agent()
agent.learn('TextToImage', module='ClipdropTextToImage')  # RuntimeError
```

Which will *not* work by default, instead throwing an important error: 

```text 
Loaded module was a service, but services have not been enabled. Enable services or load a non-service module.
```

This error message is very important. When you use services, you are implicitly agreeing to:

    1. Send your data over the interwebs;
    2. You are probably spending money;

Because of these facts, services and modules are kept distinct within Dosaku.

Comparing Modules and Services:

|                                                       | Modules | Services  |
|------------------------------------------------------:|:-------:|:---------:|
|                  May download data from the interwebs |    x    |     x     |
| May run code from the interwebs on your local machine |    x    |     x     |
|                        May send data to the interwebs |         |     x     |
|                                        May cost money |         |     x     |
|                                  Computation location |  Local  | Interwebs |

In general, only use modules you trust, as they are likely downloading data (AI models with associated weights) to your
machine, where they will subsequently be run. And, definitely, only use services you trust *and* understand how much 
money using them costs. There are no limits within Dosaku itself— so before you request a million images from the 
Clipdrop service, it would be a good idea to [look at their pricing](https://clipdrop.co/apis/pricing). Currently, processing a
single text-to-image request is approximately 10 cents (USD 0.10) after any initial free credits. 

In other words, if you haven't signed up to a third party service, given them your credit card number, and copied the
associated API key into your Dosaku config file, nothing will cost money and, hopefully, the worst that can happen is 
you download a model too big for your machine and you crash it. If you have done those things, because you 
want to use e.g. ChatGPT, then you are completely responsible for how much money Dosaku spends using those services. 

With that, in order to continue, you may enable services, and then learn and use text-to-image with:

```python
agent.enable_services()
agent.learn('TextToImage', module='ClipdropTextToImage')
image = agent.TextToImage.text_to_image('Dosaku playing a game of go')
image.show()
```

Which should show a lovely image of our namesake Dosaku, as generated by Stability AI's Stable Diffusion API.

![Dosaku playing go](resources/dosaku.png)


## Working with Dosaku

Adding knowledge and abilities to Dosaku revolves around creating new modules it can learn. For more details on how to 
write new tasks and modules, refer to the [developer readme](/dosaku/README.md). One powerful service Dosaku comes 
with, however, is called **Ponder**. Ponder (attempts to) automatically create new modules for you. Ponder uses OpenAI's 
GPT-3.5/GPT-4, and so requires an OpenAI API key. Once you have put an API key into your config file, you may try the 
following:

```python
from dosaku import Agent

agent = Agent(enable_services=True)
agent.learn('Ponder', model='gpt-4')

new_task_description = (
    'Implement a game of tic tac toe between a human and AI. At minimum, include methods new_game, make_human_move, '
    'make_ai_move, show_board and play. The play method should put all the other methods together into a complete game. '
    'You should display the board between moves, and ask the user for their move on their turn. After the game display '
    'the result as well.'
)

agent.Ponder(reqs=new_task_description, write_to_file=True, save_filename='tic_tac_toe.py')
```

The above will create a new TicTacToe task and module. Specifically, it will generate five new files, each filling their
associated 'pondered' directory:

    1. dosaku.tasks.pondered.tic_tac_toe.py: Detailing a new TicTacToe task.
    2. dosaku.modules.pondered.tic_tac_toe.py: The actual implementation for a TicTacToe module.
    3. dosaku.samples.pondered.tic_tac_toe.py: A standalone sample on how to use the module.
    4. dosaku.app.pondered.tic_tac_toe.py: An end-to-end gradio app incorporating the module.
    5. tests.pondered.test_tic_tac_toe.py: A unit test suite for the new module.

For example, here are the task and module files for a GPT-4 using the exact task description above:

```python
from abc import abstractmethod
from dosaku import Task


class TicTacToe(Task):
    """Interface for a game of tic-tac-toe between a human and an AI."""
    name = 'TicTacToe'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def new_game(self) -> None:
        """Starts a new game of tic-tac-toe.

        Resets the state of the board and determines who goes first.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def make_human_move(self, row: int, col: int) -> None:
        """Makes a move on behalf of the human player.

        Args:
            row: The row of the board where the human wants to place their piece.
            col: The column of the board where the human wants to place their piece.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def make_ai_move(self) -> None:
        """Makes a move on behalf of the AI player.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def show_board(self) -> None:
        """Displays the current state of the board.

        Returns:
            None
        """
        raise NotImplementedError
  
    @abstractmethod
    def play(self) -> None:
        """Plays a game of tic-tac-toe from start to finish.

        This method will call the following methods in order:
            new_game
            show_board
            make_human_move (or make_ai_move, depending on who goes first)
            show_board
            make_human_move (or make_ai_move, depending on who goes second)
            show_board
            ... (continue alternating moves)
            show_board (after the game has ended)

        Returns:
            None
        """
        raise NotImplementedError


TicTacToe.register_task()
```

```python
from dosaku import Module


class TicTacToeAI(Module):
    name = 'TicTacToeAI'

    def __init__(self):
        super().__init__()
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.players = ['X', 'O']
        self.current_player = 0

    def new_game(self) -> None:
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 0

    def make_human_move(self, row: int, col: int) -> None:
        self.board[row][col] = self.players[0]

    def make_ai_move(self) -> None:
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    self.board[i][j] = self.players[1]
                    return

    def show_board(self) -> None:
        for row in self.board:
            print(' | '.join(row))
            print('-' * 9)

    def play(self) -> None:
        self.new_game()
        self.show_board()
        for _ in range(9):
            if self.current_player == 0:
                row = int(input('Enter the row for your move: '))
                col = int(input('Enter the column for your move: '))
                self.make_human_move(row, col)
            else:
                self.make_ai_move()
            self.show_board()
            self.current_player = 1 - self.current_player


TicTacToeAI.register_task(task='TicTacToe')
```

The app given to run the above model:
```python
from dosaku import Agent


def tic_tac_toe_sample():
    agent = Agent()
    agent.learn('TicTacToe', module='TicTacToeAI')

    while True:
        agent.TicTacToe.play()

        play_again = input('Do you want to play again? (yes/no): ')
        if play_again.lower() != 'yes':
            break
            
            
if __name__ == "__main__":
    tic_tac_toe_sample()
```

Which runs and works. In this case Dosaku has forgotten to implement a method to check who won, which usually is 
included in the implementation. In any case, results are still a work in progress. 
