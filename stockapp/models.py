from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# ===== DEPOT =====
class Depot(models.Model):
    code_depot = models.CharField(max_length=20, unique=True)
    etat = models.BooleanField(default=True)
    is_siege = models.BooleanField(default=False)  # ✅ True pour le dépôt principal (siège)
    libelle = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return f"{self.libelle} ({self.code_depot})"


# ===== AGENCE =====
class Agence(models.Model):
    code_agence = models.CharField(max_length=20, unique=True, default='unknown')
    libelle = models.CharField(max_length=100)

    # ✅ Chaque agence est liée à un seul dépôt
    depot = models.OneToOneField(
        Depot,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='agence'
    )

    def __str__(self):
        return f"{self.libelle} ({self.code_agence})"


# ===== GESTION UTILISATEUR =====
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not extra_fields.get('matricule'):
            raise ValueError('Le matricule est obligatoire')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('matricule'):
            extra_fields['matricule'] = 'admin-default'
        return self.create_user(username, email, password, **extra_fields)


# ===== UTILISATEUR =====
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False)
    email = models.EmailField(unique=True)
    matricule = models.CharField(max_length=50, unique=True)

    agence = models.ForeignKey(
        Agence,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'matricule', 'agence']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ===== PRODUIT =====
class Produit(models.Model):
    CATEGORIES_CHOICES = [
        ('informatique', 'Informatique'),
        ('bureautique', 'Bureautique'),
        ('mobilier', 'Mobilier'),
    ]

    nom = models.CharField(max_length=100, unique=True)
    categorie = models.CharField(max_length=100, choices=CATEGORIES_CHOICES)
    quantite = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nom} ({self.categorie})"


# ===== STOCK =====
class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE)  # ✅ depot obligatoire
    quantite = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.produit.nom} - {self.depot.libelle} : {self.quantite}"


# ===== DEMANDE DE STOCK =====
class DemandeStock(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('transferee', 'Transférée'),
        ('traitee', 'Traitée'),  # Ajouter si absent
    ]

    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE)
    quantite_demandee = models.PositiveIntegerField()
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif_refus = models.TextField(blank=True, null=True)

    vue_par_utilisateur = models.BooleanField(default=False)
    vue_par_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"Demande de {self.utilisateur.username} - {self.produit.nom} ({self.quantite_demandee})"
