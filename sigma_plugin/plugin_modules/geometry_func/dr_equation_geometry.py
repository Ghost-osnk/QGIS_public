from .dr_geometry_parsers import DRGeometryParser

# from dr_geometry_parsers import DRGeometryParser

class DREquationGeometry:

    @staticmethod
    def create_equation_line(start_x, start_y, end_x, end_y):
        k = 1 if start_x - end_x == 0 else (start_y - end_y) / (start_x - end_x)
        b = end_y - k * end_x
        return k, b

    @staticmethod
    def create_equation_perpendicular_line(point, init_k):
        x, y = DRGeometryParser.point_to_coords(point)
        kp = -1 / init_k
        bp = kp * (-x) + y
        return kp, bp