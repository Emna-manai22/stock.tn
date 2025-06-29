# stockapp/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Agence, Depot, Produit, Stock, DemandeStock

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'matricule',
        'get_code_agence',   # ✅ colonne affichée
        'is_staff',
        'is_superuser'
    )

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('matricule', 'agence')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('matricule', 'agence')}),
    )

    def get_code_agence(self, obj):
        if obj.agence:
            return f"{obj.agence.code_agence} - {obj.agence.libelle}"
        return "-"
    get_code_agence.short_description = 'Code Agence'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Agence)
admin.site.register(Depot)
admin.site.register(Produit)
admin.site.register(Stock)
admin.site.register(DemandeStock)
