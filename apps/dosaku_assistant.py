import gradio as gr

from dosaku.agents import Dosaku

dosk = Dosaku(enable_services=True)


def main():
    with gr.Blocks(title='Dosaku', theme='HaleyCH/HaleyCH_Theme') as demo:
        chatbot = gr.Chatbot(height=600, show_label=False)

        with gr.Row():
            msg = gr.Textbox(show_label=False, placeholder='Type message')
        with gr.Accordion('Microphone'):
                microphone = gr.Microphone(streaming=True, show_label=False)
                auto_response = gr.Checkbox(label='Auto send message', value=True)
                use_spellchecker = gr.Checkbox(label='Use spellchecker', value=True)
        streaming_audio = gr.State(False)

        def reset_msg(message, history):
            if history is None:
                history = list()
            return "", history + [[message, None]]

        def predict(history):
            for partial_response in dosk.Chat(history[-1][0]):
                history[-1][1] = partial_response
                print(f'{partial_response}')
                yield history

        def start_audio_stream():
            dosk.RealtimeSpeechToText.reset_stream()
            streaming_audio.value = True
            return ''

        def process_audio_stream(new_chunk):
            if streaming_audio.value is True:
                text = dosk.RealtimeSpeechToText.stream(new_chunk)
            else:
                text = dosk.RealtimeSpeechToText.text()
            return text

        def stop_audio_stream(text, history, use_spellchecker, auto_response):
            streaming_audio.value = False
            if use_spellchecker:
                text = dosk.Spellchecker(text)
            dosk.RealtimeSpeechToText.text(text)

            if auto_response:
                history.append([text, None])
                for partial_response in dosk.Chat(history[-1][0]):
                    history[-1][1] = partial_response
                    print(f'{partial_response}')
                    yield '', history
            else:
                return text, history


        msg.submit(reset_msg, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
            predict, inputs=chatbot, outputs=chatbot
        )

        microphone.start_recording(start_audio_stream, inputs=None, outputs=msg)

        microphone.stream(
            process_audio_stream,
            inputs=microphone,
            outputs=msg)

        microphone.stop_recording(
            stop_audio_stream, inputs=[msg, chatbot, use_spellchecker, auto_response], outputs=[msg, chatbot], queue=True)

    demo.queue()
    demo.launch()


if __name__ == "__main__":
    main()
