#!/usr/bin/env python
# coding: utf-8

# ## faire le CORRECTIF ENVIRONNEMENT PROJ/GDAL (À EXÉCUTER EN PREMIER)

# In[1]:


import os
import pyproj

os.environ["PROJ_LIB"] = pyproj.datadir.get_data_dir()
os.environ["PROJ_DATA"] = pyproj.datadir.get_data_dir()

print("PROJ_LIB utilisé :", os.environ["PROJ_LIB"])


# ## Charger les Librairies

# In[2]:


import osmnx as ox
import city2graph
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib.lines import Line2D
from shapely.geometry import box

city2graph.__version__


# ## Afficher les limites Administratives

# In[3]:


city_name = "Bordeaux metropole, France"
admin = ox.geocode_to_gdf(city_name)
admin.plot()


# ## Accessibilité aux équipements sportifs Aix

# In[4]:


#Récupération des équipements sportifs (gyms, centres sportifs) à Aix-en-Provence ---
city_name = "Bordeaux Métropole, France, France"
poi_gdf = ox.features_from_place(city_name, {"leisure": ["gym", "sports_centre"]}).to_crs(3944)
#Conversion des géométries en points (centroïdes) ---
poi_gdf["geometry"] = poi_gdf.geometry.centroid
#Nettoyage des données (suppression des géométries manquantes) ---
poi_gdf = poi_gdf.dropna(subset=["geometry"]).reset_index(drop=True)
#Aperçu du résultat ---
poi_gdf.head()


# ## Liste des grap

# In[5]:


dir(city2graph)


# ## FONCTION DE VISUALISATION - GRAPHE PIÉTON

# In[6]:


#Définition de la fonction d'affichage (graphe + limite administrative + fond de carte) ---
def plot_pub_graph(edges_gdf, nodes_gdf, admin_gdf, title, color="#00FFFF", alpha=0.5, linewidth=0.75):

    fig, ax = plt.subplots(figsize=(5, 5))

# Affichage de la limite administrative d'Aix-en-Provence ---
    admin_gdf.to_crs(epsg=3944).boundary.plot(ax=ax, color="white", linewidth=1.0, alpha=0.4)

 #Affichage des arêtes du graphe (réseau piéton) ---
    edges_gdf.to_crs(epsg=3944).plot(ax=ax, color=color, linewidth=linewidth, alpha=alpha)

 #Ajout du fond de carte sombre ---
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels)

    ax.set_axis_off()
    ax.set_title(title, fontsize=14, color="white", pad=12)
    plt.tight_layout()
    plt.show()


# ## GRAPHE À RAYON FIXE - ACCESSIBILITÉ AUX ÉQUIPEMENTS SPORTIFS

# In[7]:


import contextily as cx
import contextily as ctx
# --- Construction du graphe à rayon fixe (1000m) autour des POI d'Aix-en-Provence ---
radius = 1000
fixed_nodes, fixed_edges = city2graph.fixed_radius_graph(poi_gdf, radius=radius)

# --- Visualisation du graphe à rayon fixe sur fond de carte ---
plot_pub_graph(fixed_edges, poi_gdf, admin, "Fixed-radius Graph - Bordeaux Métropole", color="#00FFFF")


# In[8]:


import contextily as cx
import contextily as ctx
# --- Construction du graphe à rayon fixe (2500m) autour des POI d'Aix-en-Provence ---
radius = 2500
fixed_nodes, fixed_edges = city2graph.fixed_radius_graph(poi_gdf, radius=radius)

# --- Visualisation du graphe à rayon fixe sur fond de carte ---
plot_pub_graph(fixed_edges, poi_gdf, admin, "Fixed-radius Graph - Bordeaux Métropole", color="#00FFFF")


# ## CONSTRUCTION DU GRAPHE DE WAXMAN (DISTANCE MANHATTAN)

# In[9]:


#Construction du graphe de Waxman avec métrique de distance Manhattan ---
wax_l1_nodes, wax_l1_edges = city2graph.waxman_graph(
    poi_gdf,
    distance_metric="manhattan",
    r0=radius,
    beta=0.5
)


