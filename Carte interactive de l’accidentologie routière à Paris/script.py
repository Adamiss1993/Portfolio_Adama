Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> # Carte interactive en clusters à partir d’un shapefile téléversé (EPSG:2154 → WGS84)
... # Environnement : Google Colab
... 
... import geopandas as gpd
... import folium
... from folium.plugins import MarkerCluster
... import os
... 
... # 1) Vérifier les fichiers présents dans le répertoire courant
... print(os.listdir())
... 
... # 2) Charger le shapefile (tous les fichiers .shp/.shx/.dbf/.prj doivent être présents)
... # Fix: Specify encoding to handle UnicodeDecodeError
... gdf_accidents = gpd.read_file('Accidentologie.shp', encoding='latin1')
... 
... # 3) Vérifier / définir le système de projection source (Lambert-93 : EPSG:2154)
... if gdf_accidents.crs is None:
...     gdf_accidents = gdf_accidents.set_crs(epsg=2154)
... 
... # 4) Reprojeter en WGS84 (EPSG:4326) pour l’affichage web
... gdf_accidents = gdf_accidents.to_crs(epsg=4326)
... 
... # 5) Créer la carte interactive (centrée sur Paris)
... m = folium.Map(
...     location=[48.8566, 2.3522],
...     zoom_start=11,
...     tiles='OpenStreetMap'
... )
... 
... # 6) Créer le cluster de points
... marker_cluster = MarkerCluster().add_to(m)
... 
... # 7) Ajouter les accidents au cluster
... for _, row in gdf_accidents.iterrows():
...     if row.geometry is not None:
        # Fix: Use row.geometry.y for latitude and row.geometry.x for longitude
        # Folium Marker expects location as [latitude, longitude]
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup="Accident"
        ).add_to(marker_cluster)

# 8) Afficher la carte
m
# Sauvegarder la carte en HTML
m.save("carte_accidents_paris.html")
from google.colab import files
files.download("carte_accidents_paris.html")

print(gdf_accidents.columns)



