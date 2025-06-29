# stockapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Agence

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    matricule = forms.CharField(max_length=50, required=True)
    agence = forms.ModelChoiceField(queryset=Agence.objects.all(), required=True)

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'matricule',
            'agence',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
# stockapp/forms.py
from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'quantite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
        }
from django import forms
from .models import DemandeStock, Produit, Agence

from django import forms
from .models import DemandeStock

class DemandeStockForm(forms.ModelForm):
    class Meta:
        model = DemandeStock
        fields = ['produit', 'agence', 'quantite_demandee']
        widgets = {
            'quantite_demandee': forms.NumberInput(attrs={'min': 1}),
        }
