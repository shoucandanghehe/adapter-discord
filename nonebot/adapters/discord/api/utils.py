import json
from typing import Any, Literal, Union

from nonebot.compat import type_validate_python

from .model import (
    ExecuteWebhookParams,
    InteractionCallbackMessage,
    InteractionResponse,
    MessageSend,
)
from ..utils import model_dump


def parse_data(
    data: dict[str, Any], model_class: type[Union[MessageSend, ExecuteWebhookParams]]
) -> dict[Literal["files", "json"], Any]:
    model = type_validate_python(model_class, data)
    payload: dict[str, Any] = model_dump(model, exclude={"files"}, exclude_none=True)
    if model.files:
        multipart: dict[str, Any] = {}
        attachments: list[dict] = payload.pop("attachments", [])
        for index, file in enumerate(model.files):
            for attachment in attachments:
                if attachment["filename"] == file.filename:
                    attachment["id"] = index
                    break
            multipart[f"files[{index}]"] = (file.filename, file.content)
        if attachments:
            payload["attachments"] = attachments
        multipart["payload_json"] = (None, json.dumps(payload), "application/json")
        return {"files": multipart}
    else:
        return {"json": payload}


def parse_forum_thread_message(
    data: dict[str, Any],
) -> dict[Literal["files", "json"], Any]:
    model = type_validate_python(MessageSend, data)
    payload: dict[str, Any] = {}
    content: dict[str, Any] = model_dump(model, exclude={"files"}, exclude_none=True)
    if auto_archive_duration := data.pop("auto_archive_duration"):
        payload["auto_archive_duration"] = auto_archive_duration
    if rate_limit_per_user := data.pop("rate_limit_per_user"):
        payload["rate_limit_per_user"] = rate_limit_per_user
    if applied_tags := data.pop("applied_tags"):
        payload["applied_tags"] = applied_tags
    payload["message"] = content
    if model.files:
        multipart: dict[str, Any] = {"payload_json": None}
        attachments: list[dict] = payload.pop("attachments", [])
        for index, file in enumerate(model.files):
            for attachment in attachments:
                if attachment["filename"] == file.filename:
                    attachment["id"] = str(index)
                    break
            multipart[f"file[{index}]"] = (file.filename, file.content)
        if attachments:
            payload["attachments"] = attachments
        multipart["payload_json"] = (None, json.dumps(payload), "application/json")
        return {"files": multipart}
    else:
        return {"json": payload}


def parse_interaction_response(
    response: InteractionResponse,
) -> dict[Literal["files", "json"], Any]:
    payload: dict[str, Any] = model_dump(response, exclude_none=True)
    if response.data and isinstance(response.data, InteractionCallbackMessage):
        payload["data"] = model_dump(
            response.data, exclude={"files"}, exclude_none=True
        )
        if response.data.files:
            multipart: dict[str, Any] = {}
            attachments: list[dict] = payload["data"].pop("attachments", [])
            for index, file in enumerate(response.data.files):
                for attachment in attachments:
                    if attachment["filename"] == file.filename:
                        attachment["id"] = index
                        break
                multipart[f"files[{index}]"] = (file.filename, file.content)
            if attachments:
                payload["data"]["attachments"] = attachments
            multipart["payload_json"] = (
                None,
                json.dumps(payload),
                "application/json",
            )
            return {"files": multipart}
    return {"json": payload}
