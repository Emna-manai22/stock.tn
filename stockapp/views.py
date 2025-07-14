from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, ProduitForm, DemandeStockForm
from .models import Produit, DemandeStock

CustomUser = get_user_model()


# -------- LOGIN VIEW --------

class CustomLoginView(LoginView):
    template_name = 'stockapp/login_register.html'

    def get_success_url(self):
        # Redirection vers dashboard unique après login
        return reverse_lazy('role_redirect')

    def form_invalid(self, form):
        username = form.data.get('username')
        if username and not CustomUser.objects.filter(username=username).exists():
            messages.error(self.request, "Ce compte n'existe pas. Veuillez créer un compte d'abord.")
        else:
            messages.error(self.request, "Identifiants incorrects. Veuillez réessayer.")
        return super().form_invalid(form)


# -------- LOGIN / REGISTER VIEW --------

from django.contrib import messages


# views.py

def login_register_view(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    active_tab = 'login'   # Par défaut, on affiche l'onglet login

    if request.method == 'POST':
        if request.POST.get('form_type') == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('role_redirect')
            active_tab = 'login'
        elif request.POST.get('form_type') == 'register':
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                messages.success(request, "Compte créé avec succès. Connectez-vous.")
                return redirect('login')
            else:
                active_tab = 'register'

    return render(request, 'stockapp/login_register.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_tab': active_tab,
    })


# -------- ROLE REDIRECT --------

@login_required
def role_redirect(request):
    # Redirige TOUS vers le dashboard unique
    return redirect('dashboard')


# -------- DASHBOARD UNIQUE --------
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from stockapp.models import DemandeStock

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from stockapp.models import DemandeStock

@login_required
def dashboard(request):
    user = request.user

    user_role = None
    notif_count = 0
    demandes_en_attente = []
    demandes_notif = []

    if user.is_superuser:
        user_role = 'admin'
        demandes_en_attente = DemandeStock.objects.filter(statut='en_attente').order_by('-date_creation')
        notif_count = demandes_en_attente.count()

    elif user.is_staff:
        user_role = 'staff'
        demandes_en_attente = DemandeStock.objects.filter(
            statut='en_attente',
            agence=user.agence
        ).order_by('-date_creation')
        notif_count = demandes_en_attente.count()

    else:
        user_role = 'user'
        demandes_notif = DemandeStock.objects.filter(
            utilisateur=user,
            statut__in=['acceptee', 'refusee'],
            vue_par_utilisateur=False
        ).order_by('-date_creation')
        notif_count = demandes_notif.count()

    context = {
        'user_role': user_role,
        'notif_count': notif_count,
        'demandes_en_attente': demandes_en_attente,
        'demandes_notif': demandes_notif,
    }

    return render(request, 'stockapp/dashboard.html', context)


# -------- PRODUIT --------

@login_required
def stock_utilisateur(request):
    produits = Produit.objects.filter(utilisateur=request.user)  # adapte selon ton modèle
    return render(request, 'stockapp/stock_utilisateur.html', {'produits': produits})


# -------- DEMANDE PRODUIT --------
# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DemandeStockForm
from .models import Produit

# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DemandeStockForm
from .models import Produit, DemandeStock

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DemandeStockForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DemandeStockForm

@login_required
def demander_produit(request):
    if request.method == 'POST':
        form = DemandeStockForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            produit = demande.produit

            if demande.quantite_demandee <= 0:
                messages.error(request, "La quantité demandée doit être positive.")
                return redirect('demander_produit')

            if produit.quantite >= demande.quantite_demandee:
                produit.quantite -= demande.quantite_demandee
                produit.save()

                demande.utilisateur = request.user
                demande.agence = request.user.agence
                demande.vue_par_utilisateur = False
                demande.save()

                messages.success(request, "Votre demande a été enregistrée.")
                return redirect('dashboard')
            else:
                messages.error(request, "Stock insuffisant pour cette demande.")
                return redirect('demander_produit')
        else:
            messages.error(request, "Formulaire invalide. Vérifiez les champs.")
    else:
        form = DemandeStockForm()

    return render(request, 'stockapp/demande_produit.html', {'form': form})

from django.shortcuts import render
from .models import DemandeStock

@login_required
def historique_demandes(request):
    user = request.user

    demandes = DemandeStock.objects.filter(utilisateur=user).order_by('-date_creation')

    demandes_non_vues = demandes.filter(
        statut__in=['acceptee', 'refusee'],
        vue_par_utilisateur=False
    )

    # Marquer comme vues
    demandes_non_vues.update(vue_par_utilisateur=True)

    return render(request, 'stockapp/historique_demandes.html', {
        'demandes': demandes,
        'notif_count': demandes_non_vues.count(),
    })


# -------- VUES POUR SUPERUSER / STAFF --------

