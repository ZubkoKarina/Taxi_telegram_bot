def build_waze_route(coordinates):
    base_url = "https://www.waze.com/ul?ll="
    if len(coordinates) == 1:
        # Якщо є тільки одна точка
        return f"{base_url}{coordinates[0][0]}%2C{coordinates[0][1]}&navigate=yes"
    else:
        # Якщо кілька точок, додаємо їх як проміжні зупинки
        waypoints_str = "&via=".join([f"{lat}%2C{lng}" for lat, lng in coordinates[:-1]])
        end = f"&navigate=yes&to={coordinates[-1][0]}%2C{coordinates[-1][1]}"
        return f"{base_url}{waypoints_str}{end}" if waypoints_str else f"{base_url}{end}"


def build_google_maps_route(coordinates):
    base_url = "https://www.google.com/maps/dir/?api=1&destination="
    if len(coordinates) == 1:
        return f"{base_url}{coordinates[0][0]},{coordinates[0][1]}"
    else:
        waypoints = "/".join([f"{lat},{lng}" for lat, lng in coordinates[:-1]])
        destination = f"{coordinates[-1][0]},{coordinates[-1][1]}"
        return f"{base_url}{waypoints}/{destination}"
