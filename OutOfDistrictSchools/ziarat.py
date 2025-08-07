import folium
import math

# Coordinates
kach = (30 + 26/60 + 2/3600, 67 + 19/60 + 27/3600)
kawas = (30 + 27/60 + 56/3600, 67 + 34/60 + 56/3600)
zandra = (30.4068, 67.4397)

# Calculate distances between points (in km)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

# Calculate distances
kach_kawas_dist = haversine_distance(kach[0], kach[1], kawas[0], kawas[1])
kach_zandra_dist = haversine_distance(kach[0], kach[1], zandra[0], zandra[1])
kawas_zandra_dist = haversine_distance(kawas[0], kawas[1], zandra[0], zandra[1])

print(f"Distance Kach to Kawas: {kach_kawas_dist:.2f} km")
print(f"Distance Kach to Zandra: {kach_zandra_dist:.2f} km")
print(f"Distance Kawas to Zandra: {kawas_zandra_dist:.2f} km")

# Find the center point and maximum distance
center = ((kach[0] + kawas[0] + zandra[0])/3, (kach[1] + kawas[1] + zandra[1])/3)

# Calculate distances from center to each point
center_to_kach = haversine_distance(center[0], center[1], kach[0], kach[1])
center_to_kawas = haversine_distance(center[0], center[1], kawas[0], kawas[1])
center_to_zandra = haversine_distance(center[0], center[1], zandra[0], zandra[1])

# Find the maximum distance to create a boundary that encompasses all points
max_distance = max(center_to_kach, center_to_kawas, center_to_zandra)
boundary_radius = max_distance + 2  # Add 2km buffer

print(f"Boundary radius: {boundary_radius:.2f} km")

# Create map
m = folium.Map(location=center, zoom_start=11)

# Add main boundary circle (light green)
folium.Circle(
    location=center,
    radius=boundary_radius * 1000,  # Convert to meters
    color='lightgreen',
    weight=3,
    fill=True,
    fillColor='lightgreen',
    fillOpacity=0.1,
    popup=f'Total Ziarat Area (Radius: {boundary_radius:.1f} km)'
).add_to(m)

# Add markers with distance information
folium.Marker(
    kach, 
    tooltip="Kach",
    popup=f"Kach<br>Distance from center: {center_to_kach:.1f} km"
).add_to(m)
folium.Marker(
    kawas, 
    tooltip="Kawas",
    popup=f"Kawas<br>Distance from center: {center_to_kawas:.1f} km"
).add_to(m)
folium.Marker(
    zandra, 
    tooltip="Zandra",
    popup=f"Zandra<br>Distance from center: {center_to_zandra:.1f} km"
).add_to(m)

# Add individual 12.5 km radius circles to each location
for i, (point, name) in enumerate([(kach, "Kach"), (kawas, "Kawas"), (zandra, "Zandra")]):
    colors = ['blue', 'red', 'purple']
    folium.Circle(
        location=point,
        radius=12500,  # 12.5 km in meters
        color=colors[i],
        weight=2,
        fill=True,
        fillOpacity=0.2,
        popup=f'{name} - 12.5 km radius'
    ).add_to(m)

# Add center point marker
folium.Marker(
    center,
    tooltip="Geographic Center",
    popup="Center of all three locations",
    icon=folium.Icon(color='green', icon='star')
).add_to(m)

# Add distance lines between points
folium.PolyLine(
    [kach, kawas],
    color='orange',
    weight=2,
    opacity=0.7,
    popup=f'Distance: {kach_kawas_dist:.1f} km'
).add_to(m)

folium.PolyLine(
    [kach, zandra],
    color='orange',
    weight=2,
    opacity=0.7,
    popup=f'Distance: {kach_zandra_dist:.1f} km'
).add_to(m)

folium.PolyLine(
    [kawas, zandra],
    color='orange',
    weight=2,
    opacity=0.7,
    popup=f'Distance: {kawas_zandra_dist:.1f} km'
).add_to(m)

# Save to HTML
m.save("map_with_radius.html")
print("Map saved as 'map_with_radius.html'")
print("\nMap Features:")
print("- Light green boundary shows total ziarat area")
print("- Individual colored circles show 12.5km radius around each location")
print("- Orange lines show distances between locations")
print("- Green star shows the geographic center")
