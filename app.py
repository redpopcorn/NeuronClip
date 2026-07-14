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
    gr.Markdown("This Hugging Face Space hosts the ClipNeuron FastAPI backend. The API endpoints are accessible under the `/api` prefix.")

# Mount our FastAPI app under /api on Gradio's FastAPI app.
# This allows Gradio to manage the server lifecycle and port bindings automatically.
demo.app.mount("/api", fastapi_app)

# Launch Gradio (this automatically binds to the correct port and blocks)
demo.launch()
