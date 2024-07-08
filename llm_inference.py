from singletons import OpenAIClientSingleton, GoogleGeminiClientSingleton
import json
from diagrams_to_drawio import render_diagram_file_to_drawio_file
import re
import requests
from config import read_openai_config

openai_config = read_openai_config()


class LLMInference:
    def __init__(self):
        self.gpt4o_openai_client = OpenAIClientSingleton.get_gpt4o_openai_client()
        self.gemini_google_client = GoogleGeminiClientSingleton.initialise_gemini_client()
    
    def remove_code_block_markers(text):
        # Remove the starting ```python
        text = re.sub(r'^```python', '', text, flags=re.MULTILINE)
        # Remove the ending ```
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        # Strip leading and trailing whitespace
        return text.strip()
    
    def run_inference_openai(self,input_data_stream:str):
        json_file_path = "prompt.json"
        with open(json_file_path, 'r') as file:
            json_prompt = json.load(file)
        max_completion_tokens = 4096
        system_prompt = str(json_prompt)
        prompt = system_prompt + str(input_data_stream)
        file_name = input_data_stream['file_name']
        response = self.gpt4o_openai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model = "gpt-4o",
            max_tokens=max_completion_tokens,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        render_diagram_file_to_drawio_file(file=response.choices[0].message.content, file_name=file_name)
        output_data = {
        "png_path": f"{file_name}.png",
        "drawio_path": f"{file_name}.drawio"
    }
        return output_data
    
    def run_inference_google(self,input_data_stream:str):
        json_file_path = "prompt.json"
        with open(json_file_path, 'r') as file:
            json_prompt = json.load(file)
        # max_completion_tokens = 4096
        system_prompt = str(json_prompt)
        prompt = system_prompt + str(input_data_stream)
        file_name = input_data_stream['file_name']
        response = self.gemini_google_client.generate_content(prompt)
        def remove_code_block_markers(text):
            # Remove the starting ```python
            text = re.sub(r'^```python', '', text, flags=re.MULTILINE)
            # Remove the ending ```
            text = re.sub(r'```$', '', text, flags=re.MULTILINE)
            # Strip leading and trailing whitespace
            return text.strip()
        render_diagram_file_to_drawio_file(file=remove_code_block_markers(response.text), file_name=file_name)
        output_data = {
        "png_path": f"{file_name}.png",
        "drawio_path": f"{file_name}.drawio"
    }
        return output_data
    
    def run_image_inference_openai(self,input_image_base64):
        system_prompt = """Receive the input image and consider only the input image and nothing else. You need to generate an incredibly detailed description of the input image, which can be
        used by a diffusion model like DALL-E to generate a version of the image very similar to the input image. Output only that description and absolutely nothing else."""
        api_key = openai_config.get('gpt4o_openai_api_key')
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

        payload = {
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"{system_prompt}",
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{input_image_base64}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        image_response = self.gpt4o_openai_client.images.generate(
        model="dall-e-2",
        prompt=f"{response}",
        size="1024x1024",
        quality="standard",
        n=1,
        )

        image = image_response.data[0].b64_json
        print(response)
        return image




        
        
