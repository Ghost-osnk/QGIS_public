"""Docstring"""

import math
from .dr_base_geometry import DRBaseGeometry
from .dr_equation_geometry import DREquationGeometry
from .dr_intersection_geometry import DRIntersectionGeometry
from .dr_line_geometry import DRLineGeometry
from .dr_geometry_parsers import DRGeometryParser

# from dr_base_geometry import DRBaseGeometry
# from dr_equation_geometry import DREquationGeometry
# from dr_intersection_geometry import DRIntersectionGeometry
# from dr_line_geometry import DRLineGeometry
# from dr_vector_geometry import DRVectorGeometry
# from dr_geometry_parsers import DRGeometryParser

class DRGeometryFunctions:

    class Base:
        @staticmethod
        def pythagorean_theorem(var1, var2):
            return DRBaseGeometry.pythagorean_theorem(var1, var2)

        @staticmethod
        def calc_cos(line_1, line_2):
            return DRBaseGeometry.calc_cos(line_1, line_2)

        @staticmethod
        def calc_length_vector(line):
            return DRBaseGeometry.calc_length_vector(line)

    class Equation:

        @staticmethod
        def create_equation_line(start_x, start_y, end_x, end_y):
            return DREquationGeometry.create_equation_line(start_x, start_y, end_x, end_y)

        @staticmethod
        def create_equation_perpendicular_line(point, init_k):
            return DREquationGeometry.create_equation_perpendicular_line(point, init_k)

    class Intersection:

        @staticmethod
        def find_segment_intersect_line(segment, line):
            return DRIntersectionGeometry.find_segment_intersect_line(segment, line)

        @staticmethod
        def find_segment_intersect_segment(segment_1, segment_2):
            return DRIntersectionGeometry.find_segment_intersect_segment(segment_1, segment_2)

        @staticmethod
        def find_line_intersect_line(line_1, line_2):
            return DRIntersectionGeometry.find_line_intersect_line(line_1, line_2)

        @staticmethod
        def find_line_intersect_circle(line, circle):
            return DRIntersectionGeometry.find_line_intersect_circle(line, circle)

        @staticmethod
        def check_point_ownership_line(start_point, interest_point, end_point):
            return DRIntersectionGeometry.check_point_ownership_line(start_point, interest_point, end_point)

        def check_point_ownership_circle(point, circle):
            return DRIntersectionGeometry.check_point_ownership_circle(point, circle)

    class Line:

        @staticmethod
        def create_perpendicular_border(main_line, inner_line, outer_line, value):
            return DRLineGeometry.create_perpendicular_border(
                main_line, inner_line, outer_line, value)

        @staticmethod
        def change_line_distance(line, value, asd=False):
            return DRLineGeometry.change_line_distance(line, value, asd)

        @staticmethod
        def calc_new_coords(point_1, point_2, value):
            return DRLineGeometry.calc_new_coords(point_1, point_2, value)

    class Vector:

        @staticmethod
        def get_vector_angle(line_1, line_2):
            return DRVectorGeometry.get_vector_angle(line_1, line_2)

        @staticmethod
        def get_vector_direction(line):
            return DRVectorGeometry.get_vector_direction(line)

        @staticmethod
        def string_direction(direction):
            return DRVectorGeometry.string_direction(direction)

        @staticmethod
        def vector_normalization(x, y):
            return DRVectorGeometry.vector_normalization(x, y)

    class Parsers:
        
        @staticmethod
        def point_to_coords(point):
            return DRGeometryParser.point_to_coords(point)

        @staticmethod
        def line_to_coords(line):
            return DRGeometryParser.line_to_coords(line)

        @staticmethod
        def line_to_points(line):
            return DRGeometryParser.line_to_points(line)

        @staticmethod
        def circle_to_coords(circle):
            return DRGeometryParser.circle_to_coords(circle)

        @staticmethod
        def circle_to_point(circle):
            return DRGeometryParser.circle_to_point(circle)
