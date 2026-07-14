import os
import sys
from pathlib import Path

# Add src and server to path
APP_ROOT = Path(__file__).resolve().parent
sys.path.append(str(APP_ROOT / "src"))
sys.path.append(str(APP_ROOT))

import gradio as gr
from server.main import app as fastapi_app

# Simple Gradio interface to satisfy Hugging Face and show status
with gr.Blocks() as demo:
    gr.Markdown("# 🚀 ClipNeuron API Backend")
    gr.Markdown("This Hugging Face Space hosts the ClipNeuron FastAPI backend. The API endpoints are accessible at the root `/` URL.")

# Mount Gradio interface inside our FastAPI application
app = fastapi_app
app = gr.mount_gradio_app(app, demo, path="/status")