# ## VISUALISATION DU GRAPHE DE WAXMAN 

# In[10]:


# --- Affichage du graphe de Waxman sur fond de carte ---
plot_pub_graph(wax_l1_edges, poi_gdf, admin, "Waxman (Manhattan Distance) - Bordeaux Métropole", color="#FF6EFF")


# ## Pour la distance eucleidienne 

# In[11]:


#Construction du graphe de Waxman avec métrique de distance euclidienne ---
wax_l2_nodes, wax_l2_edges = city2graph.waxman_graph(
    poi_gdf,
    distance_metric="euclidean",
    r0=radius,
    beta=0.5
)


# In[12]:


#Affichage du graphe de Waxman sur fond de carte ---
plot_pub_graph(wax_l2_edges, poi_gdf, admin, "Waxman (Euclidean Distance) - Bordeaux Métropole", color="#00FF9F")


# ## La distance sur le reseau

# In[13]:


# --- Récupération des segments du réseau routier depuis OSM ---
segments_gdf = ox.graph_to_gdfs(ox.graph_from_place(city_name, network_type="drive"))[1].to_crs(3944)
len(segments_gdf)


# ## GRAPHE DE WAXMAN (DISTANCE RÉSEAU)

# In[14]:


# --- Vérification de la cohérence des CRS avant calcul ---
assert poi_gdf.crs == segments_gdf.crs, f"CRS mismatch: {poi_gdf.crs} != {segments_gdf.crs}"

# --- Construction du graphe de Waxman avec métrique de distance réseau ---
wax_net_nodes, wax_net_edges = city2graph.waxman_graph(
    poi_gdf,
    distance_metric="network",
    r0=radius,
    beta=0.5,
    network_gdf=segments_gdf
)


# ## VISUALISATION - GRAPHE DE WAXMAN (DISTANCE RÉSEAU)

# In[15]:


# --- Affichage du graphe de Waxman (distance réseau) sur fond de carte ---
plot_pub_graph(wax_net_edges, poi_gdf, admin, "Waxman (Network Distance) - Bordeaux Metropole", color="#FFA500")


# ## CONFIGURATION - VILLE, LIMITE ADMINISTRATIVE ET RÉSEAU ROUTIER

# In[16]:


# --- Définition de la ville et récupération de la limite administrative, reprojetée en CC44 ---
city_name = "Bordeaux Métropole, France"
admin = ox.geocode_to_gdf(city_name).to_crs(3944)

# --- Récupération des segments du réseau routier, reprojetés en CC44 ---
segments_gdf = ox.graph_to_gdfs(ox.graph_from_place(city_name, network_type="drive"))[1].to_crs(3944)


# ## DÉFINITION DES 4 CATÉGORIES Des Equipements

# In[17]:


# --- Requêtes OSM pour les 4 catégories de service (vie active, besoins quotidiens, vie sociale, santé) ---
poi_queries = {
    "Centres_Sport": {"leisure": ["gym", "sports_centre"]},
    "Supermaché": {"shop": ["supermarket", "convenience"]},
    "Restaurant": {"amenity": ["restaurant"]},
    "Service de santé": {"amenity": ["hospital", "clinic", "pharmacy"]}
}


# ## RÉCUPÉRATION DES 4  CATÉGORIES

# In[18]:


# --- Récupération, reprojection en CC44 et filtrage des POI de type point pour chaque catégorie ---
poi_layers = {}
for label, query in poi_queries.items():
    poi = ox.features_from_place(city_name, query).to_crs(3944)
    poi_layers[label] = poi[poi.geometry.type == "Point"]
    print(label, len(poi_layers[label]))


# ## GRAPHES DE WAXMAN PAR CATÉGORIE DE POI

# In[19]:


