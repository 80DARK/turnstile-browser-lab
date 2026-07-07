import time
import requests


BASE_URL = "http://127.0.0.1:5072"


def create_turnstile_task(url: str, sitekey: str, action: str | None = None, cdata: str | None = None) -> str:
    params = {
        "url": url,
        "sitekey": sitekey,
    }

    if action:
        params["action"] = action

    if cdata:
        params["cdata"] = cdata

    response = requests.get(f"{BASE_URL}/turnstile", params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("errorId") != 0:
        raise RuntimeError(f"Task creation failed: {data}")

    return data["taskId"]


def wait_for_result(task_id: str, timeout: int = 60, interval: float = 1.0) -> dict:
    started = time.time()

    while time.time() - started < timeout:
        response = requests.get(f"{BASE_URL}/result", params={"id": task_id}, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "processing":
            time.sleep(interval)
            continue

        return data

    raise TimeoutError("Timed out waiting for result")


def main():
    url = "https://example.com"
    sitekey = "YOUR_SITEKEY"

    print("Creating task...")
    task_id = create_turnstile_task(url=url, sitekey=sitekey)
    print("Task ID:", task_id)

    print("Waiting for result...")
    result = wait_for_result(task_id)

    if result.get("errorId") == 0 and result.get("status") == "ready":
        print("Token:", result["solution"]["token"])
    else:
        print("Error:", result)


if __name__ == "__main__":
    main()