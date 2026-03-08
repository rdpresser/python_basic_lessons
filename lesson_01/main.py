import os
from pathlib import Path

import requests
from requests.exceptions import RequestException

NAME = "Rodrigo"
AGE = 45
NUMBERS = [1, 2, 3, 4, 5]
USER = {
    "name": NAME,
    "age": AGE,
}
GITHUB_API_URL = "https://api.github.com"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

def count_errors(logs: list[str]) -> int:
    return sum(1 for log in logs if is_error(log))


def is_error(log: str) -> bool:
    return "error" in log.casefold()


def print_intro() -> None:
    print("Hello, Rodrigo!")
    print("My name is " + NAME + " and I am " + str(AGE) + " years old.")
    print("The numbers are: " + str(NUMBERS))
    print("User info: " + USER["name"] + ", " + str(USER["age"]) + " years old.")


def read_logs(log_file: Path) -> list[str]:
    try:
        with log_file.open(encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        print("logs.txt not found at: " + str(log_file))
        return []


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

def fetch_github_status() -> None:
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        response.raise_for_status()
        print(response.status_code)
    except RequestException as exc:
        print("GitHub request failed: " + str(exc))


def fetch_bitcoin_price() -> None:
    try:
        response = requests.get(COINGECKO_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("Current Bitcoin price in USD: " + str(data["bitcoin"]["usd"]))
    except RequestException as exc:
        print("Bitcoin API request failed: " + str(exc))
    except (KeyError, TypeError, ValueError) as exc:
        print("Unexpected Bitcoin API response: " + str(exc))


def run_openai_example(env_file: Path) -> None:
    load_env_file(env_file)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL

    if not openai_api_key:
        print("OPENAI_API_KEY not found in .env. Add your key to run the OpenAI example.")
        return

    try:
        from openai import OpenAI

        client = OpenAI(api_key=openai_api_key)
        response = client.responses.create(
            model=openai_model,
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


def main() -> None:
    print_intro()

    project_root = Path(__file__).resolve().parent.parent
    logs_path = Path(__file__).with_name("logs.txt")
    logs = read_logs(logs_path)
    error_count = count_errors(logs)
    print("Total errors found: " + str(error_count))

    fetch_github_status()
    fetch_bitcoin_price()
    run_openai_example(project_root / ".env")


if __name__ == "__main__":
    main()