# --- Construction d'un graphe de Waxman (distance réseau) pour chaque catégorie de POI ---
wax_graphs = {}
radius = 1000
for label, gdf in poi_layers.items():
    if len(gdf) > 1:
        nodes, edges = city2graph.waxman_graph(
            gdf,
            distance_metric="network",
            r0=radius,
            beta=0.5,
            network_gdf=segments_gdf
        )
        wax_graphs[label] = edges


# In[20]:


#Nombre de catégories pour lesquelles un graphe a pu être construit ---
len(wax_graphs)


# ## COULEURS PAR CATÉGORIE DE POI 

# In[21]:


layer_colors = {
    "Centres_Sport": "#FF69B4",       # rose
    "Supermaché": "#FFFF00",          # jaune
    "Restaurant": "#00FFFF",          # cyan
    "Service de santé": "#00FF00"     # vert
}


# In[ ]:





# ## VISUALISATION GLOBALE - GRAPHES DE WAXMAN PAR CATÉGORIE

# In[23]:


# ============================================================
# TEST SANS FOND DE CARTE - ISOLER LA CAUSE DU BLOCAGE
# ============================================================

fig, ax = plt.subplots(figsize=(6, 6))

admin.to_crs(3857).boundary.plot(ax=ax, color="black", linewidth=0.8, zorder=5)

for label, edges in wax_graphs.items():
    edges_3857 = edges.to_crs(3857)
    for _, row in edges_3857.iterrows():
        x, y = row.geometry.xy
        ax.plot(x, y, color=layer_colors[label], linewidth=0.6, alpha=0.3, zorder=6)

for label, pois in poi_layers.items():
    pois.to_crs(3857).plot(ax=ax, markersize=5, color=layer_colors[label], alpha=0.8, zorder=7)

ax.set_title("Métropole de Bordeaux", fontsize=13, pad=12)
plt.tight_layout()
plt.show()


# In[59]:


print(list(poi_layers.keys()))


# ## VISUALISATION FINALE - CONNECTIVITÉ PIÉTONNE BORDEAUX MÉTROPOLE (Graphes de Waxman + POI + fond de carte)

# In[25]:


# ============================================================
# VISUALISATION FINALE - CONNECTIVITÉ PIÉTONNE BORDEAUX MÉTROPOLE
# (Graphes de Waxman + POI + fond de carte)
# ============================================================

import matplotlib.pyplot as plt
import contextily as ctx

fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor("black")

# --- 1. Limite administrative ---
admin.to_crs(3857).boundary.plot(ax=ax, color="white", linewidth=0.8, zorder=5)

# --- 2. Fond de carte (avec sécurité si le téléchargement échoue) ---
try:
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels, crs=3857, zoom=10)
except Exception as e:
    print("Fond de carte non chargé (on continue sans) :", e)

# --- 3. Graphes de Waxman (tracé vectorisé, pas de boucle iterrows) ---
for label, edges in wax_graphs.items():
    edges.to_crs(3857).plot(ax=ax, color=layer_colors[label], linewidth=0.6, alpha=0.3, zorder=6)

# --- 4. POI ---
for label, pois in poi_layers.items():
    pois.to_crs(3857).plot(ax=ax, markersize=5, color=layer_colors[label], alpha=0.8, zorder=7)

ax.set_axis_off()
ax.set_title(
    "Connectivité Piétonne aux Besoins Quotidiens à Bordeaux Métropole",
    fontsize=13, color="white", pad=12
)
plt.tight_layout()
plt.show()


# ## VISUALISATION GLOBALE - GRAPHES DE WAXMAN - Bordeaux Métropole

# In[78]:


from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor("black")  # <-- ajouté, essentiel pour la visibilité du titre blanc

admin.to_crs(3857).boundary.plot(ax=ax, color="white", linewidth=0.8, zorder=5)

for label, edges in wax_graphs.items():
    edges.to_crs(3857).plot(ax=ax, color=layer_colors[label], linewidth=0.6, alpha=0.3, zorder=6)

for label, pois in poi_layers.items():
    pois.to_crs(3857).plot(ax=ax, markersize=5, color=layer_colors[label], alpha=0.8, zorder=7)

ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels, zoom=10)
ax.set_axis_off()

