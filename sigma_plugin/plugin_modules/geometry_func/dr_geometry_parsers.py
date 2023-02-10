class DRGeometryParser:

    @staticmethod
    def line_to_coords(line):

        start_x = line.start_point.x
        start_y = line.start_point.y
        end_x = line.end_point.x
        end_y = line.end_point.y

        return start_x, start_y, end_x, end_y

    @staticmethod
    def line_to_points(line):

        start_point = line.start_point
        end_point = line.end_point

        return start_point, end_point

    @staticmethod
    def point_to_coords(point):

        x = point.x
        y = point.y

        return x, y

    @staticmethod
    def circle_to_coords(circle):

        x = circle.center.x
        y = circle.center.y
        r = circle.r

        return x, y, r

    @staticmethod
    def circle_to_point(circle):

        point = circle.center
        radius = circle.r

        return point, radius
