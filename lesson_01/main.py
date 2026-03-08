import os
from pathlib import Path

import requests
from requests.exceptions import RequestException

print("Hello, Rodrigo!")

name = "Rodrigo"
age = 45

print("My name is " + name + " and I am " + str(age) + " years old.")

numbers = [1, 2, 3, 4, 5]
print("The numbers are: " + str(numbers))

user = {
    "name": "Rodrigo",
    "age": 45
}

print("User info: " + user["name"] + ", " + str(user["age"]) + " years old.")

logs = [
    "error: something went wrong",
    "error : failed to connect to database",
    "warning: low disk space"
]

# for log in logs:
#     if "error" in log:
#         print("Error found: " + log)


# logs_path = Path(__file__).with_name("logs.txt")
# with logs_path.open() as file:
#     logs = file.readlines()

# print(logs)

def count_errors(logs: list[str]) -> int:
    count = 0
    for log in logs:
        if is_error(log):
            count += 1
    return count

def is_error(log: str) -> bool:
    return "error" in log.casefold()


def load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            os.environ[key] = value

logs_path = Path(__file__).with_name("logs.txt")
with logs_path.open(encoding="utf-8") as file:
    logs = file.readlines()

# for log in logs:
#     if is_error(log):
#         print("Error found in file: " + log.rstrip())
error_count = count_errors(logs)
print("Total errors found: " + str(error_count))

try:
    response = requests.get("https://api.github.com", timeout=10)
    response.raise_for_status()
    print(response.status_code)
except RequestException as exc:
    print("GitHub request failed: " + str(exc))

try:
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    print("Current Bitcoin price in USD: " + str(data["bitcoin"]["usd"]))
except RequestException as exc:
    print("Bitcoin API request failed: " + str(exc))
except (KeyError, TypeError, ValueError) as exc:
    print("Unexpected Bitcoin API response: " + str(exc))

load_env_file(Path(__file__).with_name(".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("OPENAI_API_KEY not found in .env. Add your key to run the OpenAI example.")
else:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=openai_api_key)
        response = client.responses.create(
            model="gpt-5-mini",
            input="Explain the difference between a list and a tuple in Python.",
        )
        print("AI response: " + response.output_text)
    except ImportError:
        print("openai package not installed. Run: python -m pip install openai")
    except Exception as exc:
        error_text = str(exc)
        lowered_error = error_text.casefold()

        if "insufficient_quota" in lowered_error or "exceeded your current quota" in lowered_error:
            print("OpenAI API sem cota/creditos. Verifique Billing e Usage em https://platform.openai.com/.")
        elif "invalid_api_key" in lowered_error or "incorrect api key" in lowered_error:
            print("OPENAI_API_KEY invalida. Confira a chave no arquivo .env.")
        else:
            print("OpenAI request failed: " + error_text)