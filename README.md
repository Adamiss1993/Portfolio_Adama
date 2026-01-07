# Portfolio_Adama: Contexte et choix du sujet

Ce projet a été réalisé dans le cadre d’un travail universitaire. Le sujet a été choisi volontairement afin de développer et de démontrer des compétences en conception et implémentation de bases de données relationnelles, appliquées à des données spatiales.
Le thème de l’accessibilité aux équipements au sein de Bordeaux Métropole a été retenu comme support d’étude. Les équipements considérés sont les collèges, écoles maternelles, pharmacies et médecins généralistes.

# Démarche méthodologique

La démarche méthodologique s’est articulée autour de la conception et de la mise en œuvre de la base de données :
•	Conception du Modèle Conceptuel de Données (MCD) et du Modèle Logique de Données (MLD) à l’aide du logiciel Looping ;
•	Définition des entités, des relations et des cardinalités ;
•	Implémentation du schéma relationnel dans PostgreSQL / PostGIS ;
•	Mise en place des clés primaires, des contraintes d’unicité et des contraintes d’intégrité référentielle ;
•	Création des index spatiaux afin d’optimiser les performances des requêtes géographiques ;
•	Structuration et préparation des données à l’aide de requêtes SQL.
Cette phase vise principalement à garantir la cohérence, la robustesse et l’efficacité de la base de données.


# Analyse (approche exploratoire)

L’analyse constitue une étape secondaire et exploratoire du projet. Elle a été initiée volontairement afin de tester et de valider le modèle de données, mais également pour se faire une première idée des enjeux liés à l’accessibilité aux équipements éducatifs et sanitaires.
Cette phase d’analyse repose sur :
•	la réalisation de requêtes spatiales et statistiques simples ;
•	l’exploration de l’accessibilité à différents types d’équipements, à savoir les collèges, écoles maternelles, pharmacies et médecins généralistes ;
•	la vérification du bon fonctionnement des relations entre les tables ainsi que de l’efficacité des index spatiaux.
Les résultats obtenus ne visent pas une interprétation approfondie des dynamiques territoriales. Ils servent avant tout à illustrer la capacité de la base de données à supporter des analyses spatiales et à confirmer la pertinence du modèle relationnel mis en place.


