import uvicorn
from clickclickclick.config import get_config
from clickclickclick.executor.android import AndroidExecutor
from clickclickclick.finder.gemini import GeminiFinder
from clickclickclick.finder.local_ollama import OllamaFinder
from clickclickclick.finder.openai import OpenAIFinder
from clickclickclick.planner.gemini import GeminiPlanner
from clickclickclick.planner.local_ollama import OllamaPlanner
from clickclickclick.planner.openai import ChatGPTPlanner
from clickclickclick.planner.task import execute_task, execute_with_timeout
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from github.clickclickclick.clickclickclick.executor.wind import WindowsExecutor

app = FastAPI()


class TaskRequest(BaseModel):
    task_prompt: str
    platform: str = "android"
    planner_model: str = "openai"
    finder_model: str = "gemini"


@app.post("/execute")
def execute_task_api(request: TaskRequest):
    task_prompt = request.task_prompt
    platform = request.platform
    planner_model = request.planner_model
    finder_model = request.finder_model

    c = get_config(platform, planner_model, finder_model)

    if platform == "win":
        executor = WindowsExecutor()
    elif platform == "android":
        executor = AndroidExecutor()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    if planner_model == "openai":
        executor.screenshot_as_base64 = True
        planner = ChatGPTPlanner(c)
    elif planner_model == "gemini":
        executor.screenshot_as_tempfile = True
        planner = GeminiPlanner(c)
    elif planner_model == "ollama":
        executor.screenshot_as_tempfile = True
        planner = OllamaPlanner(c, executor)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported planner model: {planner_model}")

    if finder_model == "openai":
        finder = OpenAIFinder(c, executor)
    elif finder_model == "gemini":
        finder = GeminiFinder(c, executor)
    elif finder_model == "ollama":
        finder = OllamaFinder("llama3.2-vision", executor)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported finder model: {finder_model}")

    result = execute_with_timeout(execute_task, c.TASK_TIMEOUT_IN_SECONDS, task_prompt, executor, planner, finder, c)

    if result is not None:
        return {"result": result}
    else:
        raise HTTPException(status_code=500, detail="Task execution failed")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
