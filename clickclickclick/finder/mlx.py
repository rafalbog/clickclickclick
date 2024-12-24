from clickclickclick.config import BaseConfig
from . import BaseFinder, logger
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_config
from tempfile import NamedTemporaryFile
import re
import json
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def extract_coordinates(response_text):
    # Define a regex pattern to capture key-value pairs in the format key="value" or key: value
    pattern = r'(\w+)=?\"?(\d*\.\d+|\d+)\"?|(\w+):\s*(\d*\.\d+)'

    # Use regular expression to find all key-value pairs
    matches = re.findall(pattern, response_text)

    # Convert matches into a dictionary
    coordinates_dict = {}
    for match in matches:
        if match[0]:  # for key="value" pattern
            key = match[0]
            value = match[1]
        else:  # for key: value pattern
            key = match[2]
            value = match[3]
        # Convert each value to int after float conversion for precision if needed
        coordinates_dict[key] = int(float(value))

    # Define the normalization mapping
    conversion_map = {
        "x1": "xmin",
        "y1": "ymin",
        "x2": "xmax",
        "y2": "ymax"
    }

    # Transform the extracted coordinates into a standardized format
    standardized_coordinates = {conversion_map[key]: coordinates_dict[key] for key in conversion_map if key in coordinates_dict}
    standardized_coordinates.update(coordinates_dict)
    # Convert the standardized dictionary to a JSON string
    response_json = json.dumps(standardized_coordinates)

    return response_json


class MLXFinder(BaseFinder):
    def __init__(self, c: BaseConfig, executor, model_path="mlx-community/Molmo-7B-D-0924-4bit"):
        self.executor = executor
        self.config = load_config(model_path)
        self.model, self.processor = load(model_path, {"trust_remote_code": True})
        # self.image_finder_prompt = c.prompts["image-finder-prompt"]
        self.system_prompt = c.prompts["finder-system-prompt"]
        finder_config = c.models.get("finder_config")
        self.IMAGE_WIDTH = finder_config.get("image_width")
        self.IMAGE_HEIGHT = finder_config.get("image_height")
        self.OUTPUT_WIDTH = finder_config.get("output_width")
        self.OUTPUT_HEIGHT = finder_config.get("output_height")
        self.model_name = finder_config.get("model_name")

    def process_image(self, image_path, prompt):
        formatted_prompt = apply_chat_template(
            self.processor, self.config, prompt, num_images=1
        )
        output = generate(self.model, self.processor, [image_path], formatted_prompt, verbose=False)
        print(output)
        try:
            logger.debug(output)
            return output
        except Exception as e:
            logger.error("Error processing image:", e)
            return ""

    # Example usage
    def process_segment(self, segment, model_name, prompt):
        prompt = f'UI bounds of "{prompt}" as ymin,ymax,xmin,xmax format strictly.  '
        segment_image, coordinates = segment
        with NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            segment_image.save(temp_file, format="PNG")
            temp_file_path = temp_file.name
            response_text = self.process_image(temp_file_path, prompt)
            response_json_str = extract_coordinates(response_text)

            return (response_json_str, coordinates)

# Example instantiation and usage would resemble how you manage the base classes and client interactions.