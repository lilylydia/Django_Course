from django.shortcuts import render, get_object_or_404
from hello.models  import Facture , LigneFacture , Client, Fournisseur, Categorie, User, Admin, Commande, LigneCommande, Produit
from django.http import HttpResponse , JsonResponse
import django_tables2 as tables
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView 
from django.views.generic import  ListView
from django_tables2.config import RequestConfig
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Button
from django.urls import reverse
from django.db.models import Count, Sum, ExpressionWrapper, FloatField, F 
from django.db import models
from random import randint
from django.views.generic import View 
from bootstrap_datepicker_plus import DatePickerInput
from jchart import Chart
from jchart.config import Axes, DataSet, rgba
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.shortcuts import redirect , render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django_select2 import forms as s2forms
from django.contrib import messages


# Create your views here.

def facture_detail_view(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    context={}
    context['facture'] = facture
    return render(request, 'hello/facture_detail.html', context)

def dashboardView(request):
    
    """ view function for sales app """

    
    return render(request, 'hello/dashboard.html')


class FactureUpdate(UpdateView, SuccessMessageMixin):
    model = Facture
    fields = ['client', 'date']
    template_name = 'hello/update.html'
    success_message="Mise à jour de la facture effectuée"
    
    def get_form(self, form_class=None):
        messages.warning(self.request, "voulez-vous modifier cette facture")
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit','Modifier',css_class='btn-warning'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('pk')})
        return form


class LigneFactureTable(tables.Table):
    action= '<a href="{% url "lignefacture_update" pk=record.id facture_pk=record.facture.id %}" class="btn btn-warning">Modifier</a>\
            <a href="{% url "lignefacture_delete" pk=record.id facture_pk=record.facture.id %}" class="btn btn-danger">Supprimer</a>'
    edit   = tables.TemplateColumn(action)   
    class Meta:
        model = LigneFacture
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__designation','produit__id', 'produit__prix', 'qte' )


#################################Afficher les factures d'un client #########################################################################################

class FactureClientTable(tables.Table):
    action= '<a href="{% url "facture_client_update" pk=record.facture.id client_pk=record.facture.client.id %}" class="btn btn-warning">Modifier</a>\
             <a href="{% url "facture_client_delete" pk=record.facture.id client_pk=record.facture.client.id %}" class="btn btn-danger">Supprimer</a>'
    edit   = tables.TemplateColumn(action)  
    class Meta:
        model = LigneFacture 
        template_name = "django_tables2/bootstrap4.html"
        fields = ('facture__id','facture__date', 'facture__client__nom','facture__client__prenom','Total')

class FactureClientView(ListView):
        template_name = 'hello/facture_client_detail.html'
        model = LigneFacture
        slug_field = 'client_slug'
        def get_context_data(self,**kwargs):
            context = super(FactureClientView, self).get_context_data(**kwargs)
            table = FactureClientTable(LigneFacture.objects.all().annotate(Total=
            Sum(ExpressionWrapper(F('qte'), output_field=FloatField())*F('produit__prix'))))
            RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
            context['client'] = table
            return context
# affichage des facture dun seul client 
class FactureDetailView(DetailView):
    template_name = 'hello/facture_table_detail.html'
    model = Facture
    def get_context_data(self, **kwargs):
        context = super(FactureDetailView, self).get_context_data(**kwargs)
        table = FactureClientTable(LigneFacture.objects.annotate(Total=
            Sum(ExpressionWrapper(F('qte'), output_field=FloatField())*F('produit__prix'))).filter(facture=self.kwargs.get('pk')))
        
        RequestConfig(self.request, paginate={"per_page": 2}).configure(table)
        context['table'] = table
        return context
 #################################création d'une facture ########################################################################################
class FactureCreateView(CreateView):
    model = Facture
    template_name = 'hello/create.html'
    fields = ['client', 'date']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.fields['client']=forms.ModelChoiceField(queryset=Client.objects.filter(id=self.kwargs.get('client_pk')), initial=0)
        form.fields['date'].widget = DatePickerInput()
        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('factures_client', kwargs={'pk':self.kwargs.get('client_pk')})
        return form
 ################################# MAJ d'une facture #########################################################################################

class FactureUpdateView(UpdateView):
    model = Facture
    template_name = 'hello/update.html'
    fields = ['client', 'date']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
  
        form.fields['client']=forms.ModelChoiceField(queryset=Client.objects.filter(id=self.kwargs.get('client_pk')), initial=0)
        form.fields['date'].widget = DatePickerInput()
        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('factures_client', kwargs={'pk':self.kwargs.get('client_pk')})
        return form
 ################################# suppression d'une facture #########################################################################################
class FactureDeleteView(DeleteView):
    model = Facture
    template_name = 'hello/delete.html'
    
    def get_success_url(self):
        self.success_url = reverse('factures_client', kwargs={'pk':self.kwargs.get('client_pk')})


class ClientTable(tables.Table):
    action= '<a href="{% url "client_update" pk=record.id %}" class="btn btn-warning">Modifier</a>\
            <a href="{% url "client_delete" pk=record.id %}" class="btn btn-danger">Supprimer</a>\
            <a href="{% url "factures_client" pk=record.id %}" class="btn btn-danger">Factures</a>'
    edit   = tables.TemplateColumn(action) 
    
    class Meta:
        model = Client 
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom','prenom','adresse',
        'tel','sexe','chiffre_affaire')

