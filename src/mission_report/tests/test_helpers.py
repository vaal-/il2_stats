from ..helpers import point_in_polygon, distance, is_pos_correct


def test_point_in_polygon():
    point = {'x': 7500.0, 'y': 0.0, 'z': 7500.0}
    polygon_square = [[0, 0, 0], [15000, 0, 0], [15000, 0, 15000], [0, 0, 15000]]
    assert point_in_polygon(point=point, polygon=polygon_square)
    # точка окружена полигоном
    polygon_square = [[0, 0, 0], [15000, 0, 0], [15000, 0, 5000], [15000, 0, 15000], [5000, 0, 15000], [5000, 0, 10000],
                      [10000, 0, 10000], [10000, 0, 5000], [5000, 0, 5000], [5000, 0, 15000], [0, 0, 15000]]
    assert not point_in_polygon(point=point, polygon=polygon_square)


def test_distance():
    pos1 = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    pos2 = {'x': 1500.0, 'y': 0.0, 'z': 1500.0}
    assert int(distance(p1=pos1, p2=pos2)) == 2121


def test_is_pos_correct():
    pos = None
    assert not is_pos_correct(pos)
    pos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    assert not is_pos_correct(pos)
    pos = {'x': 1.0, 'y': 2.0, 'z': 3.0}
    assert is_pos_correct(pos)
