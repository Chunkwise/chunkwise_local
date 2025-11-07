import logging
import functools
import requests
from fastapi import HTTPException


def handle_endpoint_exceptions(func):
    """
    Decorator for FastAPI route handlers to centralize error translation
    from upstream request errors and validation errors into HTTPException.
    Works with sync and async handlers.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # await if result is awaitable
            if hasattr(result, "__await__"):
                result = await result
            return result

        except ValueError as exc:
            logging.exception("Invalid input in endpoint")
            raise HTTPException(status_code=400, detail="Invalid input") from exc

        except requests.RequestException as e:
            response = getattr(e, "response", None)
            logging.exception("Requests error when contacting upstream service")
            if response is not None:
                if response.status_code in (400, 401, 403, 404):
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Upstream service returned a client error",
                    ) from e
                else:
                    raise HTTPException(
                        status_code=502, detail="Upstream service error"
                    ) from e
            else:
                raise HTTPException(
                    status_code=503, detail="Unable to reach upstream service"
                ) from e

        except Exception as exc:
            logging.exception("Unhandled exception in endpoint")
            raise HTTPException(
                status_code=500, detail="Internal server error"
            ) from exc

    return wrapper
