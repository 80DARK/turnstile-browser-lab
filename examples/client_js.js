const BASE_URL = "http://127.0.0.1:5072";

async function createTurnstileTask(url, sitekey, action = null, cdata = null) {
  const params = new URLSearchParams({ url, sitekey });

  if (action) params.set("action", action);
  if (cdata) params.set("cdata", cdata);

  const response = await fetch(`${BASE_URL}/turnstile?${params.toString()}`);
  const data = await response.json();

  if (data.errorId !== 0) {
    throw new Error(`Task creation failed: ${JSON.stringify(data)}`);
  }

  return data.taskId;
}

async function waitForResult(taskId, timeoutMs = 60000, intervalMs = 1000) {
  const started = Date.now();

  while (Date.now() - started < timeoutMs) {
    const response = await fetch(`${BASE_URL}/result?id=${encodeURIComponent(taskId)}`);
    const data = await response.json();

    if (data.status === "processing") {
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
      continue;
    }

    return data;
  }

  throw new Error("Timed out waiting for result");
}

async function main() {
  const url = "https://example.com";
  const sitekey = "YOUR_SITEKEY";

  console.log("Creating task...");
  const taskId = await createTurnstileTask(url, sitekey);
  console.log("Task ID:", taskId);

  console.log("Waiting for result...");
  const result = await waitForResult(taskId);

  if (result.errorId === 0 && result.status === "ready") {
    console.log("Token:", result.solution.token);
  } else {
    console.error("Error:", result);
  }
}

main().catch(console.error);