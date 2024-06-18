import os
from dotenv import load_dotenv
import gradio as gr
import logging
import random
from shutil import copyfile
from ComfyUIClient import ComfyUIClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'
)

# Load environment variables from the .env file
load_dotenv()

# Load environment variables
INPUT_DIR = os.getenv('INPUT_DIR', './input')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
WORKFLOW_TEMPLATE = os.getenv('WORKFLOW_TEMPLATE', 'i2i_workflow_api.json')
ENDPOINT_URL = os.getenv('ENDPOINT_URL', 'https://api.runpod.ai/v2')
API_KEY = os.getenv('API_KEY', 'your_api_key')
ENDPOINT_ID = os.getenv('ENDPOINT_ID', 'your_endpoint_id')

# Create output and input directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

def image_generate_image(local_image, prompt_text):
    logging.debug("Received prompt_text: %s", prompt_text)
    logging.debug("Received local_image: %s", local_image)
    try:
        client = ComfyUIClient(endpoint_url=ENDPOINT_URL, api_key=API_KEY, endpoint_id=ENDPOINT_ID, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR)

        # Load and update the workflow
        logging.debug("Loading workflow from %s...", WORKFLOW_TEMPLATE)
        client.load_workflow(
            filepath=WORKFLOW_TEMPLATE,
            load_image_node_number=72,
            seed_node_number=63,
            positive_prompt_node_number=66,
            output_node_number=69
        )
        logging.debug("Workflow loaded successfully.")

        # Save the input image to INPUT_DIR
        input_image_path = os.path.join(INPUT_DIR, os.path.basename(local_image))
        copyfile(local_image, input_image_path)
        logging.debug("Saved input image to %s", input_image_path)
        
        # Upload the image
        logging.debug("Uploading image...")
        image_data = client.upload_image(input_image_path)
        logging.debug("Encoded image data: %s", image_data[:50])  # Log the beginning of the base64 string for debugging
        
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

# Define the Gradio interface with two inputs: a local image and a text prompt
iface = gr.Interface(
    fn=image_generate_image,
    inputs=[
        gr.Image(type="filepath", label="Upload Image"),
        gr.Textbox(lines=20, label="Prompt")
    ],
    outputs=gr.Gallery(label="Generated Images", columns=2),
    title="ComfyUI Image Generator",
    description="Upload an image and enter a prompt to generate images using ComfyUI."
)

# Launch the Gradio interface
iface.launch()
