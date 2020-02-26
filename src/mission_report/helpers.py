import math


# http://www.ariel.com.au/a/python-point-int-poly.html
def point_in_polygon(point, polygon):
    x, y = point['x'], point['z']
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def distance(p1, p2):
    return math.hypot(p2['x'] - p1['x'], p2['z'] - p1['z'])


def is_pos_correct(pos):
    if not pos or pos == {'x': 0.0, 'y': 0.0, 'z': 0.0}:
        return False
    return True
