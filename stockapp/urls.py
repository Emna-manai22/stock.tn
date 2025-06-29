from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_view, name='register'),

    # Redirection après login
    path('role-redirect/', views.role_redirect, name='role_redirect'),

    # Dashboards
    path('dashboard/superuser/', views.dashboard_superuser, name='dashboard_superuser'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),

    # Dashboard admin - sous pages
    path('dashboard/admin/utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('dashboard/admin/transfert-stock/', views.transfert_stock, name='transfert_stock'),
    path('dashboard/admin/ajouter-produit/', views.ajouter_produit, name='ajouter_produit'),
    path('dashboard/admin/historique-demandes/', views.historique_demandes, name='historique_demandes'),

    # Gestion stock avec modification et suppression
    path('dashboard/admin/gestion-stock/', views.gestion_stock, name='gestion_stock'),
    path('dashboard/admin/gestion-stock/modifier/<int:produit_id>/', views.modifier_produit, name='modifier_produit'),
    path('dashboard/admin/gestion-stock/supprimer/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
]
urlpatterns += [
    path('dashboard/user/demander-produit/', views.demander_produit, name='demander_produit'),
    path('historique-demandes/', views.historique_demandes, name='historique_demandes'),
path('admin/historique-demandes/', views.historique_demandes_admin, name='historique_demandes_admin'),

]
