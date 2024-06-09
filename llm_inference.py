from singletons import OpenAIClientSingleton, GoogleGeminiClientSingleton
import json
from diagrams_to_drawio import render_diagram_file_to_drawio_file
import re


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


        
        
