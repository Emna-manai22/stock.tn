# stockapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm

CustomUser = get_user_model()


# ========= LOGIN VIEW ===========

class CustomLoginView(LoginView):
    template_name = 'stockapp/login.html'

    def get_success_url(self):
        return reverse_lazy('role_redirect')

    def form_invalid(self, form):
        username = form.data.get('username')
        if username and not CustomUser.objects.filter(username=username).exists():
            messages.error(
                self.request,
                "Ce compte n'existe pas. Veuillez créer un compte d'abord."
            )
        else:
            messages.error(
                self.request,
                "Identifiants incorrects. Veuillez réessayer."
            )
        return super().form_invalid(form)


# ========= REGISTER VIEW ===========

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('role_redirect')
        else:
            print(form.errors)
            messages.error(request, "Une erreur est survenue lors de l'inscription.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'stockapp/register.html', {'form': form})


# ========= ROLE REDIRECT ===========

@login_required
def role_redirect(request):
    user = request.user

    if user.is_superuser:
        # Admin Django → Dashboard admin
        return redirect('dashboard_admin')

    elif getattr(user, 'is_staff_app', False):
        # Ton staff interne → Dashboard superuser
        return redirect('dashboard_superuser')

    else:
        # Simple utilisateur
        return redirect('dashboard_user')


# ========= DASHBOARDS ===========

@user_passes_test(lambda u: u.is_authenticated and getattr(u, 'is_staff_app', False))
def dashboard_superuser(request):
    return render(request, 'stockapp/dashboard_superuser.html')


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def dashboard_admin(request):
    return render(request, 'stockapp/dashboard_admin.html')


@login_required
def dashboard_user(request):
    return render(request, 'stockapp/dashboard_user.html')
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def dashboard_admin(request):
    return render(request, 'stockapp/dashboard_admin.html')

@user_passes_test(is_superuser)
def gestion_utilisateurs(request):
    return render(request, 'stockapp/gestion_utilisateurs.html')

@user_passes_test(is_superuser)
def transfert_stock(request):
    return render(request, 'stockapp/transfert_stock.html')

@user_passes_test(is_superuser)
def ajouter_produit(request):
    return render(request, 'stockapp/ajouter_produit.html')

@user_passes_test(is_superuser)
def historique_demandes(request):
    return render(request, 'stockapp/historique_demandes.html')

@user_passes_test(is_superuser)
def gestion_stock(request):
    return render(request, 'stockapp/gestion_stock.html')
# stockapp/views.py

# stockapp/views.py

from django.shortcuts import render, redirect
from .forms import ProduitForm

def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = ProduitForm()
    return render(request, 'stockapp/ajouter_produit.html', {'form': form})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit
from .forms import ProduitForm

def gestion_stock(request):
    produits = Produit.objects.all()
    return render(request, 'stockapp/gestion_stock.html', {'produits': produits})

def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        produit.delete()
        return redirect('gestion_stock')
    return render(request, 'stockapp/supprimer_produit.html', {'produit': produit})

def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('gestion_stock')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'stockapp/modifier_produit.html', {'form': form})
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    request.session.flush()      # supprime TOUTES les données de session
    return redirect('login')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import DemandeStockForm

# views.py
from django.shortcuts import render, redirect
from .forms import DemandeStockForm

@login_required
def demander_produit(request):
    if request.method == 'POST':
        form = DemandeStockForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.utilisateur = request.user     # Liaison de l’utilisateur connecté
            demande.save()
            return redirect('dashboard_user')
    else:
        form = DemandeStockForm()

    return render(request, 'stockapp/demande_produit.html', {'form': form})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DemandeStock

@login_required
def historique_demandes(request):
    # Filtrer les demandes de l'utilisateur connecté
    demandes = DemandeStock.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'stockapp/historique_demandes.html', {'demandes': demandes})
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required  # accessible uniquement aux admins (is_staff=True)
def historique_demandes_admin(request):
    demandes = DemandeStock.objects.all().order_by('-date_creation')
    return render(request, 'stockapp/historique_demandes_admin.html', {'demandes': demandes})
