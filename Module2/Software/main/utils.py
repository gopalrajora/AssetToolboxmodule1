import pandas as pd
import folium
from folium import FeatureGroup
from folium.plugins import MarkerCluster
from folium import plugins
from folium.plugins import Draw
from folium.plugins import MiniMap
from folium.plugins import Search
def create_map(data_df,region_coordinates):
    #Create the base Map
    m = folium.Map(location=region_coordinates, tiles='OpenStreetMap', zoom_start=7,control_scale=True)
    draw = Draw(export=True)
    draw.add_to(m)
    minimap = MiniMap()
    m.add_child(minimap)
    markerCluster = MarkerCluster().add_to(m)
    data_df = data_df.copy()
    data_df.reset_index(inplace=True)
    final_column_index =  len(data_df.columns) - 3
    print(final_column_index)
    for i, row in data_df.iterrows():
        lat = data_df.at[i,'lat']
        lng = data_df.at[i,'long']
        print(lat, lng)
        assets = data_df.iat[i,final_column_index]
        popup = '<center>'+f'<h6 style="font-size:16px; color:SlateBlue">{data_df["index"].values[i]}</h6>'
        for clm in data_df.columns[1:-2]:
            popup +='<br>'+'<strong>'+ clm+': </strong>'+ '{0:.4f}'.format(data_df.at[i, clm])

        popup +='</center>'
        if assets >0.75:
            color = 'red'
        elif assets >.50:
            color = 'orange'
        else:
            color = 'green'
        
        folium.Marker(location=[lat, lng],popup=popup, icon=folium.Icon(color=color, icon ='info-sign')).add_to(markerCluster)

    m.save("../HTML_ASSETS/results/assets_location.html")

