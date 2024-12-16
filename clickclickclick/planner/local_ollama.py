from ollama import Client
from typing import Any
from . import Planner, logger
from clickclickclick.config import BaseConfig
from clickclickclick.executor import Executor


class OllamaPlanner(Planner):
    def __init__(self, c: BaseConfig, executor: Executor, host=None):
        if host is None:
            host = "http://localhost:11434"
        prompts = c.prompts
        system_prompt = f"{prompts['common-planner-prompt']}\n{prompts['specific-planner-prompt']}"
        planner_config = c.models.get("planner_config")
        self.client = Client(host=host)
        self.model_name = planner_config.get("model_name")
        function_declarations = c.function_declarations
        self.executor = executor
        self.chat_history = [
            {
                "role": "system",
                "content": system_prompt,  # + "\nHere is a exact list of functions in JSON format that you can invoke.\n\n{functions}\n , Make sure you do not use any other function.".format(functions=function_declarations),
            }
        ]
        # Create tool representations directly
        self.tools = []
        for func in function_declarations:
            tool = {"type": "function", "function": func}
            self.tools.append(tool)

    def llm_response(self, prompt=None, screenshot=None) -> list[tuple[str, dict]]:
        # Remove items with 'images' key from chat history
        self.chat_history = [entry for entry in self.chat_history if "images" not in entry]

        if screenshot:
            self.chat_history.append(
                {
                    "role": "user",
                    "content": prompt or "New screenshot for the task attached",
                    "images": [screenshot],
                }
            )
        else:
            self.chat_history.append({"role": "user", "content": prompt})
        import time

        start_time = time.time()  # Record the start time
        response = self.client.chat(
            model=self.model_name, messages=self.chat_history, tools=self.tools
        )
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate the elapsed time
        print(f"Time required to run the statement: {elapsed_time} seconds")
        print(response, "all res[ponse]")
        tool_calls = response["message"].get("tool_calls", [])

        if tool_calls:
            print(tool_calls, "tool calls")
            functions_list = []
            for tool_call in tool_calls:
                function_call = tool_call["function"]
                function_name = function_call["name"]
                args = function_call.get("arguments", {})

                self.chat_history.append(
                    {"role": "assistant", "content": f"Function: {function_name} with args: {args}"}
                )

                print(f"Function Call: {function_name} with args: {args}")
                if "observation" not in args:
                    args["observation"] = "NA"
                functions_list.append((function_name, args))
            return functions_list

        # Log the response content when there's no function call
        logger.info(response["message"]["content"])
        return response["message"]["content"]

    def add_finder_message(self, message):
        self.chat_history.append({"role": "user", "content": message})

    def task_finished(self, reason, observation: str):
        logger.info(f"Task finished, reason: {reason}")
