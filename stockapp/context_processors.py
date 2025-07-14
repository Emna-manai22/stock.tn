# stockapp/context_processors.py

from .models import DemandeStock

def notification_context(request):
    """
    Context processor qui ajoute :
      - le rôle de l'utilisateur
      - les notifications staff (demandes non vues)
    """
    context = {}
    user = request.user

    if user.is_authenticated:
        # Détermination du rôle
        if user.is_superuser:
            role = 'admin'
        elif user.is_staff:
            role = 'staff'
        else:
            role = 'user'

        context['user_role'] = role

        # Notifications uniquement pour le staff
        if role == 'staff':
            demandes_non_vues = DemandeStock.objects.filter(
                statut='en_attente',
                vue_par_staff=False
            )
            context['demandes_non_vues_staff'] = demandes_non_vues

    return context
