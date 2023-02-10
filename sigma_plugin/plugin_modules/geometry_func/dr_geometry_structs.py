from dataclasses import dataclass

@dataclass
class DRPoint:
    x: float = 0
    y: float = 0

@dataclass
class DRLine:
    start_point: DRPoint = DRPoint(0, 0)
    end_point: DRPoint = DRPoint(0, 0)

    def reverse_line(line):
        return DRLine(line.end_point, line.start_point)

    def create_from_coords(start_x, start_y, end_x, end_y):
        start_point = DRPoint(start_x, start_y)
        end_point = DRPoint(end_x, end_y)

        return DRLine(start_point, end_point)

@dataclass
class DRCircle:
    center: DRPoint = DRPoint(0, 0)
    r: float = 0

    def create_from_coords(x, y, radius):
        center = DRPoint(x, y)
        return DRCircle(center, radius)