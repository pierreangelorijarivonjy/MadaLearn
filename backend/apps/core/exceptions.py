from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions global qui intercepte les erreurs DRF
    et retourne la structure standard { "success": false, "message": "...", "data": {} }.
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"
        data = response.data

        if isinstance(data, dict):
            if 'detail' in data:
                message = str(data['detail'])
                # If detail is the only key, data becomes empty dict or remaining errors
                remaining = {k: v for k, v in data.items() if k != 'detail'}
                data = remaining if remaining else {}
            elif len(data) > 0:
                message = "Validation error"

        elif isinstance(data, list):
            message = "Validation error"

        response.data = {
            "success": False,
            "message": message,
            "data": data
        }
    else:
        # Non-DRF unhandled exceptions (500 Internal Server Error)
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        response = Response(
            {
                "success": False,
                "message": "Internal Server Error",
                "data": {"detail": str(exc)}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
