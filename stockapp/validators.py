import re
from django.core.exceptions import ValidationError

def validate_password_strength(value):
    """
    Valide que le mot de passe :
    - fait au moins 8 caractères
    - contient au moins une lettre
    - contient au moins un chiffre
    - contient au moins un symbole
    """
    if len(value) < 8:
        raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

    if not re.search(r"[A-Za-z]", value):
        raise ValidationError("Le mot de passe doit contenir au moins une lettre.")

    if not re.search(r"\d", value):
        raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")

    if not re.search(r"[^A-Za-z0-9]", value):
        raise ValidationError("Le mot de passe doit contenir au moins un symbole.")
