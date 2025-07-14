from stockapp.models import Depot, Produit, Stock

def synchroniser_stock_siege(qte_par_defaut=0):
    # 1. Récupérer ou créer le dépôt siège
    depot_siege, created = Depot.objects.get_or_create(
        is_siege=True,
        defaults={
            'code_depot': 'SIEGE',
            'libelle': 'Stock Central'
        }
    )
    if created:
        print(f"Dépôt siège créé : {depot_siege}")

    # 2. Pour chaque produit, créer une ligne de stock dans dépôt siège si elle n'existe pas
    produits = Produit.objects.all()
    created_count = 0
    for produit in produits:
        stock, stock_created = Stock.objects.get_or_create(
            produit=produit,
            depot=depot_siege,
            defaults={'quantite': qte_par_defaut}
        )
        if stock_created:
            created_count += 1
            print(f"Ligne Stock créée pour produit '{produit.nom}' avec quantité {qte_par_defaut}")

    print(f"Synchronisation terminée : {created_count} lignes de stock créées.")
