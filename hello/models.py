from django.contrib.auth.models import  AbstractUser
from django.db import models
from django import utils
import datetime
from django.utils import timezone
from django import forms
from django.db.models import F, Sum
from django.urls import reverse


# Create your models here.

# class user
#The user can't assume multiple role (client or provider )

class User(AbstractUser):
    USER_TYPE_CHOICES= (
        (0, 'admin'),
        (1, 'client'),
        (2, 'fournisseur'),
    )
    email = models.EmailField(unique=True, null=False, blank=False)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['user_type','username']

class Admin(models.Model):
    SEXE =(
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length = 50, null=True, blank=True)
    prenom = models.CharField(max_length = 50, null=True, blank=True)
    adresse = models.CharField(max_length = 50, null=True, blank=True)
    tel = models.CharField(max_length = 50, null=True, blank=True)
    sexe = models.CharField(max_length = 1, choices = SEXE)


class Client(models.Model):
    SEXE = (
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50, null=True, blank=True)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    tel = models.CharField(max_length = 10, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices = SEXE)
    
    def __str__(self):
        return self.nom + ' ' + self.prenom

class Fournisseur(models.Model):
    SEXE = (
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50, null=True, blank=True)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    tel = models.CharField(max_length = 10, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices = SEXE)

class Categorie(models.Model):    
    CATEGORIE = (
        ('A','alimentation'),
        ('H','habillement'),
        ('M','meuble'),
        ('E','electromenager'),
        ('I','IT')
    )
    categorie = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.categorie

class Produit(models.Model):
    designation = models.CharField(max_length=50)
    prix = models.FloatField(default=0)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE,null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE,null=True)
    photo = models.ImageField(default=None)

    def __str__(self):
        return self.designation

class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    date = models.DateField(default=utils.timezone.now)
    valide = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('commande_detail', kwargs={'pk': self.id})

    def __str__(self):
        return str(self.client)+' : '+ str(self.date)
    
    def total(self):
        return self.lignes.all().aggregate(total=Sum(F("produit__prix") * F("qte"),output_field=models.FloatField()))


class LigneCommande(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE,related_name="lignes_commande")
    qte = models.IntegerField(default=1)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['produit', 'commande'], name="produit-commande")
        ]
    

class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE,related_name='factures')
    date = models.DateField(default=utils.timezone.now)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='facture')
    def get_absolute_url(self):
            return reverse('facture_detail', kwargs={'pk': self.id})

    def __str__(self):
        return str(self.client)+' : '+ str(self.date)
    
    def total(self):
        return self.lignes.all().aggregate(total=Sum(F("produit__prix") * F("qte"),output_field=models.FloatField()))

class LigneFacture(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    qte = models.IntegerField(default=1)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['produit', 'facture'], name="produit-facture")
        ]
        
    def prixFacture(self):
        return self.qte * self.produit.prix


