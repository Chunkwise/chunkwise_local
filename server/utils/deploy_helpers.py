import json


def secret_name_for_instance(db_identifier: str):
    return f"/rds/{db_identifier}/master-credentials"


def sse_event(data: dict, event: str | None = None) -> str:
    payload = json.dumps(data, default=str)
    if event:
        return f"event: {event}\ndata: {payload}\n\n"
    return f"data: {payload}\n\n"
