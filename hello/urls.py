
from django.urls import path , re_path, include
from django.views.generic import TemplateView 
from . import views
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required



urlpatterns = [
    re_path(r'^facture_detail/(?P<pk>\d+)/$', views.facture_detail_view, name='facture_detail'),
    re_path(r'^facture_table_detail/(?P<pk>\d+)/$', views.FactureDetailView.as_view(), name='facture_table_detail'),
    re_path(r'^facture_table_create/(?P<facture_pk>\d+)/$', views.LigneFactureCreateView.as_view(), name='facture_table_create'),
    re_path(r'^lignefacture_delete/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureDeleteView.as_view(), name='lignefacture_delete'),
    re_path(r'^lignefacture_update/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureUpdateView.as_view(), name='lignefacture_update'),
    re_path(r'^facture_update/(?P<pk>\d+)/$', views.FactureUpdate.as_view(), name='facture_update'),
    #URLs pour gérer les clients 
    path('clients/', views.ClientListView.as_view(), name='clients'),
    path('client_table_detail/<int:pk>/', views.ClientDetailView.as_view(), name='client_table_detail'),
    re_path(r'^client_table_create/$', views.ClientCreateView.as_view(), name='client_table_create'),
    re_path(r'^client_update/(?P<pk>\d+)/$', views.ClientUpdateView.as_view(), name='client_update'),
    re_path(r'^client_delete/(?P<pk>\d+)/$', views.ClientDeleteView.as_view(), name='client_delete'),
    re_path(r'^factures_client/(?P<pk>\d+)/$', views.FactureDetailView.as_view(), name='factures_client'),
    #URLs pour gérer les fournisseurs
    re_path(r'^fournisseur_table_detail/$', views.FournisseurDetailView.as_view(), name='fournisseur_table_detail'),
    re_path(r'^fournisseur_table_create/$', views.FournisseurCreateView.as_view(), name='fournisseur_table_create'),
    re_path(r'^fournisseur_delete/(?P<pk>\d+)/$', views.FournisseurDeleteView.as_view(), name='fournisseur_delete'),
    re_path(r'^fournisseur_update/(?P<pk>\d+)/$', views.FournisseurUpdateView.as_view(), name='fournisseur_update'),
    # gestion des factures
    re_path(r'^facture_client_create/(?P<client_pk>\d+)/$', views.FactureCreateView.as_view(), name='facture_client_create'),
    re_path(r'^facture_client_delete/(?P<pk>\d+)/(?P<client_pk>\d+)/$', views.FactureDeleteView.as_view(), name='facture_client_delete'),
    re_path(r'^facture_client_update/(?P<pk>\d+)/(?P<client_pk>\d+)/$', views.FactureUpdateView.as_view(), name='facture_client_update'), 
   # Dashboard 
    re_path(r'^dashboard/$', views.DashView.as_view(), name='dashboard'),
   # Auth 
    url(r'^$', views.home, name='home'),
    re_path(r'^signUp/$', views.register, name='register'),
    path('oauth/', include('social_django.urls', namespace='social')),  # <-- 

    # Gestion des paniers clients
    path('confirmer_panier/', views.confirme_panier_view, name='confirmer_panier'),
    path('commandes/', login_required(views.CommandeListView.as_view()), name='commandes'),
    #détail d'une commande 
    path('commande_table_detail/<int:pk>/', views.CommandeDetailView.as_view(), name='commande_table_detail'),
    path('valider_commande/<int:pk>/', views.valider_commande_view, name='valider_commande'),

    #Panier dun client
    path('panier/', views.panier_detail_view, name='panier'),
    #Ajout dun produit au panier
    path('add_produit_panier/<int:pk>/', views.ajouter_panier_view, name='add_produit_panier'),
    #afficher la liste des produits
    path('produits/', views.ProduitListView.as_view(), name='produits'),
    # creer un  produit
    path('produit_table_create/', views.ProduitCreateView.as_view(), name='produit_table_create'),
]
