from .dr_geometry_structs import DRPoint
from .dr_geometry_parsers import DRGeometryParser

# from dr_geometry_structs import DRPoint
# from dr_geometry_parsers import DRGeometryParser

class DRBaseGeometry:
    @staticmethod
    def pythagorean_theorem(var1, var2):
        return (var1 ** 2 + var2 ** 2) ** 0.5

    @staticmethod
    def calc_cos(line_1, line_2):
        vector_1 = DRBaseGeometry._calc_line_vector(line_1)
        vector_2 = DRBaseGeometry._calc_line_vector(line_2)

        numerator = (vector_1.x * vector_2.x + vector_1.y  * vector_2.y)

        den_vec1 = DRBaseGeometry.pythagorean_theorem(vector_1.x, vector_1.y)
        den_vec1 = den_vec1 if den_vec1 != 0 else 1

        den_vec2 = DRBaseGeometry.pythagorean_theorem(vector_2.x, vector_2.y)
        den_vec2 = den_vec2 if den_vec2 != 0 else 1

        denominator = den_vec2 * den_vec1

        return numerator / denominator

    @staticmethod
    def _calc_line_vector(line):
        start_x, start_y, end_x, end_y = DRGeometryParser.line_to_coords(line)
        vector = DRPoint(end_x - start_x, end_y - start_y)

        return vector

    def calc_length_vector(line):
        start_x, start_y, end_x, end_y = DRGeometryParser.line_to_coords(line)
        length = DRBaseGeometry.pythagorean_theorem(
            start_x - end_x, start_y - end_y)

        return length