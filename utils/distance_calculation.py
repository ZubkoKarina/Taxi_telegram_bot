import math


def haversine(first_point: list, second_point: list) -> float:
    R = 6371.0

    dlat = math.radians(float(second_point[0]) - float(first_point[0]))
    dlon = math.radians(float(second_point[1]) - float(first_point[1]))
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(float(first_point[0]))) * math.cos(math.radians(float(second_point[0]))) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance
