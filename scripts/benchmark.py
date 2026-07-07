import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


BASE_URL = "http://127.0.0.1:5072"
TARGET_URL = "https://example.com"
SITEKEY = "YOUR_SITEKEY"

TOTAL_TASKS = 5
POLL_INTERVAL = 1.0
POLL_TIMEOUT = 60


def create_task():
    started = time.time()

    response = requests.get(
        f"{BASE_URL}/turnstile",
        params={
            "url": TARGET_URL,
            "sitekey": SITEKEY,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("errorId") != 0:
        raise RuntimeError(f"Task creation failed: {data}")

    return data["taskId"], time.time() - started


def wait_result(task_id: str):
    started = time.time()

    while time.time() - started < POLL_TIMEOUT:
        response = requests.get(
            f"{BASE_URL}/result",
            params={"id": task_id},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "processing":
            time.sleep(POLL_INTERVAL)
            continue

        return data, time.time() - started

    return {"status": "timeout"}, time.time() - started


def run_single(index: int):
    create_started = time.time()
    task_id, create_latency = create_task()
    result, solve_latency = wait_result(task_id)
    total_latency = time.time() - create_started

    success = result.get("errorId") == 0 and result.get("status") == "ready"

    return {
        "index": index,
        "task_id": task_id,
        "create_latency": round(create_latency, 3),
        "solve_latency": round(solve_latency, 3),
        "total_latency": round(total_latency, 3),
        "success": success,
        "result": result,
    }


def main():
    results = []

    with ThreadPoolExecutor(max_workers=TOTAL_TASKS) as executor:
        futures = [executor.submit(run_single, i + 1) for i in range(TOTAL_TASKS)]

        for future in as_completed(futures):
            item = future.result()
            results.append(item)

            status = "OK" if item["success"] else "FAIL"
            print(
                f"[{status}] task={item['task_id']} "
                f"create={item['create_latency']}s "
                f"solve={item['solve_latency']}s "
                f"total={item['total_latency']}s"
            )

    success_times = [r["total_latency"] for r in results if r["success"]]
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    print("\n=== Benchmark summary ===")
    print(f"Total tasks: {len(results)}")
    print(f"Success: {success_count}")
    print(f"Fail: {fail_count}")

    if success_times:
        print(f"Min total: {round(min(success_times), 3)}s")
        print(f"Max total: {round(max(success_times), 3)}s")
        print(f"Avg total: {round(statistics.mean(success_times), 3)}s")
        if len(success_times) > 1:
            print(f"Median total: {round(statistics.median(success_times), 3)}s")


if __name__ == "__main__":
    main()