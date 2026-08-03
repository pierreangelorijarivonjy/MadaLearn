import os
from django.core.exceptions import ValidationError


def validate_file_size(file_obj, max_size_mb=10):
    """
    Valide que la taille d'un fichier ne dépasse pas max_size_mb (en Méga-octets).
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        raise ValidationError(f"La taille du fichier ne doit pas dépasser {max_size_mb} Mo.")


def validate_image_file(file_obj):
    """
    Valide que le fichier téléversé est une image autorisée (JPG, PNG, WEBP) et <= 5 Mo.
    """
    validate_file_size(file_obj, max_size_mb=5)
    ext = os.path.splitext(file_obj.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(f"Format d'image non supporté. Formats acceptés : {', '.join(valid_extensions)}")


def validate_document_file(file_obj):
    """
    Valide que le fichier téléversé est un document pédagogique autorisé (PDF, EPUB, DOCX, PPTX) et <= 50 Mo.
    """
    validate_file_size(file_obj, max_size_mb=50)
    ext = os.path.splitext(file_obj.name)[1].lower()
    valid_extensions = ['.pdf', '.epub', '.docx', '.pptx', '.txt']
    if ext not in valid_extensions:
        raise ValidationError(f"Format de document non supporté. Formats acceptés : {', '.join(valid_extensions)}")
