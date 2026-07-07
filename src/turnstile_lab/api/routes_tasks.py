from quart import Blueprint, current_app, jsonify, request

from turnstile_lab.api.schemas import (
    bad_request,
    consultation_error_response,
    consultation_ready_response,
    processing_response,
    task_created_response,
    turnstile_ready_response,
    turnstile_error_response,
)
from turnstile_lab.utils.validators import validate_plate

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/turnstile")
async def create_turnstile_task():
    url = request.args.get("url")
    sitekey = request.args.get("sitekey")
    action = request.args.get("action")
    cdata = request.args.get("cdata")

    if not url or not sitekey:
        return jsonify(
            bad_request(
                error_code="ERROR_WRONG_PAGEURL",
                description="Both 'url' and 'sitekey' are required",
            )
        ), 200

    task_manager = current_app.config.get("TASK_MANAGER")

    if task_manager is None:
        return jsonify(
            bad_request(
                error_code="ERROR_SERVICE_UNAVAILABLE",
                description="Task manager not initialized",
            )
        ), 503

    task_id = await task_manager.create_turnstile_task(
        url=url,
        sitekey=sitekey,
        action=action,
        cdata=cdata,
    )

    return jsonify(task_created_response(task_id)), 200


@tasks_bp.get("/consultar")
async def create_sunarp_task():
    url = request.args.get("url")
    sitekey = request.args.get("sitekey")
    placa = request.args.get("placa")

    if not url or not sitekey or not placa:
        return jsonify(
            bad_request(
                error_code="ERROR_WRONG_PARAMETERS",
                description="'url', 'sitekey' and 'placa' are required",
            )
        ), 200

    is_valid, normalized_plate = validate_plate(placa)
    if not is_valid:
        return jsonify(
            bad_request(
                error_code="ERROR_WRONG_PARAMETERS",
                description="'placa' must be 5 to 8 alphanumeric characters",
            )
        ), 200

    task_manager = current_app.config.get("TASK_MANAGER")

    if task_manager is None:
        return jsonify(
            bad_request(
                error_code="ERROR_SERVICE_UNAVAILABLE",
                description="Task manager not initialized",
            )
        ), 503

    task_id = await task_manager.create_sunarp_task(
        url=url,
        placa=normalized_plate,
    )

    return jsonify(task_created_response(task_id)), 200


@tasks_bp.get("/result")
async def get_result():
    task_id = request.args.get("id")

    if not task_id:
        return jsonify(
            bad_request(
                error_code="ERROR_WRONG_CAPTCHA_ID",
                description="Invalid task ID",
            )
        ), 200

    task_manager = current_app.config.get("TASK_MANAGER")

    if task_manager is None:
        return jsonify(
            bad_request(
                error_code="ERROR_SERVICE_UNAVAILABLE",
                description="Task manager not initialized",
            )
        ), 503

    result = await task_manager.get_result(task_id)

    if not result:
        return jsonify(processing_response()), 200

    if not isinstance(result, dict):
        return jsonify(processing_response()), 200

    status = result.get("status")
    value = result.get("value")

    if status in {"PROCESSING", "CAPTCHA_NOT_READY"}:
        return jsonify(processing_response()), 200

    if status == "ready" and "image" in result:
        return jsonify(
            consultation_ready_response(
                image=result.get("image"),
                placa=result.get("placa"),
            )
        ), 200

    if value == "CAPTCHA_FAIL":
        return jsonify(
            turnstile_error_response(
                error_code="ERROR_CAPTCHA_UNSOLVABLE",
                description="Could not solve the Captcha",
            )
        ), 200

    if value:
        return jsonify(turnstile_ready_response(value)), 200

    if status == "error":
        return jsonify(
            consultation_error_response(
                message=result.get("error", "Task failed"),
            )
        ), 200

    return jsonify(processing_response()), 200
