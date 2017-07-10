
"""
Allocation de ressources : association opérateur / composant matériel (non instancié)

	Factorisation d'opérateurs:
		Si opérateur à nombre d'arguments variable :
			Si contraintes de ressources large :
				> type accumulation
			Sinon
				> type partage du temps
		Sinon
			Si contraintes de ressources large :
				> multiplication du nombre d'opérateur
			Sinon
				> type partage du temps
				
				
Interval d'initialisation : nombre de cycle d'horloge à attendre entre deux cycle d'ordonnancement (1 pour pipeline maximum). C'est la contrainte de pipelining !

---------------------------------------------
Partage des resources en cas d'exclusion mutuelle. 
	> If, elif, else avec le même opérateur.
	> return après chaque condition
---------------------------------------------


"""
