import os
import tempfile
from typing import Union, Literal
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def tts(text: str, model: Union[str, Literal["tts-1", "tts-1-hd"]],
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        output_file_format: Literal["mp3", "opus", "aac", "flac", ""] = "",
        speed: float = 1.0, api_key_input: str = ""):
    openai_key = api_key_input if api_key_input else os.getenv("OPENAI_KEY")
    if not openai_key:
        raise gr.Error("OpenAI API Key is not provided. Please enter a valid API key.")

    try:
        client = OpenAI(api_key=openai_key)
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=output_file_format,
            speed=speed
        )
    except Exception as error:
        print(str(error))
        raise gr.Error("生成语音时出现错误，请检查您的 API 密钥后重试。")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(response.content)

    temp_file_path = temp_file.name
    return temp_file_path

def launch_with_optional_auth():
    # 从环境变量中读取用户名和密码，如果没有设置，则使用默认值
    default_username = "admin"
    default_password = "123"
    username = os.getenv("GRADIO_USERNAME", default_username)
    password = os.getenv("GRADIO_PASSWORD", default_password)

    auth = None
    if os.getenv("LOGIN", "false").lower() == "true":
        auth = (username, password)

    with gr.Blocks() as demo:
        gr.Markdown("# <center> OpenAI 文本转语音 API 接口 </center>")
        with gr.Row(variant="panel"):
            model = gr.Dropdown(choices=["tts-1", "tts-1-hd"], label="模型", value="tts-1")
            voice = gr.Dropdown(choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"], label="声音选项", value="onyx")
            output_file_format = gr.Dropdown(choices=["mp3", "opus", "aac", "flac"], label="输出格式", value="mp3")
            speed = gr.Slider(minimum=0.25, maximum=4.0, value=1.0, step=0.01, label="速度")
            api_key_input = gr.Textbox(label="OpenAI API 密钥", placeholder="如果环境变量中未设置，请在此输入您的 OpenAI API 密钥。")

        text = gr.Textbox(label="输入文本", placeholder="请输入您的文本，然后点击下面的“文本转语音”按钮，或直接按 Enter 键。", lines=12)
        btn = gr.Button("文本转语音")
        output_audio = gr.Audio(label="语音输出")

        text.submit(fn=tts, inputs=[text, model, voice, output_file_format, speed, api_key_input], outputs=output_audio, api_name="tts")
        btn.click(fn=tts, inputs=[text, model, voice, output_file_format, speed, api_key_input], outputs=output_audio, api_name=False)

    demo.launch(server_name="0.0.0.0", auth=auth)

launch_with_optional_auth()
