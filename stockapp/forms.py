# stockapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Agence, Produit, DemandeStock
import re

# ==========================
# FORMULAIRE UTILISATEUR
# ==========================

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    matricule = forms.CharField(max_length=50, required=True, label="Matricule")
    agence = forms.ModelChoiceField(
        queryset=Agence.objects.all(),
        required=True,
        label="Agence",
        empty_label="Sélectionnez une agence"
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'matricule',
            'agence',
            'password1',
            'password2',
        )
        labels = {
            'username': "Nom d'utilisateur",
            'first_name': "Prénom",
            'last_name': "Nom",
            'password1': "Mot de passe",
            'password2': "Confirmer le mot de passe",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name and not re.match(r'^[A-Za-zÀ-ÿ\s\-]+$', first_name):
            raise forms.ValidationError("Le prénom ne doit contenir que des lettres.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name and not re.match(r'^[A-Za-zÀ-ÿ\s\-]+$', last_name):
            raise forms.ValidationError("Le nom ne doit contenir que des lettres.")
        return last_name

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if password:
            if len(password) < 8:
                raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
            if not re.search(r"[A-Za-z]", password):
                raise ValidationError("Le mot de passe doit contenir au moins une lettre.")
            if not re.search(r"\d", password):
                raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
            if not re.search(r"[^A-Za-z0-9]", password):
                raise ValidationError("Le mot de passe doit contenir au moins un symbole.")

        return password

# ==========================
# FORMULAIRE PRODUIT
# ==========================

from django import forms
from .models import Produit
from django import forms
from .models import Produit
from django import forms
from .models import Produit
from django import forms
from .models import Produit
# stockapp/forms.py

from django import forms
from .models import Produit
# stockapp/forms.py
# forms.py

from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
        }
# forms.py (dans le même fichier)

class AjoutStockForm(forms.Form):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        label="Produit",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantite = forms.IntegerField(
        label="Quantité à ajouter",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

# ==========================
# FORMULAIRE DEMANDE STOCK
# ==========================

class DemandeStockForm(forms.ModelForm):
    class Meta:
        model = DemandeStock
        fields = ['produit', 'quantite_demandee']
        widgets = {
            'quantite_demandee': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite_demandee = cleaned_data.get('quantite_demandee')

        if produit and quantite_demandee:
            if quantite_demandee > produit.quantite:
                self.add_error(
                    'quantite_demandee',
                    f"La quantité demandée ({quantite_demandee}) dépasse le stock disponible ({produit.quantite})."
                )
        return cleaned_data
