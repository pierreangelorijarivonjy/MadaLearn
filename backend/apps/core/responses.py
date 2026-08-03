from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status


def custom_response(data=None, message="Operation successful", success=True, status_code=status.HTTP_200_OK):
    """
    Génère une réponse HTTP au format JSON standardisé MadaLearn :
    {
        "success": bool,
        "message": str,
        "data": dict/list/null
    }
    """
    return Response(
        {
            "success": success,
            "message": message,
            "data": data if data is not None else {}
        },
        status=status_code
    )


class StandardJSONRenderer(JSONRenderer):
    """
    Renderer DRF personnalisé qui enveloppe automatiquement les réponses dans la structure standard :
    {
        "success": bool,
        "message": str,
        "data": dict/list/null
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        # Si les données sont déjà formatées avec la structure standard (success, message, data)
        if isinstance(data, dict) and 'success' in data and 'message' in data and 'data' in data:
            return super().render(data, accepted_media_type, renderer_context)

        # Déterminer si le statut est un succès (2xx)
        is_success = 200 <= status_code < 300
        default_message = "Operation successful" if is_success else "An error occurred"

        # Traitement spécifique en cas d'erreurs (ex: validation errors ou exception)
        message = default_message
        payload = data

        if not is_success:
            if isinstance(data, dict):
                if 'detail' in data:
                    message = str(data['detail'])
                    payload = {k: v for k, v in data.items() if k != 'detail'}
                elif 'message' in data:
                    message = str(data['message'])
                    payload = {k: v for k, v in data.items() if k != 'message'}

        formatted_response = {
            "success": is_success,
            "message": message,
            "data": payload if payload is not None else {}
        }

        return super().render(formatted_response, accepted_media_type, renderer_context)