class FournisseurTable(tables.Table):
    action= '<a href="{% url "fournisseur_update" pk=record.id %}" class="btn btn-warning">Modifier</a>\
            <a href="{% url "fournisseur_delete" pk=record.id %}" class="btn btn-danger">Supprimer</a>'
    edit   = tables.TemplateColumn(action) 
    
    class Meta:
        model = Fournisseur
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom','prenom','adresse','tel','sexe')

class DashTable(tables.Table):
    class Meta:
        model = Fournisseur
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__fournisseur__nom','produit__fournisseur__prenom','produit__fournisseur__adresse','produit__fournisseur__tel','produit__fournisseur__sexe','chiffre_affaire')

class ClientDashTable(tables.Table):
    class Meta:
        model = Client
        template_name = "django_tables2/bootstrap4.html"
        fields = ('facture__client__nom','facture__client__prenom','facture__client__adresse','facture__client__tel','facture__client__sexe','chiffre_affaire')

### Fonctions pour le  dashboard 
class DashView(ListView):
    template_name = 'hello/dashboard.html'
    model = LigneFacture
    slug_field = 'client_slug'
    def get_context_data(self,**kwargs):
        context = super(DashView, self).get_context_data(**kwargs)
        table = DashTable(LigneFacture.objects.all().values('produit__fournisseur__nom','produit__fournisseur__prenom','produit__fournisseur__adresse','produit__fournisseur__tel','produit__fournisseur__sexe').
        annotate(chiffre_affaire=Sum(ExpressionWrapper(F('qte'), output_field=FloatField())*F('produit__prix'))).order_by('-chiffre_affaire').reverse())
        RequestConfig(self.request, paginate={"per_page": 2}).configure(table)

        client = ClientDashTable(LigneFacture.objects.all().values('facture__client__nom','facture__client__prenom','facture__client__adresse','facture__client__tel','facture__client__sexe')
        .annotate(chiffre_affaire=
        Sum(ExpressionWrapper(F('qte'), output_field=FloatField())*F('produit__prix'))).order_by('-chiffre_affaire'))
        RequestConfig(self.request, paginate={"per_page": 2}).configure(client)
        
        context['fournisseurDash'] = table
        context['clientDash'] = client
       # context['linecharte']= LineChart()
       # context['radarchart'] = RadarChart()
            #Chiffre d'affaire par fournisseur
        fournisseurs = LigneFacture.objects.all().values('produit__fournisseur').annotate(chiffre=models.Sum(models.ExpressionWrapper(models.F('qte'),output_field=models.FloatField()) * models.F('produit__prix')),nom=models.F('produit__fournisseur__nom'),prenom=models.F('produit__fournisseur__prenom'))
        

        labels = []
        data = []

    #  Chiffre d'affaire par jour
        factures = Facture.objects.all().values('date').annotate(total=models.Sum(models.F("lignes__produit__prix") * models.F("lignes__qte"),output_field=models.FloatField()))    
        for f in factures:
            labels.append(str(f['date']))
            data.append(f['total'])
        context['labelsLine'] = labels
        context['dataLine'] = data

        labels = []
        data = []
    #Chiffre par categorie de produit 
        produits = LigneFacture.objects.all().values('produit__categorie').annotate(total=models.Sum(models.F("produit__prix") * models.F("qte"),output_field=models.FloatField()),Categorie=models.F("produit__categorie__categorie"))
        for f in produits:
            labels.append(f['Categorie'])
            data.append(f['total'])
        print(labels,data)
        context['labelsRadar'] = labels
        context['dataRadar'] = data

        return context