legend_elements = [
    Line2D([0], [0], color=layer_colors[label], lw=3, label=label)
    for label in wax_graphs.keys()
]
ax.legend(
    handles=legend_elements,
    loc="upper left",
    bbox_to_anchor=(0.02, 0.98),
    frameon=True,
    framealpha=1,
    facecolor="black",
    edgecolor="black",
    fontsize=9,
    labelcolor="white",
    title="Bordeaux Métropole",
    title_fontproperties={"weight": "bold", "size": 10}
)

ax.set_title(
    "Connectivité Piétonne aux Besoins Quotidiens à Bordeaux Métropole",
    fontsize=13, color="white", pad=12
)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()


# ## DÉFINITION DE LA FONCTION - CONNECTIVITÉ URBAINE

# In[76]:


from matplotlib_scalebar.scalebar import ScaleBar

def plot_city_connectivity(city_name, admin, poi_layers, wax_graphs, radius):
    labels_fr = {
        "active_life": "Vie active",
        "daily_needs": "Besoins quotidiens",
        "social_life": "Vie sociale",
        "health_services": "Services de santé"
    }
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("black")
    admin.to_crs(3857).boundary.plot(ax=ax, color="white", linewidth=0.8, zorder=5)
    for label, edges in wax_graphs.items():
        edges.to_crs(3857).plot(ax=ax, color=layer_colors[label], linewidth=1.0, alpha=0.3, zorder=6)
    for label, pois in poi_layers.items():
        pois.to_crs(3857).plot(ax=ax, markersize=5, color=layer_colors[label], alpha=0.8, zorder=7)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels, zoom=10)
    ax.set_axis_off()

    # --- Légende ---
    legend_elements = [
        Line2D([0], [0], color=color, lw=3, label=labels_fr.get(label, label))
        for label, color in layer_colors.items() if label in wax_graphs
    ]
    ax.legend(
        handles=legend_elements,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
        framealpha=1,
        facecolor="black",
        edgecolor="black",
        fontsize=9,
        labelcolor="white",
        title="  " + city_name,
        title_fontproperties={"weight": "bold", "size": 10}
    )

    # --- Flèche du Nord ---
    ax.annotate(
    "N", xy=(0.98, 0.94), xytext=(0.98, 0.82),
    xycoords="axes fraction",
    arrowprops=dict(facecolor="white", edgecolor="white", width=4, headwidth=12),
    ha="center", va="center", fontsize=12, color="white", fontweight="bold", zorder=10
)


    # --- Échelle (en mètres, données en EPSG:3857) ---
    ax.add_artist(ScaleBar(
    dx=1, units="m", location="lower right",
    box_color="black", box_alpha=0.7, color="white",
    font_properties={"size": 8}, pad=0.3
))

    # --- Source des données ---
    fig.text(
    0.01, 0.07,
    "Source : OpenStreetMap, IGN\nRéalisation : Diané Adama",
    fontsize=7, color="lightgrey", ha="left", va="bottom"
)

    # --- Titres ---
    fig.suptitle(
        f"Accessibilité aux services essentiels: {city_name}",
        fontsize=15, color="white", fontweight="bold", y=0.98
    )
    ax.set_title(
        f"Waxman (Distance Réseau) — r={radius}m",
        fontsize=11, color="lightgrey", pad=10
    )
    plt.tight_layout()
    plt.show()


# ## APPEL 

# In[77]:


plot_city_connectivity("Bordeaux Métropole", admin, poi_layers, wax_graphs, radius)


# ## FONCTION - CONNECTIVITÉ URBAINE AVEC AUTO-ZOOM, MASQUE ET LÉGENDE 

# In[45]:


def plot_city_connectivity(city_name, admin, poi_layers, wax_graphs, radius):
    # --- Traduction des catégories pour l'affichage de la légende ---
    labels_fr = {
        "Centres_Sport": "Centres sportifs",
        "Supermaché": "Supermarchés",
        "Restaurant": "Restaurants",
        "Service de santé": "Services de santé"
    }

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("black")
    admin_3857 = admin.to_crs(3857)
    admin_3857.boundary.plot(ax=ax, color="dimgrey", linewidth=2.0, zorder=5, alpha=0.6)

    wax_graphs_3857 = {}
    for label in ["Centres_Sport", "Supermaché", "Restaurant", "Service de santé"]:
        edges = wax_graphs.get(label)
        if edges is None or edges.empty:
            continue
        edges_3857 = edges.to_crs(3857)
        wax_graphs_3857[label] = edges_3857
        color = layer_colors[label]
        edges_3857.plot(ax=ax, color=color, linewidth=0.6, alpha=0.3, zorder=6)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels, zoom=12)
    ax.set_axis_off()

    all_bounds = [gdf.total_bounds for gdf in wax_graphs_3857.values() if not gdf.empty]
    if all_bounds:
        minx = min(b[0] for b in all_bounds)
        miny = min(b[1] for b in all_bounds)
        maxx = max(b[2] for b in all_bounds)
        maxy = max(b[3] for b in all_bounds)
        buffer_x = (maxx - minx) * 0.05
        buffer_y = (maxy - miny) * 0.05
        zoom_minx = minx - buffer_x
        zoom_maxx = maxx + buffer_x
        zoom_miny = miny - buffer_y
        zoom_maxy = maxy + buffer_y

        outer_box = box(
            zoom_minx - buffer_x,
            zoom_miny - buffer_y,
            zoom_maxx + buffer_x,
            zoom_maxy + buffer_y
        )
        city_shape = admin_3857.geometry.unary_union
        mask_geom = outer_box.difference(city_shape)
        gpd.GeoSeries([mask_geom], crs=admin_3857.crs).plot(
            ax=ax, color="black", zorder=4
        )

    # --- Légende en français (uniquement les catégories non vides) ---
    legend_elements = [
        Line2D([0], [0], color=color, lw=3, label=labels_fr.get(label, label))
        for label, color in layer_colors.items() if label in wax_graphs_3857
    ]

    ax.legend(
        handles=legend_elements,
        loc="lower left",
        bbox_to_anchor=(0.02, -0.02),
        frameon=True,
        framealpha=1,
        facecolor="black",
        edgecolor="black",
        fontsize=9,
        labelcolor="white",
        title="  " + city_name.split(",")[0],
        title_fontproperties={"weight": "bold", "size": 10}
    )

    ax.set_title(
        f"Waxman (Distance Réseau) — Connectivité aux services essentiels à {city_name} (r={radius}m)",
        fontsize=13, color="white", pad=12
    )
    plt.tight_layout()
    plt.show()


# ## Appel

# In[46]:


plot_city_connectivity(city_name, admin, poi_layers, wax_graphs, radius)


# ## FONCTION - CONNECTIVITÉ URBAINE AVEC AUTO-ZOOM, MASQUE avec ZOOM

# In[79]:


def plot_city_connectivity(city_name, admin, poi_layers, wax_graphs, radius):

    # --- Traduction des catégories pour l'affichage de la légende ---
    labels_fr = {
        "Centres_Sport": "Centres sportifs",
        "Supermaché": "Supermarchés",
        "Restaurant": "Restaurants",
        "Service de santé": "Services de santé"
    }

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("black")

    admin_3857 = admin.to_crs(3857)
    admin_3857.boundary.plot(ax=ax, color="dimgrey", linewidth=2.0, zorder=5, alpha=0.6)

    wax_graphs_3857 = {}
    for label in ["Centres_Sport", "Supermaché", "Restaurant", "Service de santé"]:
        edges = wax_graphs.get(label)
        if edges is None or edges.empty:
            continue
        edges_3857 = edges.to_crs(3857)
        wax_graphs_3857[label] = edges_3857
        color = layer_colors[label]
        edges_3857.plot(ax=ax, color=color, linewidth=0.6, alpha=0.3, zorder=6)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.DarkMatterNoLabels, zoom=12)
    ax.set_axis_off()

    all_bounds = [gdf.total_bounds for gdf in wax_graphs_3857.values() if not gdf.empty]
    if all_bounds:
        minx = min(b[0] for b in all_bounds)
        miny = min(b[1] for b in all_bounds)
        maxx = max(b[2] for b in all_bounds)
        maxy = max(b[3] for b in all_bounds)

        buffer_x = (maxx - minx) * 0.05
        buffer_y = (maxy - miny) * 0.05

        zoom_minx = minx - buffer_x
        zoom_maxx = maxx + buffer_x
        zoom_miny = miny - buffer_y
        zoom_maxy = maxy + buffer_y

        outer_box = box(
            zoom_minx - buffer_x,
            zoom_miny - buffer_y,
            zoom_maxx + buffer_x,
            zoom_maxy + buffer_y
        )

        city_shape = admin_3857.geometry.unary_union
        mask_geom = outer_box.difference(city_shape)

        gpd.GeoSeries([mask_geom], crs=admin_3857.crs).plot(
            ax=ax, color="black", zorder=4
        )

    # --- Légende en français (uniquement les catégories non vides) ---
    legend_elements = [
        Line2D([0], [0], color=color, lw=3, label=labels_fr.get(label, label))
        for label, color in layer_colors.items() if label in wax_graphs_3857
    ]

    ax.legend(
        handles=legend_elements,
        loc="lower left",
        bbox_to_anchor=(0.02, -0.02),
        frameon=True,
        framealpha=1,
        facecolor="black",
        edgecolor="black",
        fontsize=9,
        labelcolor="white",
        title="  " + city_name.split(",")[0],
        title_fontproperties={"weight": "bold", "size": 10}
    )

    ax.set_title(
        f"Waxman (Distance Réseau) — Connectivité aux services essentiels à {city_name} (r={radius}m)",
        fontsize=13, color="white", pad=12
    )
    plt.tight_layout()
    plt.show()


# In[80]:


plot_city_connectivity(city_name, admin, poi_layers, wax_graphs, radius)


# In[81]:


get_ipython().run_line_magic('pip', 'install folium')


# In[82]:


import folium

# --- 1. Centrer la carte sur l'emprise de l'admin ---
admin_4326 = admin.to_crs(4326)  # Folium/Leaflet travaille en WGS84 (lat/lon)
centroid = admin_4326.geometry.unary_union.centroid
m = folium.Map(
    location=[centroid.y, centroid.x],
    zoom_start=12,
    tiles="CartoDB dark_matter"  # équivalent Leaflet du fond sombre que tu utilises
)

# --- 2. Limite administrative ---
folium.GeoJson(
    admin_4326,
    name="Limite administrative",
    style_function=lambda x: {"color": "white", "weight": 1.5, "fillOpacity": 0}
).add_to(m)

# --- 3. Graphes Waxman (une couche par catégorie, activable/désactivable) ---
for label, edges in wax_graphs.items():
    if edges is None or edges.empty:
        continue
    edges_4326 = edges.to_crs(4326)
    color = layer_colors[label] if isinstance(layer_colors[label], str) else "#{:02x}{:02x}{:02x}".format(
        int(layer_colors[label][0]*255), int(layer_colors[label][1]*255), int(layer_colors[label][2]*255)
    )
    folium.GeoJson(
        edges_4326,
        name=f"Réseau — {label}",
        style_function=lambda x, c=color: {"color": c, "weight": 1, "opacity": 0.4}
    ).add_to(m)

# --- 4. POI (une couche par catégorie, avec popup au clic) ---
for label, pois in poi_layers.items():
    if pois is None or pois.empty:
        continue
    pois_4326 = pois.to_crs(4326)
    color = layer_colors[label] if isinstance(layer_colors[label], str) else "#{:02x}{:02x}{:02x}".format(
        int(layer_colors[label][0]*255), int(layer_colors[label][1]*255), int(layer_colors[label][2]*255)
    )
    fg = folium.FeatureGroup(name=f"POI — {label}")
    for _, row in pois_4326.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=label
        ).add_to(fg)
    fg.add_to(m)