def is_superuser_or_staff(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'is_staff_app', False))



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DemandeStock

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DemandeStock


from django.shortcuts import render
from .models import DemandeStock

def consultation_depot(request):
    # Récupérer tous les dépôts actifs
    depots = Depot.objects.filter(etat=True)

    # Préparer un dict dépôt -> liste des stocks
    depot_stocks = {}
    for depot in depots:
        stocks = Stock.objects.filter(depot=depot)
        depot_stocks[depot] = stocks

    return render(request, 'stockapp/consultation_depot.html', {'depot_stocks': depot_stocks})


from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def historique_demandes_admin(request):
    # Récupérer toutes les demandes, ou juste celles en attente si tu préfères
    demandes = DemandeStock.objects.all().order_by('-date_creation')

    # Filtrer celles non vues par staff et en attente (ou tous statuts selon besoin)
    demandes_non_vues = demandes.filter(
        statut='en_attente',
        vue_par_staff=False
    )

    # Marquer comme vues
    demandes_non_vues.update(vue_par_staff=True)

    return render(request, 'stockapp/historique_demandes_admin.html', {
        'demandes': demandes,
        'notif_count_staff': demandes_non_vues.count(),
    })



# -------- VUES ADMIN UNIQUEMENT --------
# -------- VUES ADMIN UNIQUEMENT --------

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'stockapp/admin_user_list.html', {'users': users})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect('admin_user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'stockapp/admin_user_form.html', {'form': form, 'title': "Créer un utilisateur"})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def user_update(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect('admin_user_list')
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'stockapp/admin_user_form.html', {'form': form, 'title': "Modifier un utilisateur"})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès.")
        return redirect('admin_user_list')
    return render(request, 'stockapp/admin_user_confirm_delete.html', {'user': user})


from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from stockapp.models import DemandeStock, Stock, Depot  # adapte selon tes modèles

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def transfert_stock(request):
    # Récupérer les demandes acceptées
    demandes = DemandeStock.objects.filter(statut='acceptee').order_by('date_creation')
    return render(request, 'stockapp/transfert_stock.html', {'demandes': demandes})


from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProduitForm
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
@login_required
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, user=request.user)
        if form.is_valid():
            produit = form.save(commit=False)

            # Superuser → quantité du produit = 0
            if request.user.is_superuser:
                produit.quantite = 0

            # Staff → quantité globale du produit = somme des stocks créés
            produit.save()

            if request.user.is_staff:
                quantite_initiale = form.cleaned_data.get('quantite_initiale')
                if quantite_initiale is not None:
                    # Création du dépôt siège s’il n’existe pas
                    depot_siege, _ = Depot.objects.get_or_create(
                        is_siege=True,
                        defaults={'code_depot': 'SIEGE', 'libelle': 'Stock Central'}
                    )
                    # Créer ou mettre à jour la ligne de stock siège
                    stock_siege, created = Stock.objects.get_or_create(
                        produit=produit,
                        depot=depot_siege,
                        defaults={'quantite': quantite_initiale}
                    )
                    if not created:
                        stock_siege.quantite += quantite_initiale
                        stock_siege.save()

                    # mettre à jour la quantité globale dans Produit
                    produit.quantite = stock_siege.quantite
                    produit.save()

            messages.success(request, "Produit ajouté avec succès.")
            return redirect('dashboard')
    else:
        form = ProduitForm(user=request.user)

    return render(request, 'stockapp/ajouter_produit.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def gestion_stock(request):
    produits = Produit.objects.all()
    return render(request, 'stockapp/gestion_stock.html', {'produits': produits})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('gestion_stock')
    return render(request, 'stockapp/supprimer_produit.html', {'produit': produit})


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect('gestion_stock')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'stockapp/modifier_produit.html', {'form': form})


# -------- LOGOUT --------

