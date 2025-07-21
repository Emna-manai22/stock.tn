# stockapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.login_register_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Redirection après login
    path('role-redirect/', views.role_redirect, name='role_redirect'),

    # Dashboard unique
    path('dashboard/', views.dashboard, name='dashboard'),

    # Gestion utilisateurs CRUD (Admin uniquement)
    path('admin/users/', views.user_list, name='admin_user_list'),
    path('admin/users/create/', views.user_create, name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.user_update, name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.user_delete, name='admin_user_delete'),

    # Pages admin spécifiques
    path('admin/transfert-stock/', views.transfert_stock, name='transfert_stock'),
    path('admin/ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('admin/historique-demandes/', views.historique_demandes_admin, name='historique_demandes_admin'),
    path('admin/gestion-stock/', views.gestion_stock, name='gestion_stock'),
    path('admin/gestion-stock/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('admin/gestion-stock/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),

    # Validation ou refus de demande (Admin ou staff)
    path('validation_demandes/', views.validation_demandes, name='validation_demandes'),
    path('validation_demandes/<int:demande_id>/accepter/', views.accepter_demande, name='accepter_demande'),
    path('validation_demandes/<int:demande_id>/refuser/', views.refuser_demande, name='refuser_demande'),

    # Pages staff ou superuser
    path('consultation-depot/', views.consultation_depot, name='consultation_depot'),

    # Pages utilisateur
    path('stock-utilisateur/', views.stock_utilisateur, name='stock_utilisateur'),
    path('demander-produit/', views.demander_produit, name='demander_produit'),
    path('historique-demandes/', views.historique_demandes, name='historique_demandes'),
path('transfert-stock/', views.transfert_stock, name='transfert_stock'),
    path('transfert-stock/<int:demande_id>/', views.transferer_demande, name='transferer_demande'),
    path('generate-receipt-pdf/', views.generate_receipt_pdf, name='generate_receipt_pdf'),
    path('mes-produits/', views.mes_produits, name='mes_produits'),

]

