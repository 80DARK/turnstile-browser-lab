from typing import Any, Optional


def bad_request(error_code: str, description: str) -> dict[str, Any]:
    return {
        "errorId": 1,
        "errorCode": error_code,
        "errorDescription": description,
    }


def task_created_response(task_id: str) -> dict[str, Any]:
    return {
        "errorId": 0,
        "taskId": task_id,
    }


def processing_response() -> dict[str, Any]:
    return {
        "status": "processing",
    }


def turnstile_ready_response(token: str) -> dict[str, Any]:
    return {
        "errorId": 0,
        "status": "ready",
        "solution": {
            "token": token,
        },
    }


def turnstile_error_response(error_code: str, description: str) -> dict[str, Any]:
    return {
        "errorId": 1,
        "errorCode": error_code,
        "errorDescription": description,
    }


def consultation_ready_response(image: str, placa: Optional[str] = None) -> dict[str, Any]:
    return {
        "status": "ready",
        "image": image,
        "placa": placa,
    }


def consultation_error_response(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "error": message,
    }