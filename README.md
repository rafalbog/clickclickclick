## ClickClickClick

### A framework to enable autonomous android and computer use using any LLM (local or remote)

![click3](https://github.com/user-attachments/assets/103afd59-ae29-45d2-9d77-75375b1538a0)

## Demos

### create a draft gmail and ask him if he is free for lunch on coming saturday at 1PM. Congratulate on the baby - write one para.
https://github.com/user-attachments/assets/7cdbebb7-0ac4-4c20-8d67-f3c07cd4ab01

### Can you open the browser at https://www.google.com/maps/ and answer the corresponding task: Find bus stops in Alanson, MI
https://github.com/user-attachments/assets/eb5dc968-206b-422d-aa3c-20c48bac3fed

### start a 3+2 game on lichess
https://github.com/user-attachments/assets/68fc3475-2299-4254-8673-3123356177b5


Currently supporting local models via Ollama (Llama 3.2-vision), Gemini, GPT 4o. The current code is highly experimental and will evolve in future commits. Please use at your own risk.

The best result currently comes from using GPT 4o/4o-mini as planner and Gemini Pro/Flash as finder.

![model recommendations](https://github.com/user-attachments/assets/355865f9-704b-483c-a23b-5dc9be54aeda)


#### Prerequisites

1. This project needs `adb` to be installed on your local machine where the code is being executed.
2. Enable USB debugging on the android phone.
3. Python >= 3.11

# How to install

Clone the repository and navigate into the project directory:

```sh
git clone https://github.com/BandarLabs/clickclickclick
cd clickclickclick
```

It is recommended to create a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the dependencies:

```sh
pip install -r requirements.txt
```


# How to use

Put your model specific settings in `config/models.yaml` and export the keys specified in the yaml file.

## As CLI tool

### Install the tool

(Ensure `OPENAI_API_KEY` and `GEMINI_API_KEY` API keys in the environment)

```sh
pip install <repo-tar>
```

```sh
click3 run open uber app
```


## As Script

### Setup

By default, planner is `openai` and finder is `gemini`.

You can change the default configuration in `config/models.yaml`

Before running any tasks, you need to configure respective keys like `OPENAI_API_KEY` and `GEMINI_API_KEY` in the environment.

Gemini Flash gives free 15 API calls - https://aistudio.google.com/apikey

### Running Tasks

To execute a task, use the `run` command. The basic usage is:

```sh
python main.py run <task-prompt>
```

#### Options

- `--platform`: Specifies the platform to use, either `android` or `osx`. Default is `android`.

  ```sh
  python main.py run "example task" --platform=osx
  ```

- `--planner-model`: Specifies the planner model to use, either `openai`, `gemini`, or `ollama`. Default is `openai`.

  ```sh
  python main.py run "example task" --planner-model=gemini
  ```

- `--finder-model`: Specifies the finder model to use, either `openai`, `gemini`, or `ollama`. Default is `gemini`.

  ```sh
  python main.py run "example task" --finder-model=ollama
  ```

### Example

A full example command might look like:

```sh
python main.py run "Open Google news" --platform=android --planner-model=openai --finder-model=gemini
```

## Use as an API

### To run the app
```sh
uvicorn api:app
```
### POST /execute

#### Description:
This endpoint executes a task based on the provided task prompt, platform, planner model, and finder model.

#### Request Body:
- `task_prompt` (string): The prompt for the task that needs to be executed.
- `platform` (string, optional): The platform on which the task is to be executed. Default is "android". Supported platforms: "android", "osx".
- `planner_model` (string, optional): The planner model to be used for planning the task. Default is "openai". Supported models: "openai", "gemini", "ollama".
- `finder_model` (string, optional): The finder model to be used for finding elements to interact with. Default is "gemini". Supported models: "gemini", "openai", "ollama".

#### Response:
- `200 OK`:
  - `result` (object): The result of the task execution.
- `400 Bad Request`:
  - `detail` (string): Description of why the request is invalid (e.g., unsupported platform, unsupported planner model, unsupported finder model).
- `500 Internal Server Error`:
  - `detail` (string): Description of the error that occurred during task execution.

#### Example Request:
```bash
curl -X POST "http://localhost:8000/execute" -H "Content-Type: application/json" -d '{
  "task_prompt": "Open uber app",
  "platform": "android",
  "planner_model": "openai",
  "finder_model": "gemini"
}'
```

#### Example Response:
```json
{"result":true}
```


#### How to contribute

Contributions are welcome! Please begin by opening an issue to discuss your ideas. Once the issue is reviewed and assigned, you can proceed with submitting a pull request.


#### Things to do

* [ ] Enable local models via Ollama on Android
* [ ] Make computer use fully functional



## License

This project is licensed under the MIT License. See the LICENSE file for details.
