"""
Passage par valeur / Passage par reference. 
	=> Rapport à la présence de buffer sur les signaux passés en paramètre.
	=> Que pour le TOP.
	=> Concerne l'interface avec l'extérieur.
	
Génération de signaux de contrôle par la synthèse : synthèse d'interface.
	Types d'interface:
		> DataValid généré avec le signal spécifié
		> Req + Ack généré avec le signal spécifié
		
Stalling the Pipeline :
	> Pipelning the main loop when using handshaking IO can prevent the pipeline from flushing.
Manually Flushing the Pipeline :
	> by explicitly coding the acknowledge into the C++ interface. 
	
	
[IO Merging] => Big issue
Conditionally reading arrays mapped to IO inside of unrolled loops has the potential to prevent pipelining. Make the IO reads unconditional when possible by reading the entire array into an internal array.
	
"""


