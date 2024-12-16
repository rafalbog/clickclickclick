import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool, File
from google.generativeai.protos import FunctionCallingConfig, ToolConfig
from typing import Any
from PIL import Image
import tempfile
from clickclickclick.config import BaseConfig
from . import Planner, logger


class GeminiPlanner(Planner):
    def __init__(self, c: BaseConfig):
        prompts = c.prompts
        system_instruction = (
            f"{prompts['common-planner-prompt']}\n{prompts['specific-planner-prompt']}"
        )
        planner_config = c.models.get("planner_config")
        api_key = planner_config.get("api_key")
        model_name = planner_config.get("model_name")
        generation_config = planner_config.get("generation_config")

        function_declarations = c.function_declarations
        logger.info("Gemini Planner init")
        genai.configure(api_key=api_key)
        self.chat_history = []
        # Create FunctionDeclaration objects
        self.functions = []
        for func in function_declarations:
            parameters = func.get("parameters")
            if parameters is None:
                function_declaration = FunctionDeclaration(
                    name=func["name"], description=func["description"]
                )
            else:
                function_declaration = FunctionDeclaration(
                    name=func["name"],
                    description=func["description"],
                    parameters=func["parameters"],
                )
            self.functions.append(function_declaration)
        all_functions_tool = Tool(function_declarations=self.functions)
        tool_config = ToolConfig(
            function_calling_config=FunctionCallingConfig(
                # ANY mode forces the model to predict only function calls
                mode=FunctionCallingConfig.Mode.ANY,
                # Allowed function calls to predict when the mode is ANY. If empty, any  of
                # the provided function calls will be predicted.
            )
        )
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
            tools=[all_functions_tool],
            tool_config=tool_config,
        )

    def llm_response(self, prompt=None, screenshot=None) -> list[tuple[str, dict]]:
        # Remove any previous screenshots from the chat history
        self.chat_history = [
            message
            for message in self.chat_history
            if not (
                message.get("role") == "user" and isinstance(message.get("parts", [{}])[0], File)
            )
        ]
        # todo
        assert screenshot.endswith(".png")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file_path = temp_file.name

        # Resize the image
        with Image.open(screenshot) as img:
            # Example resize operation, may need to adjust size
            img = img.resize((768, 768))  # todo from config
            img.save(temp_file_path)

        file = genai.upload_file(temp_file_path, mime_type="image/png")
        # Append the current screenshot to the chat history
        self.chat_history.append({"role": "user", "parts": [file]})

        logger.info(self.chat_history)
        self.chat_session = self.model.start_chat(history=self.chat_history)
        response = self.chat_session.send_message(f"{prompt}")  # Adjust as needed
        logger.info(response)
        for i in range(len(response.candidates[0].content.parts)):
            try:
                function_call = response.candidates[0].content.parts[i].function_call
                break
            except Exception as e:
                pass
        function_name = function_call.name

        # user prompt needs to be only inserted one time
        if not any(
            message.get("parts", [None])[0] == prompt
            for message in self.chat_history
            if message.get("role") == "user"
        ):
            self.chat_history.append({"role": "user", "parts": [prompt]})

        args = function_call.args
        d = {key: args[key] for key in args}
        logger.info(f"{d} args")
        self.chat_history.append(
            {"role": "model", "parts": [f"function name: {function_name} args: {d}"]}
        )

        if function_name == "task_finished":
            with open("planner.logs", "a") as f:
                f.write("\n".join(map(str, self.chat_history)))
                f.write("\n\n")
        return [(function_name, {key: args[key] for key in args})]

    def add_finder_message(self, message):
        self.chat_history.append({"role": "user", "parts": [message]})

    def task_finished(self, reason, observation: str):
        logger.info(f"Task finished, reason: {reason}")
