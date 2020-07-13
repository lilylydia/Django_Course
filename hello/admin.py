from django.contrib import admin
from hello.models import Client, Produit, Facture, LigneFacture, Fournisseur, Categorie, Admin, User, Commande, LigneCommande 

# Register your models here.
admin.site.register(User)
admin.site.register(Admin)    
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Produit)
admin.site.register(LigneFacture)
admin.site.register(Fournisseur)
admin.site.register(Categorie)
admin.site.register(Commande)
admin.site.register(LigneCommande)