import os
import gradio as gr
from main import iface, CSS

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    is_cloud = "PORT" in os.environ
    iface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=not is_cloud,
        theme=gr.themes.Base(),
        css=CSS
    )
