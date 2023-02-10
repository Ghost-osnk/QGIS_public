import math
from .dr_base_geometry import DRBaseGeometry 
from .dr_geometry_structs import DRPoint
from .dr_geometry_parsers import DRGeometryParser
from .dr_equation_geometry import DREquationGeometry

# from dr_base_geometry import DRBaseGeometry 
# from dr_geometry_structs import DRPoint
# from dr_geometry_parsers import DRGeometryParser
# from dr_equation_geometry import DREquationGeometry

class DRIntersectionGeometry:

    @staticmethod
    def find_segment_intersect_line(segment, line):

        result = DRIntersectionGeometry._find_line_intersect_line(segment, line)

        if result is not None:
            start_segment, end_segment = DRGeometryParser.line_to_points(segment)

            ownership = DRIntersectionGeometry.check_point_ownership_line(
                start_segment, result, end_segment)

            return result if ownership else None
        
        else:
            return None

    @staticmethod
    def find_segment_intersect_segment(segment_1, segment_2):
        
        result = DRIntersectionGeometry._find_line_intersect_line(segment_1, segment_2)

        if result is not None:
            start_segment_1, end_segment_1 = DRGeometryParser.line_to_points(segment_1)
            start_segment_2, end_segment_2 = DRGeometryParser.line_to_points(segment_2)

            ownership_1 = DRIntersectionGeometry.check_point_ownership_line(
                start_segment_1, result, end_segment_1)
            ownership_2 = DRIntersectionGeometry.check_point_ownership_line(
                start_segment_2, result, end_segment_2)

            return result if ownership_1 and ownership_2 else None
        
        else:
            return None

    @staticmethod
    def find_line_intersect_line(line_1, line_2):
        result = DRIntersectionGeometry._find_line_intersect_line(line_1, line_2)
        return result

    @staticmethod
    def find_line_intersect_circle(line, circle):

        x1, y1, x2, y2 = DRGeometryParser.line_to_coords(line)
        cx, cy, r = DRGeometryParser.circle_to_coords(circle)

        if x1 == x2:
            if abs(r) >= abs(x1 - cx):
                point_1 = x1, cy - (r ** 2 - (x1 - cx) ** 2) ** 0.5
                point_2 = x1, cy - (r ** 2 + (x1 - cx) ** 2) ** 0.5
                intersection = [point_1, point_2]

            else:
                intersection = []

        else:
            eq_k, eq_b = DREquationGeometry.create_equation_line(x1, y1, x2, y2)
            a = eq_k ** 2 + 1
            b = 2 * eq_k * (eq_b - cy) - 2 * cx
            c = (eq_b - cy) ** 2 + cx ** 2 - r ** 2
            delta = b ** 2 - 4 * a * c
            delta = delta if -0.1 ** 5 > delta > 0 else 0

            if delta >= 0:
                point1_x = (-b - delta ** 0.5) / (2 * a)
                point1_y = eq_k * point1_x + eq_b
                point2_x = (-b + delta ** 0.5) / (2 * a)
                point2_y = eq_k * point2_x + eq_b
                intersection = [[point1_x, point1_y], [point2_x, point2_y]]

            else:
                intersection = []

        if intersection:
            intersection = [el for el in intersection if min(y1, y2) <= el[1] <= max(y1, y2)]

        return intersection

    @staticmethod
    def check_point_ownership_line(start_point, interest_point, end_point):

        # Взят порог погрешности в 0.1% от расчётов, так как иначе при текущих исходных данных нихера не работает

        threshold = 0.1
        min_threshold = 1 - threshold / 100
        max_threshold = 1 + threshold / 100

        x1, y1 = start_point.x, start_point.y
        x2, y2 = interest_point.x, interest_point.y
        x3, y3 = end_point.x, end_point.y

        distance_12 = DRBaseGeometry.pythagorean_theorem(x1 - x2, y1 - y2)
        distance_23 = DRBaseGeometry.pythagorean_theorem(x2 - x3, y2 - y3)
        distance_13 = DRBaseGeometry.pythagorean_theorem(x1 - x3, y1 - y3)


        if distance_13 * min_threshold < distance_12 + distance_23 < distance_13 * max_threshold:
            ownership = True
        else:
            ownership = False

        return ownership

    @staticmethod
    def check_point_ownership_circle(point, circle):
        x, y = DRGeometryParser.point_to_coords(point)
        cx, cy, r = DRGeometryParser.circle_to_coords(circle)

        return (x - cx)**2 / r**2 + (y - cy)**2 / r**2 < 1

    @staticmethod
    def _find_line_intersect_line(line_1, line_2):

        start_x1, start_y1, end_x1, end_y1 = DRGeometryParser.line_to_coords(line_1)
        start_x2, start_y2, end_x2, end_y2 = DRGeometryParser.line_to_coords(line_2)

        if start_x1 == end_x1:
            if start_x2 == end_x2:
                if start_x1 != start_x2:
                    return None
            else:
                k2, b2 = DREquationGeometry.create_equation_line(start_x2, start_y2, end_x2, end_y2)
                intersection_x = start_x1
                intersection_y = k2 * intersection_x + b2

        elif start_x2 == end_x2:
            k1, b1 = DREquationGeometry.create_equation_line(start_x1, start_y1, end_x1, end_y1)
            intersection_x = start_x2
            intersection_y = k1 * intersection_x + b1

        else:
            k1, b1 = DREquationGeometry.create_equation_line(start_x1, start_y1, end_x1, end_y1)
            k2, b2 = DREquationGeometry.create_equation_line(start_x2, start_y2, end_x2, end_y2)

            if k1 == k2:
                return None

            else:
                intersection_x = (b2 - b1) / (k1 - k2)
                intersection_y = k1 * intersection_x + b1

        return DRPoint(intersection_x, intersection_y)    
