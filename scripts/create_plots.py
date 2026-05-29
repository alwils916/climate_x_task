import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerTuple
import matplotlib.patches as mpatches


df = pd.read_csv('../data/api_csv_output_ssp370_None.csv')

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
    offsets = {
    3: (80, 50),
    5: (125, 25),
    2: (-20, 20),
    4: (-20, 20),
    6: (125, 25),
    }
    # Permanent label
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        icon=folium.DivIcon(
            html=f'<div style="color:white;font-weight:bold;font-size:30px;text-shadow: 1px 1px 2px black;">Asset {int(row["Asset ID"])}</div>',
            icon_size=(120, 30),
            icon_anchor=offsets.get(int(row["Asset ID"]), (0, 0))
        )
    ).add_to(m)


m.save("../data/asset_locations.html")

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../data/api_csv_output_ssp370_None.csv')
df.query('Year == 2050').sort_values(by="Asset ID", ascending=True)[
    ['Asset ID', 'Coastal Flood Severity Value (maximum depth (m))','Building Replacement Cost', 'Total Building Loss', 'Total Loss Percentage',
     ]].to_csv('../data/2050_projections.csv', index=False)
df_rp = pd.read_csv('../data/api_csv_output_ssp370_10_50_100_200_500.csv')
ids = [2, 7, 6]
subset = df_rp.query('`Asset ID` in @ids and `Return Period` == "1 in 50"').copy()
subset = subset[['Asset ID', 'Year',  'Coastal Flood Severity Value (maximum depth (m))',
 'Coastal Flood Severity Lower Bound',
 'Coastal Flood Severity Upper Bound',]].copy()

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['text.color'] = 'black'
plt.rcParams['axes.labelcolor'] = 'black'
plt.rcParams['xtick.color'] = 'black'
plt.rcParams['ytick.color'] = 'black'
fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.tab10.colors
colors = (colors[3], colors[2], colors[1])
handles = []


for i, (asset_id, group) in enumerate(subset.groupby('Asset ID')):
    group = group.sort_values('Year')
    color = colors[i]
    
    line, = ax.plot(
        group['Year'],
        group['Coastal Flood Severity Value (maximum depth (m))'],
        marker='*',
        color=color,
        label=f'Asset {asset_id}'
    )
    
    fill = ax.fill_between(
        group['Year'],
        group['Coastal Flood Severity Lower Bound'],
        group['Coastal Flood Severity Upper Bound'],
        color=color,
        alpha=0.2
    )
    handles.append((line, fill))

# Build legend with both line and shaded band per asset
legend_handles = []
legend_labels = []
for i, (asset_id, _) in enumerate(subset.groupby('Asset ID')):
    color = colors[i]
    line = plt.Line2D([0], [0], color=color, marker='o')
    patch = mpatches.Patch(color=color, alpha=0.2)
    legend_handles.append((line, patch))
    legend_labels.append(f'Asset {asset_id} (shaded = uncertainty bounds)')

ax.legend(
    legend_handles,
    legend_labels,
    handler_map={tuple: HandlerTuple(ndivide=None)},
    # bbox_to_anchor=(1.05, 1),
    loc='upper left',
    title='Asset ID',
    fontsize=14

)

ax.set_title('1 in 50 Year Coastal Flood Depth by Asset (SSP3-7.0)', fontweight="bold", fontsize=16)
ax.set_xlabel('Year', fontweight='bold', fontsize=14)
ax.set_ylabel('Maximum Coastal Flood Depth (m)', fontweight='bold', fontsize=14)
ax.tick_params(axis='both', labelsize=12)
ax.get_legend().get_title().set_fontsize(14)
plt.tight_layout()
plt.savefig('../data/coastal_flood_50yr_uncertainty.png', dpi=150, bbox_inches='tight')