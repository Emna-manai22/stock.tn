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

def login_register_view(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        if request.POST.get('form_type') == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('role_redirect')
        elif request.POST.get('form_type') == 'register':
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                messages.success(request, "Compte créé avec succès. Connectez-vous.")
                return redirect('login')  # correspond au name='login' dans urls.py

    return render(request, 'stockapp/login_register.html', {
        'login_form': login_form,
        'register_form': register_form
    })


# -------- ROLE REDIRECT --------

@login_required
def role_redirect(request):
    # Redirige TOUS vers le dashboard unique
    return redirect('dashboard')


# -------- DASHBOARD UNIQUE --------

@login_required
def dashboard(request):
    user = request.user

    # Superuser → admin
    if user.is_superuser:
        user_role = 'admin'
    # Staff mais pas superuser
    elif user.is_staff:
        user_role = 'staff'
    else:
        user_role = 'user'

    context = {
        'user_role': user_role
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

def demander_produit(request):
    if request.method == 'POST':
        form = DemandeStockForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            produit = demande.produit

            # Décrémenter le stock
            produit.quantite -= demande.quantite_demandee
            produit.save()

            demande.utilisateur = request.user
            demande.agence = request.user.agence
            demande.save()

            messages.success(request, "Votre demande a été enregistrée avec succès.")
            return redirect('dashboard')
    else:
        form = DemandeStockForm()

    return render(request, 'stockapp/demande_produit.html', {'form': form})


@login_required
def historique_demandes(request):
    demandes = DemandeStock.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'stockapp/historique_demandes.html', {'demandes': demandes})


# -------- VUES POUR SUPERUSER / STAFF --------

def is_superuser_or_staff(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'is_staff_app', False))


@user_passes_test(is_superuser_or_staff)
def validation_demandes(request):
    demandes = DemandeStock.objects.filter(status='En attente')  # adapte selon ton modèle
    return render(request, 'stockapp/validation_demandes.html', {'demandes': demandes})


@user_passes_test(is_superuser_or_staff)
def consultation_depot(request):
    produits = Produit.objects.filter(depot='siege')  # adapte selon ton modèle
    return render(request, 'stockapp/consultation_depot.html', {'produits': produits})


@user_passes_test(is_superuser_or_staff)
def historique_demandes_admin(request):
    demandes = DemandeStock.objects.all().order_by('-date_creation')
    return render(request, 'stockapp/historique_demandes_admin.html', {'demandes': demandes})


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


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def transfert_stock(request):
    # Logic à compléter selon ton projet
    return render(request, 'stockapp/transfert_stock.html')


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

            # Si tu veux bloquer la quantité pour superuser :
            # if request.user.is_superuser:
            #     produit.quantite = 0

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

def historique_demandes_admin(request):
    demandes = DemandeStock.objects.all().order_by('date_creation')
    return render(request, 'stockapp/historique_demandes_admin.html', {'demandes': demandes})
from django.shortcuts import render, redirect
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
