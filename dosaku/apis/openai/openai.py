from typing import List

import openai

from dosaku import Config


class OpenAI:
    """"""
    """OpenAI wrapper class around OpenAI's public API.

    OpenAI requires an API key to use. Put the API key in dosaku/config/config.ini.
    """
    config = Config()
    openai.api_key = config['API_KEYS']['OPENAI']

    def chat(self, system: str, user_assistant: List[str]):
        """Send a system chat message and receive a response.

        Example::

            from dosaku.apis import OpenAI

            openai = OpenAI()
            response = openai.chat(
                system='You are a machine learning expert.',
                user_assistance=['Explain what a neural network is.'])
            print(response)  # A neural network is a type of machine learning model that is inspired by the...
        """
        system_msg = [{"role": "system", "content": system}]
        user_assistant_msgs = [
            {"role": "assistant", "content": user_assistant[i]} if i % 2 else {"role": "user",
                                                                               "content": user_assistant[i]}
            for i in range(len(user_assistant))]

        msgs = system_msg + user_assistant_msgs
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=msgs)
        status_code = response["choices"][0]["finish_reason"]
        assert status_code == "stop", f"The status code was {status_code}."

        return response["choices"][0]["message"]["content"]
