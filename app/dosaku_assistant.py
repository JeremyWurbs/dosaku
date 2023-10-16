import gradio as gr
import openai

from dosaku import Config
from dosaku.agents import Dosaku


def main():
    config = Config()
    openai.api_key = config['API_KEYS']['OPENAI']

    dosaku = Dosaku(enable_services=True)

    def predict(message, _):
        for partial_response in dosaku.Chat(message):
            yield partial_response

    gr.ChatInterface(
        predict,
        chatbot=gr.Chatbot(height=600),
        title='Dosaku',
        theme='HaleyCH/HaleyCH_Theme',
        retry_btn=None,
        undo_btn=None,
        clear_btn=None,
        submit_btn=None,
    ).queue().launch()


if __name__ == "__main__":
    main()
