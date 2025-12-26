# newsApp/exception_handler.py
import logging
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("app")


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler
    Logs all handled and unhandled API errors
    """

    response = drf_exception_handler(exc, context)

    view = context.get("view")
    request = context.get("request")

    if response is not None:
        # Handled DRF errors (400, 401, 403, etc.)
        logger.error(
            "Handled API exception",
            extra={
                "view": view.__class__.__name__ if view else None,
                "method": request.method if request else None,
                "path": request.path if request else None,
                "status_code": response.status_code,
                "error": str(exc),
            },
        )
        return response

    #  Unhandled errors (500)
    logger.exception(
        "Unhandled API exception",
        extra={
            "view": view.__class__.__name__ if view else None,
            "method": request.method if request else None,
            "path": request.path if request else None,
        },
    )

    return response