def custom_logout(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render
from .models import DemandeStock
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def historique_demandes_admin(request):
    demandes = DemandeStock.objects.all().order_by('date_creation')
    return render(request, 'stockapp/historique_demandes_admin.html', {
        'demandes': demandes
    })

from .forms import CustomUserCreationForm

def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role')

        if form.is_valid() and role:
            user = form.save(commit=False)

            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif role == 'superuser':
                user.is_staff = True
                user.is_superuser = False
            else:  # utilisateur
                user.is_staff = False
                user.is_superuser = False

            user.save()
            return redirect('admin_user_list')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'title': 'Ajouter un utilisateur'
    }
    return render(request, 'stockapp/user_create.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import DemandeStock



from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import DemandeStock

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DemandeStock

def is_superuser_or_staff(user):
    return user.is_superuser or user.groups.filter(name='staff').exists() or user.is_staff
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import DemandeStock

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def validation_demandes(request):
    demandes_en_attente = DemandeStock.objects.filter(statut='en_attente').order_by('date_creation')
    return render(request, 'stockapp/validation_demandes.html', {
        'demandes_en_attente': demandes_en_attente
    })

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def accepter_demande(request, demande_id):
    demande = get_object_or_404(DemandeStock, id=demande_id)
    if request.method == 'POST':
        demande.statut = 'acceptee'  # attention à l'orthographe si tu utilises des choix
        demande.vue_par_staff = True  # marque comme vue par le staff/admin
        demande.vue_par_utilisateur = False  # notifie l'utilisateur qu'il y a une réponse
        demande.save()
        messages.success(request, "La demande a été acceptée.")
    return redirect('validation_demandes')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def refuser_demande(request, demande_id):
    demande = get_object_or_404(DemandeStock, id=demande_id)
    if request.method == 'POST':
        motif = request.POST.get('motif_refus', '')
        demande.statut = 'refusee'
        demande.motif_refus = motif
        demande.vue_par_staff = True  # idem, vue par staff
        demande.vue_par_utilisateur = False  # notifie utilisateur
        demande.save()
        messages.success(request, "La demande a été refusée.")
    return redirect('validation_demandes')

@login_required
def notifications_utilisateur(request):
    demandes = DemandeStock.objects.filter(
        utilisateur=request.user,
        statut__in=['acceptee', 'refusee'],
        vue_par_utilisateur=False
    )

    for demande in demandes:
        demande.vue_par_utilisateur = True
        demande.save()

    return render(request, 'stockapp/notifications_utilisateur.html', {
        'demandes': demandes
    })
# stockapp/views.py

@login_required
def marquer_notifications_utilisateur_lues(request):
    DemandeStock.objects.filter(
        utilisateur=request.user,
        statut__in=['acceptee', 'refusee'],
        vue_par_utilisateur=False
    ).update(vue_par_utilisateur=True)
    messages.success(request, "Notifications marquées comme lues.")
    return redirect('historique_demandes')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def marquer_notifications_staff_lues(request):
    DemandeStock.objects.filter(
        statut='en_attente',
        vue_par_staff=False
    ).update(vue_par_staff=True)
    messages.success(request, "Notifications marquées comme lues.")
    return redirect('historique_demandes_admin')


# stockapp/views.py
# stockapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from stockapp.models import DemandeStock, Stock, Depot, Agence

def liste_demandes_acceptees(request):
    demandes = DemandeStock.objects.filter(statut='acceptee')
    return render(request, 'stockapp/transfert_stock.html', {
        'demandes': demandes,
    })

# stockapp/views.py
# stockapp/views.py
# stockapp/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from stockapp.models import DemandeStock, Stock, Depot
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from stockapp.models import DemandeStock, Stock, Depot
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from stockapp.models import DemandeStock, Depot, Stock
# stockapp/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from stockapp.models import DemandeStock, Depot, Stock

def transferer_demande(request, demande_id):
    # Récupérer la demande
    demande = get_object_or_404(DemandeStock, id=demande_id, statut='acceptee')
    produit = demande.produit
    quantite = demande.quantite_demandee
    agence = demande.agence

    # 1. Vérifier que l’agence a bien un dépôt
    if agence.code_depot is None:
        messages.error(
            request,
            f"L'agence {agence.libelle} n'a pas de dépôt associé."
        )
        return redirect('transfert_stock')

    # 2. Récupérer le dépôt siège
    try:
        depot_siege = Depot.objects.get(is_siege=True)
    except Depot.DoesNotExist:
        messages.error(request, "Le dépôt siège n'est pas configuré.")
        return redirect('transfert_stock')

    # 3. Vérifier que le produit existe dans le stock siège
    try:
        stock_siege = Stock.objects.get(produit=produit, depot=depot_siege)
    except Stock.DoesNotExist:
        messages.error(
            request,
            f"Produit {produit.nom} introuvable dans le stock siège."
        )
        return redirect('transfert_stock')

    # 4. Vérifier la quantité disponible
    if stock_siege.quantite < quantite:
        messages.error(
            request,
            f"Quantité insuffisante dans le stock siège pour {produit.nom}."
        )
        return redirect('transfert_stock')

    # 5. Diminuer la quantité dans le stock siège
    stock_siege.quantite -= quantite
    stock_siege.save()

    # 6. Augmenter le stock dans le dépôt agence
    stock_agence, created = Stock.objects.get_or_create(
        produit=produit,
        depot=agence.code_depot,
        defaults={'quantite': 0}
    )
    stock_agence.quantite += quantite
    stock_agence.save()

    # 7. Supprimer la demande ou la marquer comme transférée
    demande.delete()
    # OU si tu souhaites garder la trace :
    # demande.statut = 'transfere'
    # demande.save()

    messages.success(
        request,
        f"Transfert de {quantite} {produit.nom} vers l'agence {agence.libelle} effectué avec succès."
    )
    return redirect('transfert_stock')