# --- 5. Contrôle des couches (case à cocher pour afficher/masquer chaque catégorie) ---
folium.LayerControl(collapsed=False).add_to(m)

# --- 6. Export en fichier HTML autonome ---
m.save("index.html")


# In[83]:


import folium
from folium.plugins import MarkerCluster

# --- 1. Centrer la carte sur l'emprise de l'admin ---
admin_4326 = admin.to_crs(4326)
centroid = admin_4326.geometry.unary_union.centroid

# tiles=None : on n'active aucun fond par défaut, on les ajoute tous manuellement ci-dessous
m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12, tiles=None)

# --- 2. Plusieurs fonds de carte, sélectionnables via le contrôle de couches ---
folium.TileLayer("CartoDB dark_matter", name="Sombre (CartoDB Dark)").add_to(m)
folium.TileLayer("CartoDB positron", name="Clair (CartoDB Positron)").add_to(m)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
folium.TileLayer(
    "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap", name="Relief (OpenTopoMap)"
).add_to(m)

# --- 3. Limite administrative ---
folium.GeoJson(
    admin_4326,
    name="Limite administrative",
    style_function=lambda x: {"color": "white", "weight": 1.5, "fillOpacity": 0}
).add_to(m)

# --- 4. Graphes Waxman (réseaux, une couche par catégorie) ---
def to_hex(color):
    if isinstance(color, str):
        return color
    return "#{:02x}{:02x}{:02x}".format(int(color[0]*255), int(color[1]*255), int(color[2]*255))

for label, edges in wax_graphs.items():
    if edges is None or edges.empty:
        continue
    edges_4326 = edges.to_crs(4326)
    color = to_hex(layer_colors[label])
    folium.GeoJson(
        edges_4326,
        name=f"Réseau — {label}",
        style_function=lambda x, c=color: {"color": c, "weight": 1, "opacity": 0.4}
    ).add_to(m)

# --- 5. POI avec clustering (une cluster group par catégorie) ---
for label, pois in poi_layers.items():
    if pois is None or pois.empty:
        continue
    pois_4326 = pois.to_crs(4326)
    color = to_hex(layer_colors[label])

    cluster = MarkerCluster(name=f"POI — {label}")
    for _, row in pois_4326.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=label
        ).add_to(cluster)
    cluster.add_to(m)

# --- 6. Contrôle des couches (fonds de carte + catégories, tout activable/désactivable) ---
folium.LayerControl(collapsed=False).add_to(m)

# --- 7. Export ---
m.save("index.html")


# In[86]:


get_ipython().system('mkdir "Bordeaux Accessibilite"')


# In[89]:


import os
print(os.getcwd())


# In[90]:


import os

# Cherche le dossier Portfolio_Adama sur ton PC
for root, dirs, files in os.walk(r"C:\Users\diane"):
    if "Portfolio_Adama" in dirs:
        print(os.path.join(root, "Portfolio_Adama"))


# In[91]:


import os
os.chdir(r"C:\Users\diane\Documents\GitHub\Portfolio_Adama")
print(os.getcwd())  # vérifie que tu es bien au bon endroit


# In[92]:


os.makedirs("Bordeaux Accessibilite", exist_ok=True)  # exist_ok évite l'erreur si déjà créé
m.save("Bordeaux Accessibilite/index.html")


# In[93]:


import os
taille_mo = os.path.getsize("Bordeaux Accessibilite/index.html") / (1024 * 1024)
print(f"{taille_mo:.1f} Mo")


# In[94]:


for label, edges in wax_graphs.items():
    edges_4326 = edges.to_crs(4326)
    edges_4326["geometry"] = edges_4326.geometry.simplify(tolerance=0.0001)  # réduit le nombre de points
    ...


# In[ ]:




