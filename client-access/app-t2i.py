import os
from dotenv import load_dotenv
import gradio as gr
import logging
import random
from ComfyUIClient import ComfyUIClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
)

# Load environment variables from the .env file
load_dotenv()

# Load environment variables
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
WORKFLOW_TEMPLATE = os.getenv('WORKFLOW_TEMPLATE', 't2i_workflow_api.json')
ENDPOINT_URL = os.getenv('ENDPOINT_URL', 'https://api.runpod.ai/v2')
API_KEY = os.getenv('API_KEY', 'your_api_key')
ENDPOINT_ID = os.getenv('ENDPOINT_ID', 'your_endpoint_id')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def text_generate_image(prompt_text):
    logging.debug("Received prompt_text: %s", prompt_text)
    try:
        client = ComfyUIClient(endpoint_url=ENDPOINT_URL, api_key=API_KEY, endpoint_id=ENDPOINT_ID, output_dir=OUTPUT_DIR)

        # Load and update the workflow
        logging.debug("Loading workflow from %s...", WORKFLOW_TEMPLATE)
        client.load_workflow(
            filepath=WORKFLOW_TEMPLATE,
            seed_node_number=3,
            positive_prompt_node_number=6,
            output_node_number=9
        )
        logging.debug("Workflow loaded successfully.")

        logging.debug("Updating seed node...")
        client.update_seed_node(random.randint(1, 1500000))
        logging.debug("Seed node updated.")

        logging.debug("Updating positive prompt node...")
        client.update_positive_prompt(prompt_text)
        logging.debug("Positive prompt node updated.")

        logging.debug("Requesting images synchronously...")
        response = client.queue_prompt_sync()
        
        logging.debug("Images generated successfully.")

        logging.debug("Response JSON: %s", client._summarize_dict(response))
        
        if response['status'] == "COMPLETED" and 'saved_images' in response:
            return response['saved_images']
        else:
            raise Exception(f"Job failed with status: {response['status']}")

    except Exception as e:
        logging.error("An error occurred: %s", e)
        return []

# Define the Gradio interface with one input: a text prompt
iface = gr.Interface(
    fn=text_generate_image,
    inputs=[
        gr.Textbox(lines=20, label="Prompt")
    ],
    outputs=gr.Gallery(label="Generated Images", columns=2),
    title="ComfyUI Text-to-Image Generator",
    description="Enter a prompt to generate images using ComfyUI."
)

# Launch the Gradio interface
iface.launch()
