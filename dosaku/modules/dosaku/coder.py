from __future__ import annotations
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from dosaku import CodingError, Config, Executor, Service, ShortTermModule
from dosaku.logic import Context
from dosaku.modules import OpenAIChat
from dosaku.tasks import Chat
from dosaku.utils import ifnone, clean_code
if TYPE_CHECKING:
    from dosaku import Agent


class Coder(Executor, Service):
    """Iteratively tests and writes code.

    As Coder is both an Executor and a Service, it is highly recommended to use Coder through an Agent to make sure
    the proper permissions are given.
    """
    name = 'Coder'
    config = Config()
    default_system_prompt = (
        'You are an expert python developer, tasked with writing code to match a given description. Your code should '
        'be able to run directly in a python interpreter. That is, DO comment all of your code, but DO NOT add any '
        'explanatory text or markdown code, such as ```python. Any explanatory code MUST be written as python '
        'comments.\n'
        '\n'
        'After you write code it will be run. If there are errors you will be given the errors. You should respond by '
        'rewriting ALL of the code with the errors corrected.\n'
    )
    determine_actions_prompt = (
        'You are an expert python developer, tasked with determining the user API for a given piece of code. You '
        'will be given a user conversation with an accompanying piece of code. You should respond with a python '
        'List[str] containing the names of the main API methods. The methods you return must exist in the given code.'
        'It is possible that extra methods are present which are only used as helper methods, in which case you should '
        'not return them as part of the API. For example: \n'
        '\n'
        'User: Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
        'integer and returns whether it is prime; (2) accepts an integer and returns its collatz 3n+1 path; (3) '
        'accepts two integers and an optional length parameter defaulting to 20 and returns the fibinacci sequence (of '
        'the optional parameter length) starting with the two integers.\n'
        '\n'
        'Assistant: ```python\n'
        'def is_prime(n):\n'
        '    if n <= 1:\n'
        '        return False\n'
        '    if n == 2:\n'
        '        return True\n'
        '    if n % 2 == 0:\n'
        '        return False\n'
        '    i = 3\n'
        '    while i * i <= n:\n'
        '        if n % i == 0:\n'
        '            return False\n'
        '        i += 2\n'
        '    return True\n'
        '\n'
        'def collatz(n):\n'
        '    sequence = [n]\n'
        '    while n != 1:\n'
        '        if n % 2 == 0:\n'
        '            n = n // 2\n'
        '        else:\n'
        '            n = 3 * n + 1\n'
        '        sequence.append(n)\n'
        '    return sequence\n'
        '\n'
        'def fibonacci(n1, n2, length=20):\n'
        '    sequence = [n1, n2]\n'
        '    while len(sequence) < length:\n'
        '        sequence.append(sequence[-1] + sequence[-2])\n'
        '    return sequence\n'
        '```\n'
        'User: Return the API for the previous conversation:\n'
        '\n'
        'You should respond:\n'
        '\n'
        '[\'is_prime\', \'collatz\', \'fibonacci\']'
    )
    determine_name_prompt = (
        'You are an expert python developer, tasked with writing class names for a given API. The API will contain a '
        'set of Python methods implementing a request from a user. You should respond with the Python class name that '
        'should contain the given methods. For example:\n'
        '\n'
        'User: Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
        'integer and returns its collatz 3n+1 path; (2) accepts two integers and an optional length parameter '
        'defaulting to 20 and returns the fibinacci sequence (of the optional parameter length) starting with the two '
        'integers.\n'
        '\n'
        'Assistant: ```python\n'
        'def collatz(n):\n'
        '    sequence = [n]\n'
        '    while n != 1:\n'
        '        if n % 2 == 0:\n'
        '            n = n // 2\n'
        '        else:\n'
        '            n = 3 * n + 1\n'
        '        sequence.append(n)\n'
        '    return sequence\n'
        '\n'
        'def fibonacci(n1, n2, length=20):\n'
        '    sequence = [n1, n2]\n'
        '    while len(sequence) < length:\n'
        '        sequence.append(sequence[-1] + sequence[-2])\n'
        '    return sequence\n'
        '```\n'
        'User: Return the API for the previous conversation:\n'
        '\n'
        'Assistant: [\'collatz\', \'fibonacci\']\n'
        '\n'
        'User: Write the API class name for the previous conversation:\n'
        '\n'
        'You should respond:\n'
        ''
        'MathSequences'
    )
    write_agent_code_prompt = (
        'You are an expert python developer agent, tasked with writing code for a library called Dosaku. You will be '
        'given a description of a task to complete, and will have to write Python code to execute that task. The code '
        'should be directly executable in a python shell, so do not give any extra commentary unless it is Python '
        'comments. Be sure to surround Python code with ```python and ``` delimiters before and after code, '
        'respectively.\n'
        '\n'
        'You will also be given documentation of functions from the Dosaku library that you may use. The Dosaku '
        'library has three main components: (1) a main agent (i.e. you), (2) tasks, and (3) actions. As you are the '
        'main agent, you will use self when referencing the agent. The tasks are Python classes (i.e. they get Python '
        'class naming conventions and WillLookLikeThis). You can access each task as attributes of self. Each task '
        'contains one or more actions, which are accessible as standard python methods (i.e. they use Python method '
        'naming conventions and will_look_like_this).\n'
        '\n'
        'The following methods are always available to you, as they are directly accessed by the agent (you):\n'
        '\n'
        '@property\n'
        'def learnable_tasks(self):\n'
        '   """Returns a list of all learnable tasks."""\n'
        '\n'
        '@property\n'
        'def tasks(self):\n'
        '    """Returns a list of all known tasks, both learned and memorized."""\n'
        '\n'
        'def api(self, task: str):\n'
        '   """Returns the actions for the given task."""\n'
        '\n'
        'def doc(self, task: str, action: Optional[str] = None):\n'
        '   """Returns documentation on the given task and action."""\n'
        '\n'
        'def learn(self, task: str, module: Optional[str] = None):\n'
        '   """Learn a task via a pre-existing module."""\n'
        '\n'
        'def memorize(self, stm: ShortTermModule, actions: Optional[Union[List[str]] = None):\n'
        '   """Equivalent to learn, but for dynamically generated code made available through a ShortTermModule."""\n'
        '\n'
        'The following methods are available to you through a Task called Coder:\n'
        '\n'
        'class Coder(Task):\n'
        '   def write_code(\n'
        '       self,\n'
        '       description: str,\n'
        '       max_tries: Optional[int] = None,\n'
        '       return_intermediate_tries: bool = False\n'
        '   ) -> Union[str, List[str]]:\n'
        '       """Writes code based on the given description."""\n'
        '   def create_stm(\n'
        '       self,\n'
        '       code: str,\n'
        '       name: Optional[str] = None,\n'
        '       actions: Optional[List[str]] = None\n'
        '   ) -> ShortTermModule:\n'
        '       """Create a ShortTermModule based on the given code."""\n'
        '   def stm_from_chat(self, conversation: Chat) -> ShortTermModule:\n'
        '       """Generate stm from the last Assistant message."""\n'
        '\n'
        'You will be given a number of attempts to complete the task. You may write code to find out more '
        'documentation, which you may use on a subsequent attempt. For each attempt, you will write Python code which '
        'will be run; you will receive the output of that code for your next attempt. If your code returns an error, '
        'you will be given the error message. You must complete the task by the last attempt.\n'
        '\n'
        'For example, given the following instruction from the user:\n'
        '\n'
        'User: Create code that takes a prompt and generates a 1500 word story from the prompt. Then create three '
        'images to illustrate the story. You have 20 attempts remaining.\n'
        '\n'
        'You may first note that the methods listed before do not allow you to write a story or create an image. Your '
        'first two or three attempts should then be looking up appropriate documentation:\n'
        '\n'
        'Assistant: ```python\n'
        'print(self.learnable_tasks)\n'
        '```\n'
        '\n'
        'The user will respond with the output of your code:\n'
        '\n'
        'User: Your code output the following (19 attempts remaining):\n'
        '[\'TextToImage\', \'SpeechToText\', \'RealtimeSpeechToText\', \'Chat\', \'ObjectDetection\']\n'
        '\n'
        'You should recognize that it is likely you can use Chat to create a story, and TextToImage to create '
        'illustrations. You should ask for documentation for these functions next:\n'
        '\n'
        'Assistant: ```python\n'
        'for task in [\'Chat\', \'TextToImage\']:\n'
        '   print(f\'{task}: {agent.api(task)}\')\n'
        '```\n'
        '\n'
        'User: Your code output the following (18 attempts remaining):\n'
        'Chat: [\'reset_chat\', \'__init__\', \'__str__\', \'history\', \'message\', \'__call__\', \'add_message\']\n'
        'TextToImage: [\'__call__\', \'text_to_image\']\n'
        '\n'
        'You should easily see that Chat.message, Chat.add_message and TextToImage.text_to_image are likely to be '
        'useful methods. You should spend one more attempt getting their explicit documentation:\n'
        '\n'
        'Assistant: ```python\n'
        'print(f\"Chat.message: {self.doc(\'Chat\', action=\'message\')}\")\n'
        'print(f\"Chat.add_message: {self.doc(\'Chat\', action=\'add_message\')}\")\n'
        'print(f\"TextToImage.text_to_image: {self.doc(\'TextToImage\', action=\'text_to_image\')}\")\n'
        '```\n'
        '\n'
        'User: Your code output the following (17 attempts remaining):\n'
        '# A lot of method documentation will appear here.\n'
        '\n'
        'From the documentation you should see that Chat.add_message does not generate a new response, but '
        'Chat.message does. Therefore we should try to use Chat.message to generate the story, and '
        'TextToImage.text_to_image to generate illustrations. In general, use standalone Chat modules, while using '
        'the agent (self) to learn all other modules. For modules that do not previously exist, you will have to '
        'write new code and learn them as a ShortTermModule.\n'
        '\n'
        'Assistant: ```python\n'
        'from dataclasses import dataclass, field\n'
        'from PIL.Image import Image\n'
        'from typing import List\n'
        '\n'
        'from dosaku.modules import OpenAIChat'
        '\n'
        'chat = OpenAIChat(stream=False)  # When using Chat, use it as a standalone module\n'
        'self.learn(\'TextToImage\')  # For all other modules, learn them directly onto self (equivalent to agent)\n'
        '\n'
        '@dataclass\n'
        'class Book:\n'
        '   chapters: List[str] = field(default_factory=list)\n'
        '   illustrations: List[Image] = field(default_factory=list)\n'
        '   @property\n'
        '   def chapter_lengths(self):\n'
        '       return [len(chapter) for chapter in self.chapters]\n'
        '\n'
        'def gen_story(prompt: str, length: int = 1500, num_chapters: int = 3, num_revisions: int = 3) -> Book:\n'
        '   """Creates a story following the given prompt"""\n'
        '   prompt = f\'Create a {length} word story about the following prompt. Be as detailed and specific as '
        'possible. Break the story into {num_chapters} distinct chapters. Write the words \"Chapter 1: [Title]\", etc. '
        'at the start of each chapter. The prompt is: {prompt}\'\n'
        '   draft = chat.message(prompt)\n'
        '   cur_draft = 0\n'
        '   while cur_draft < num_revisions:\n'
        '       if len(draft) < int(0.9 * length):\n'
        '           prompt = \'Rewrite the story you just wrote to be more detailed. You wrote {len(draft)} words, but '
        'the target length is {length} words.\'\n'
        '       elif len(draft) > int(1.5 * length):\n'
        '           prompt = \'Rewrite the story you just wrote to be more concise. You wrote {len(draft)} words, but '
        'the target length is {length} words.\'\n'
        '       elif len(draft.split(\'Chapter\')) < num_chapters + 1:\n'
        '           prompt = \'Add chapter titles into the story you just wrote. There should be at least '
        '{num_chapters} chapters. The titles should be of the form Chapter 1: [Chapter Title].\'\n'
        '       else:\n'
        '           break\n'
        '       draft = chat.message(prompt)\n'
        '       cur_draft += 1\n'
        '   chapters = draft.split(\'Chapter\')\n'
        '   if len(chapters) <= num_chapters + 1:\n'
        '       chapter_length = int(len(chapters) / num_chapters)\n'
        '       chapters = [draft[i:i+chapter_length] for i in range(0, len(draft), chapter_length)]\n'
        '   return Book(chapters=chapters)\n'
        '\n'
        'def illustrate_book(book: Book) -> Book:\n'
        '   for chapter in book.chapters:\n'
        '       image = self.TextToImage.text_to_image(prompt=chapter)\n'
        '       book.illustrations.append(image)\n'
        '   return book\n'
        '\n'
        'def create_illustrated_book('
        '   prompt: str, \n'
        '   length: int = 1500, \n'
        '   num_chapters: int = 3, \n'
        '   num_revisions: int = 3\n'
        ') -> Book:\n'
        '   book = gen_story(prompt=prompt, length=length, num_chapters=num_chapters, num_revisions=num_revisions)\n'
        '   book = illustrate_book(book)\n'
        '   return book\n'
        '\n'
        '# Run the code to test it\n'
        'book = create_illustrated_book()\n'
        'print(f\'Chapter Lengths: {book.chapter_lengths}\')\n'
        '```\n'
        '\n'
        'Once you successfully write the task into code without errors, use it to generate a ShortTermModule (STM) and '
        'then memorize the STM:\n'
        '\n'
        'Assistant: ```python\n'
        'stm = self.Coder.stm_from_chat(self.OpenAIChat)\n'
        'self.memorize(stm, actions = [\'create_illustrated_book\'])'
        '```'
    )

    def __init__(self, model: str = None):
        super().__init__()
        self.model = ifnone(model, default=self.config['OPENAI']['DEFAULT_MODEL'])

    def write_code(
            self,
            description: str,
            max_tries: Optional[int] = None,
            system_prompt: Optional[str] = None,
            return_intermediate_tries: bool = False
    ) -> Union[str, List[str]]:
        """Writes code based on the given description.

        Unless specified explicitly in the given description, the code will be stand-alone Python code. It will not
        know of Dosaku or use any of its modules or library.

        Args:
            description: A description of the code to write.
            max_tries: The maximum number of tries before returning. If not given, defaults to the value in config.ini.
            system_prompt: The system prompt given to the chat module. Defaults to the default_system_prompt.
            return_intermediate_tries: Whether to return the intermediate tries.

        Returns:
            The generated code. If return_intermediate_tries is False (the default), the code will be returned as a
            string. If return_intermediate_tries is True, the code will be returned as a list of str, where code[0] was
            the first try and code[-1] the last. In this case, the "final" code should be taken as this last value,
            code[-1].

        Example::

            from dosaku import Agent

            agent = Agent(enable_services=True, enable_executors=True)
            agent.learn('Coder')
            code = agent.Coder('Write a method that takes two integers and returns their greatest common denominator.")
        """
        max_tries = ifnone(max_tries, default=self.config['DOSAKU'].getint('CODER_MAX_TRIES'))
        system_prompt = ifnone(system_prompt, default=self.default_system_prompt)

        conversation = OpenAIChat(system_prompt=system_prompt, model=self.model)
        code = conversation.message(f'Write python code to match the following requirements: {description}')
        code = clean_code(code)
        intermediate_tries = [code]

        num_tries = 0
        while num_tries < max_tries:
            result, err = self.exec(code, globals=globals())
            if err != '':
                code = conversation.message(f'Your code received the following error: {err}\n\nRewrite your code.')
                #code = clean_code(code)
                num_tries += 1
                if return_intermediate_tries:
                    intermediate_tries.append(code)
            else:
                break

        if return_intermediate_tries:
            return intermediate_tries
        else:
            return code

    def create_stm(
            self,
            code: Union[str, OpenAIChat],
            name: Optional[str] = None,
            actions: Optional[Union[str, List[str]]] = None
    ) -> ShortTermModule:
        """Create a ShortTermModule based on the given code.

        If the name or actions are not given, they will be inferred from the code itself.

        Args:
            code: The code to turn into a ShortTermModule.
            name: The name of returned module.
            actions: The list of module actions.

        Returns:
            A ShortTermModule that wraps the given code.

        Example::

            from dosaku.agents import Dosaku

            agent = Dosaku(enable_services=True, enable_executors=True, stream_chat=False)
            agent.learn('Coder')

            desc = (
                'Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
                'integer and returns whether it is prime; (2) accepts an integer and returns its collatz 3n+1 path; '
                '(3) accepts two integers and an optional length parameter defaulting to 20 and returns the fibinacci '
                'sequence (of the optional parameter length) starting with the two integers.')
            code = agent.Coder.write_code(desc)
            stm = agent.Coder.create_stm(code)
            agent.memorize(stm)

            stm.name  # 'NumberSequences'
            agent.api(stm.name)  # ['is_prime', 'collatz', 'fibonacci']

            agent.NumberSequences.is_prime(101)  # True
            agent.NumberSequences.collatz(17)  # [17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
            agent.NumberSequences.fibonacci(2, 3, length=10)  # [2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

        """
        code = str(code)
        actions_conversation = None
        if actions is None:
            actions_conversation = OpenAIChat(
                system_prompt=self.determine_actions_prompt,
                model=self.model,
                stream=False,
                temperature=0.1)
            actions = actions_conversation.message(code + '\n\nUser: Return the API for the previous conversation:\n\n')
            actions = eval(actions)
            if not isinstance(actions, List):
                raise RuntimeError(f'Generated actions were not a list, but a list was needed.')
        if name is None:
            if actions_conversation is None:
                actions_conversation = code + f'\n\nThe selected actions are {actions}.'
            conversation = OpenAIChat(
                system_prompt=self.determine_name_prompt,
                model=self.model,
                stream=False,
                temperature=0.1)
            name = conversation.message(
                str(actions_conversation) + '\n\nUser: Write the API class name for the previous conversation:\n\n')

        return ShortTermModule(name=name, code=clean_code(code), actions=actions)

    def write_agent_code(
            self,
            description: str,
            max_tries: Optional[int] = None,
            system_prompt: Optional[str] = None,
            return_intermediate_tries: bool = False
    ) -> Union[str, List[str]]:
        """Writes agent-aware code based on the given description."""
        system_prompt = ifnone(system_prompt, default=self.write_agent_code_prompt)
        code = self.write_code(
            description=description,
            max_tries=max_tries,
            system_prompt=system_prompt,
            return_intermediate_tries=return_intermediate_tries
        )
        return code

    def agent_code_from_context(self, context: Context) -> Context:
        """Generates agent-aware code according to the context instruction."""
        code = self.write_agent_code(description=context.instruction)
        context.conversation.add_message(Chat.Message(sender='assistant', message=code))
        return context

    def code_from_context(self, context: Context) -> Context:
        """Generates code according to the context instruction."""
        code = self.write_code(description=context.instruction)
        context.conversation.add_message(Chat.Message(sender='assistant', message=code))
        return context

    def stm_from_chat(self, conversation: Chat) -> ShortTermModule:
        """Generate stm from the last Assistant message."""
        context = Context(conversation=conversation)
        context = self.stm_from_context(context)
        return context.short_term_memory

    def fetch_code_from_context(self, context: Context) -> str:
        """Finds and segments out the last code block from the context conversation."""
        code = None
        for message in reversed(context.conversation.history()):
            if message.sender == 'assistant':
                code = clean_code(message.message)
                break

        return code

    def stm_from_context(self, context: Context) -> Context:
        """Generates stm according to the last Assistant message."""
        code = self.fetch_code_from_context(context)
        if code is None:
            raise CodingError(
                'Requested to create an ShortTermModule from code, but code could not be found from context.')

        stm = self.create_stm(code)
        context.short_term_memory = stm

        response = Chat.Message(
            sender='assistant',
            message='ShortTermModule created and placed into the context\'s short term memory.'
        )
        context.conversation.add_message(response)

        return context

    def __call__(self, description: str, max_tries: Optional[int] = None, return_intermediate_tries: bool = False) -> str:
        return self.write_code(
            description=description, max_tries=max_tries, return_intermediate_tries=return_intermediate_tries)


Coder.register_action('write_code')
Coder.register_action('create_stm')
Coder.register_action('fetch_code_from_context')
Coder.register_action('code_from_context')
Coder.register_action('agent_code_from_context')
Coder.register_action('stm_from_context')
Coder.register_action('exec')
Coder.register_action('__call__')
Coder.register_task('Coder')