class FactureTable(tables.Table):
    #Total de la facture
    total = tables.Column("Total") # Any attr will do, dont mind it

    modifier = '<a href="{% url "facture_update" pk=record.id  %}" class="btn btn-warning">Modifier</a>'
    lignes =   '<a href="{% url "facture_table_detail" pk=record.id  %}" class="btn btn-info">Lignes</a>'
    edit   = tables.TemplateColumn(modifier) 
    Lignes   = tables.TemplateColumn(lignes)  

    class Meta:
        model = Facture
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date')
class ClientListView(PermissionRequiredMixin,ListView):
    template_name = 'hello/list.html'
    model = Client
    permission_required = 'hello.view_client'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        #Total chiffre d'affaire de chaque client
        clients = Client.objects.filter().annotate(chiffre_affaire=models.Sum(models.ExpressionWrapper(models.F('factures__lignes__qte'),output_field=models.FloatField()) * models.F('factures__lignes__produit__prix')))
        table = ClientTable(clients)
        RequestConfig(self.request, paginate={"per_page": 8}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/hello/client_table_create/"
        context['object'] = 'Client'
        context['title'] = 'La liste des clients :'

        return context
class ClientDetailView(DetailView):
    template_name = 'hello/list.html'
    model = Client
    
    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        
        table = FactureTable(Facture.objects.filter(client=self.kwargs.get('pk')).annotate(total=models.Sum(models.F("lignes__produit__prix") * models.F("lignes__qte"),output_field=models.FloatField())))
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/hello/facture_create/" + str(self.kwargs.get('pk')) + "/"
        context['object'] = 'Facture'
        context['title'] = 'La liste des factures du client ' + str(self.get_object())

        return context

class FournisseurDetailView(ListView):
    template_name = 'hello/fournisseur_table_detail.html'
    model = Fournisseur
    slug_field = 'client_slug'
    def get_context_data(self,**kwargs):
        context = super(FournisseurDetailView, self).get_context_data(**kwargs)
        table = FournisseurTable(Fournisseur.objects.all())
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['fournisseur'] = table
        return context

class LigneFactureCreateView(CreateView):
    model = LigneFacture
    template_name = 'hello/create.html'
    fields = ['facture', 'produit', 'qte']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture']=forms.ModelChoiceField(queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})
        return form

class ClientCreateView(CreateView):
    model = Client
    template_name = 'hello/create.html'
    fields = ['nom', 'prenom','adresse', 'tel', 'sexe']
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('client_table_detail')
        return form

class FournisseurCreateView(CreateView):
    model = Fournisseur
    template_name = 'hello/create.html'
    fields = ['nom', 'prenom','adresse','tel','sexe'],
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('fournisseur_table_detail')
        return form

class LigneFactureUpdateView(UpdateView):
    model = LigneFacture
    template_name = 'hello/update.html'
    fields = ['facture', 'produit', 'qte']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture']=forms.ModelChoiceField(queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})
        return form

class ClientUpdateView(PermissionRequiredMixin,SuccessMessageMixin, UpdateView):
    model = Client
    template_name = 'hello/update.html'
    fields = ['nom', 'prenom', 'adresse','tel', 'sexe']
    success_message = "Mise à jour des informations effectuée"
    permission_required = 'hello.update_client'
    
    def get_form(self, form_class=None):
        messages.warning(self.request, "Voulez-vous modifier vos informations")
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('client_table_detail')
        return form

class FournisseurUpdateView(UpdateView):
    model = Fournisseur
    template_name = 'hello/update.html'
    fields = ['nom', 'prenom','adresse','tel','sexe']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit','Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('fournisseur_table_detail')
        return form

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'hello/delete.html'
    
    def get_success_url(self):
        self.success_url = reverse('client_table_detail')

class FournisseurDeleteView(DeleteView):
    model = Fournisseur
    template_name = 'hello/delete.html'
    
    def get_success_url(self):
        self.success_url = reverse('fournisseur_table_detail')

class LigneFactureDeleteView(DeleteView):
    model = LigneFacture
    template_name = 'hello/delete.html'
    
    def get_success_url(self):
        self.success_url = reverse('facture_table_detail', kwargs={'pk':self.kwargs.get('facture_pk')})

        

# linge de l'évolution du chiffre d'affaire

class LineChart(Chart):
    chart_type = 'line'
    scales ={
        'xAxes':[Axes(type='time',position='bottom')],
    }

    def get_datasets(self, **kwargs):
        factures = Facture.objects.all().values('date').annotate(y=Sum(ExpressionWrapper(F('lignes__produit__prix')*F('lignes__qte'), output_field=FloatField())))
        data=factures.annotate(x=F('date')).values('x','y')        
        
        return [DataSet(
             type='line',
             label="Le Total de chaque facture",
             data=list(data)
        )] 



class RadarChart(Chart):
    chart_type = 'radar'
    labels = []
    data = []
    f = 0
    produits = LigneFacture.objects.all().values('produit__categorie').annotate(total=Sum(F("produit__prix") * F("qte"),output_field=models.FloatField()),Categorie=F("produit__categorie__categorie"))
    for f in produits:
          labels.append(f['Categorie'])
          data.append(f['total'])
          
    def get_labels(self):
        return self.labels

    def get_datasets(self, **kwargs):
        return [
                DataSet(label="le chiffre d'affaire réparti par catégorie de Produit",
                        color=(255, 99, 132),
                        data=self.data )
               ]
def some_view(request):
    return render(request, 'hello/chart.html', {
        'line_chart': LineChart(),
    })
#class SignUp

class SignUp(UserCreationForm):
    nom = forms.CharField(required=False)
    prenom = forms.CharField(required=False)
    email = forms.EmailField(help_text='write a valid email address')
    SEXE =(
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    adresse = forms.CharField(required=False)
    tel = forms.CharField(required=False)
    sexe = forms.ChoiceField(choices=SEXE)

    class Meta:
        model = User  
        fields = ('username','nom','prenom','adresse','tel','sexe','password1','password2','user_type')



def register(response):
    if response.method =='POST':
        form=SignUp(response.POST)
        if form.is_valid():
            user = form.save()
            sexe=form.cleaned_data.get('sexe')
            tel =form.cleaned_data.get('tel')
            adresse=form.cleaned_data.get('adresse')
            nom=form.cleaned_data.get('nom')
            prenom=form.cleaned_data.get('prenom')
            user_type=form.cleaned_data.get('user_type')

            if user_type==1:
                Client.objects.create(user=user,sexe=sexe,tel=tel,adresse=adresse,nom=nom,prenom=prenom)
                login(response,user,backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            elif user_type==2:
                Fournisseur.objects.create(user=user,sexe=sexe,tel=tel,adresse=adresse,nom=nom,prenom=prenom)
                login(response,user,backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                Admin.objects.create(user=user,sexe=sexe,tel=tel,adresse=adresse,nom=nom,prenom=prenom)
                login(response,user,backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
    else:
        form=SignUp()

    return render(response,"registration/sign_up.html", {"form":form})


@login_required
def home(request):
    return render(request, 'registration/home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

#Confirmer panier dun client
@login_required
def confirme_panier_view(request):

    if 'panier' in request.session and len(request.session['panier']) > 0:
        commande = Commande.objects.create(client=request.user.client)
        for pk,qte in request.session['panier'].items():
            produit = get_object_or_404(Produit, id=pk)
            LigneCommande.objects.create(produit=produit,qte=qte,commande=commande)
        request.session['panier'] = {}
        request.session.modified = True
    return HttpResponseRedirect(reverse('commandes'))

# Lister les commandes 
class CommandeTable(tables.Table):
    
    lignes = '<a href="{% url "commande_table_detail" pk=record.id %}" class="btn btn-info">Lignes</a>'
    Lignes   = tables.TemplateColumn(lignes) 

    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date', 'valide')

class CommandeTableAdmin(CommandeTable):

    valider = '<a href="{% url "valider_commande" pk=record.id %}" class="btn btn-info">Valider </a>'
    valider   = tables.TemplateColumn(valider) 
    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date', 'valide')

class CommandeListView(ListView):
    
    template_name = 'hello/commande.html'
    model = Commande
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        filter = {}
        if self.request.user.is_authenticated:
            if self.request.user.user_type == 1:
                filter['client'] = self.request.user.client
        commandes = Commande.objects.filter(**filter)

        if self.request.user.user_type == 0:
            table = CommandeTableAdmin(commandes)
        elif self.request.user.user_type == 1:
            table = CommandeTable(commandes)

        RequestConfig(self.request, paginate={"per_page": 8}).configure(table)
        context['table'] = table
        context['object'] = 'Commande'
        context['title'] = 'La liste des commandes :'
        return context
        
class LigneCommandeTable(tables.Table):
    class Meta:
        model = LigneCommande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__designation','produit__id', 'produit__prix', 'qte')

class CommandeDetailView(DetailView):
    template_name = 'hello/commande.html'
    model = Commande
    
    def get_context_data(self, **kwargs):
        context = super(CommandeDetailView, self).get_context_data(**kwargs)
        commande = Commande.objects.get(id=self.kwargs.get('pk'))
        table = LigneCommandeTable(LigneCommande.objects.filter(commande=commande))
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['table'] = table
        context['object'] = 'LigneCommande'
        context['title'] = 'La liste des produits de la commande : ' + str(self.get_object())

        return context

@login_required
def valider_commande_view(request, pk):
    try:
        commande = Commande.objects.filter(id=pk)
    except Commande.DoesNotExist:
        raise Http404
    if commande[0].valide == False:
        commande.update(valide = True)
        commande = commande[0]
        facture = Facture.objects.create(client=commande.client,commande=commande)
        for ligne in commande.lignes.all():
            LigneFacture.objects.create(produit=ligne.produit,qte=ligne.qte,facture=facture)

    return HttpResponseRedirect(reverse('commandes'))

class PanierTable(tables.Table):
    
    produit = tables.Column()
    qte = tables.Column()
    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit','qte')

@login_required
def panier_detail_view(request):
    panier = []
    context = {}
    
    if 'panier' in request.session:
        for pk,qte in request.session['panier'].items():
            produit = get_object_or_404(Produit, id=pk)
            panier.append({"produit":produit,"qte":qte})
    table = PanierTable(panier)
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    context['table'] = table
    return render(request, 'hello/panier.html', context)

#Ajouter un produit
class ProduitCreateView( PermissionRequiredMixin,CreateView):
    model = Produit
    template_name = 'hello/create.html'
    fields = '__all__'
    permission_required = 'hello.add_produit'
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit','Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('produits')
        return form

    def get_context_data(self, **kwargs):
        ctx = super(ProduitCreateView, self).get_context_data(**kwargs)
        ctx['object'] = 'Produit'
        ctx['title'] = "Ajout d'un Produit :"
        return ctx


#La liste des produits
class ProduitTable(tables.Table):
    add_panier =  '<a href="{% url "add_produit_panier" pk=record.id %}" class="btn btn-info">Ajouter</a>'
    photo =   '<img src="{{ record.photo.url }}" alt="produit" width="200" height="200">'
    photo   = tables.TemplateColumn(photo) 
    Panier   = tables.TemplateColumn(add_panier) 

    class Meta:
        model = Produit
        template_name = "django_tables2/bootstrap4.html"
        fields = ('designation','categorie', 'prix')
class ProduitListView(ListView):
    template_name = 'hello/list.html'
    model = Produit
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produits = Produit.objects.all()
        table = ProduitTable(produits)
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        # pform = ProduitForm()
        # context['pform'] = pform
        context['table'] = table
        #URL qui pointe sur la vue de création
        context['creation_url']  = "/hello/produit_table_create/"
        context['object'] = 'produit'
        context['title'] = 'La liste des produits :'
        return context

@login_required
def ajouter_panier_view(request, pk):
    context={}
    if request.method == 'GET':
        #afficher le détail du produit et un input pr saisir la quantité du produit à rajouter
        # au panier
        produit = get_object_or_404(Produit, id=pk)
        context['produit'] = produit
        return render(request, 'hello/ajouter_produit_au_panier.html', context)
    elif request.method == 'POST':
        produit = get_object_or_404(Produit, id=pk)
        if 'qte' not in request.POST:
            qte = 1
        else:
            qte = int(request.POST['qte'])
            if qte < 0:
                qte = 1
        
        if 'panier' not in request.session:
            request.session['panier'] = {}
        request.session['panier'][int(pk)] = qte
        request.session.modified = True
        return HttpResponseRedirect(reverse('produits'))

