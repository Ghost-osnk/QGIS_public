import math

from .dr_base_geometry import DRBaseGeometry 
from .dr_geometry_parsers import DRGeometryParser
from .dr_geometry_structs import DRLine

# from dr_base_geometry import DRBaseGeometry 
# from dr_geometry_parsers import DRGeometryParser
# from dr_geometry_structs import DRLine

class DRVectorGeometry:

    @staticmethod
    def get_vector_angle(line_1, line_2):

        vector_1 = DRLine(line_1.start_point, line_1.end_point)
        vector_2 = DRLine(line_1.end_point, line_2.start_point)

        rad_to_angle = 180 / math.pi
        cos = DRBaseGeometry.calc_cos(vector_1, vector_2)
        cos = 1 if cos > 1 else cos
        angle = abs(180 - math.acos(cos) * rad_to_angle)

        return angle

    @staticmethod
    def string_direction(direction):
        if direction == 0:
            string = "up"
        elif direction == 1:
            string = "down" 
        elif direction == 2:
            string = "right" 
        elif direction == 3:
            string = "left" 
        elif direction == 4:
            string = "up-right" 
        elif direction == 5:
            string = "down-left" 
        elif direction == 6:
            string = "down-right" 
        elif direction == 7:
            string = "up-left"
        else:
            string = "wrong direction"
        return string 

    @staticmethod
    def get_vector_direction(line):
        # 0 - up
        # 1 - down
        # 2 - right
        # 3 - left
        # 4 - up-right
        # 5 - down-left
        # 6 - down-right
        # 7 - up-left

        start_x, start_y, end_x, end_y = DRGeometryParser.line_to_coords(line)

        direction = None
        delta_x = end_x - start_x
        delta_y = end_y - start_y

        if delta_x == 0:
            direction = 0 if delta_y > 0 else 1
        elif delta_y == 0:
            direction = 2 if delta_x > 0 else 3
        else:
            if delta_x > 0 and delta_y > 0:
                direction = 4
            elif delta_x < 0 and delta_y < 0:
                direction = 5
            elif delta_x > 0 > delta_y:
                direction = 6
            elif delta_x < 0 < delta_y:
                direction = 7

        return direction

    @staticmethod
    def vector_normalization(x, y):

        distance = DRBaseGeometry.pythagorean_theorem(x, y)
        distance = distance if distance != 0 else 1

        return x / distance, y / distance