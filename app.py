import os
import sys
from pathlib import Path

# Add src and server to path
APP_ROOT = Path(__file__).resolve().parent
sys.path.append(str(APP_ROOT / "src"))
sys.path.append(str(APP_ROOT))

import spaces
import gradio as gr
from server.main import app as fastapi_app


# ZeroGPU requires at least one @spaces.GPU decorated function
@spaces.GPU
def health_check():
    """Dummy GPU function required by ZeroGPU Spaces."""
    return "ClipNeuron API is running!"


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🚀 ClipNeuron API Backend")
    gr.Markdown(
        "This Hugging Face Space hosts the ClipNeuron FastAPI backend.\n\n"
        "API endpoints are available under `/api`."
    )
    btn = gr.Button("Health Check")
    output = gr.Textbox(label="Status")
    btn.click(fn=health_check, inputs=[], outputs=[output])

# Mount FastAPI under /api on Gradio's internal server
demo.app.mount("/api", fastapi_app)

# Let Gradio manage the server lifecycle (port, blocking, etc.)
demo.launch()
