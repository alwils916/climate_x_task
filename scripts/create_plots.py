import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point

df = pd.read_csv('../data/api_csv_output_ssp370_10_50_100_200_500.csv')

locations = df[['Asset ID', 'Latitude', 'Longitude']].drop_duplicates()
gdf = gpd.GeoDataFrame(
    locations,
    geometry=[Point(lon, lat) for lat, lon in zip(locations.Latitude, locations.Longitude)],
    crs="EPSG:4326"
)

m = folium.Map(
    location=[gdf['Latitude'].mean(), gdf['Longitude'].mean()],
    zoom_start=12,
    tiles='Esri.WorldImagery'
)

for _, row in gdf.iterrows():
    # Red dot
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=8,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.8,
    ).add_to(m)
    
    # Permanent label
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        icon=folium.DivIcon(
            html=f'<div style="color:white;font-weight:bold;font-size:20px;text-shadow: 1px 1px 2px black;">Asset {int(row["Asset ID"])}</div>',
            icon_size=(120, 30),
            icon_anchor=(0, 0)
        )
    ).add_to(m)


m.save("../data/asset_locations.html")