import math

from .dr_base_geometry import DRBaseGeometry 
from .dr_geometry_structs import DRPoint
from .dr_geometry_parsers import DRGeometryParser
from .dr_equation_geometry import DREquationGeometry
from .dr_vector_geometry import DRVectorGeometry

# from dr_base_geometry import DRBaseGeometry 
# from dr_geometry_structs import DRPoint
# from dr_geometry_parsers import DRGeometryParser
# from dr_equation_geometry import DREquationGeometry
# from dr_vector_geometry import DRVectorGeometry

class DRLineGeometry:
    """Docstring"""

    @staticmethod
    def create_perpendicular_border(main_line, inner_line, outer_line, value):
        pass
    #     new_inner_line = inner_line.copy()
    #     new_outer_line = outer_line.copy()

    #     start_main_line = [main_line[1], main_line[0]]
    #     end_main_line = [main_line[-2], main_line[-1]]
    #     start_line = DRGeomParser.parse_line(start_main_line)
    #     end_line = DRGeomParser.parse_line(end_main_line)

    #     start_inner_line = [inner_line[1], inner_line[0]]
    #     end_inner_line = [inner_line[-2], inner_line[-1]]
    #     start_inner = DRGeomParser.parse_line(start_inner_line)
    #     end_inner = DRGeomParser.parse_line(end_inner_line)

    #     start_outer_line = [outer_line[1], outer_line[0]]
    #     end_outer_line = [outer_line[-2], outer_line[-1]]
    #     start_outer = DRGeomParser.parse_line(start_outer_line)
    #     end_outer = DRGeomParser.parse_line(end_outer_line)

    #     new_inner_line[0] = DRLineGeometry._sub_func_create_perpendicular_border(
    #         start_line, start_inner, value)
    #     new_inner_line[-1] = DRLineGeometry._sub_func_create_perpendicular_border(
    #         end_line, end_inner, value)

    #     new_outer_line[0] = DRLineGeometry._sub_func_create_perpendicular_border(
    #         start_line, start_outer, value)
    #     new_outer_line[-1] = DRLineGeometry._sub_func_create_perpendicular_border(
    #         end_line, end_outer, value)

    #     return new_inner_line, new_outer_line

    @staticmethod
    def _sub_func_create_perpendicular_border(line_1, line_2, value):
        pass

        # start_x1, start_y1, end_x1, end_y1 = DRGeomParser.line_to_coords(line_1)
        # start_x2, start_y2, end_x2, end_y2 = DRGeomParser.line_to_coords(line_2)

        # point = DRPoint(end_x1, end_y1)

        # if start_y1 - end_y1 == 0:
        #     intersection_x = end_x1
        #     intersection_y = end_y1 - value if end_y1 > end_y2 else end_y1 + value

        # elif start_x1 - end_x1 == 0:
        #     intersection_y = end_y1
        #     intersection_x = end_x1 - value if end_x1 > end_x2 else end_x1 + value

        # else:
        #     k1, _ = DREquationGeometry.create_equation_line(start_x1, start_y1, end_x1, end_y1)
        #     k2, b2 = DREquationGeometry.create_equation_line(start_x2, start_y2, end_x2, end_y2)
        #     kp, bp = DREquationGeometry.create_equation_perpendicular_line(point, k1)

        #     intersection_x = (bp - b2) / (k2 - kp)
        #     intersection_y = k2 * intersection_x + b2

        # return DRPoint(intersection_x, intersection_y)

    @staticmethod
    def change_line_distance(line, value, asd=False):

        x1, y1, x2, y2 = DRGeometryParser.line_to_coords(line)
        distance = DRBaseGeometry.pythagorean_theorem(x2 - x1, y2 - y1)
        direction = DRVectorGeometry.get_vector_direction(line)

        if direction == 0:
            x3 = x2
            y3 = y2 + value

        elif direction == 1:
            x3 = x1
            y3 = y2 - value

        elif direction == 2:
            x3 = x2 + value
            y3 = y2

        elif direction == 3:
            x3 = x2 - value
            y3 = y2

        else:




            if direction == 4:
                vr = y2 - y1
                gr = x2 - x1
            if direction == 5:
                vr = y2 - y1
                gr = x2 - x1
            if direction == 6:
                vr = y2 - y1
                gr = x2 - x1
            if direction == 7:
                vr = y2 - y1
                gr = x2 - x1

            atan = math.atan(vr/gr)
            cos = math.cos(atan)
            sin = math.sin(atan)

            if direction in [4,6]:
                x3 = x2 + value * cos
                y3 = y2 + value * sin
            elif direction in [5,7]:
                x3 = x2 - value * cos
                y3 = y2 - value * sin

            # else:
            #     x3 = x2 - value * cos
            #     y3 = y2 - value * sin

        # if asd:
        #     print()
        #     print(vr)
        #     print(gr)
        #     print(atan)
        #     print(cos)
        #     print(sin)
        #     print(x1, x2, x3)
        #     print(y1, y2, y3)
        #     print()



        # else:
        #     new_distance = distance + value

        #     sin_x = (x2 - x1) / distance
        #     sin_y = (y2 - y1) / distance
        #     x3 = new_distance * sin_x + x1
        #     y3 = new_distance * sin_y + y1

        return DRPoint(x3, y3)
