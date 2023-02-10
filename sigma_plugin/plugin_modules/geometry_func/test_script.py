from dr_geometry_functions import DRGeometryFunctions as dr_geometry
from dr_geometry_structs import DRPoint, DRLine, DRCircle

print("run test script...\n")

x1, y1 = 0, 0
x2, y2 = 10, 10

x3, y3 = 0, 10
x4, y4 = 10, 0

x5, y5 = 0, 20
x6, y6 = 15, 20

x7, y7 = 10, 0
x8, y8 = 10, 10

r = 5

print("----- Test create structures -----")

point_1 = DRPoint(x1, y1)
point_2 = DRPoint(x2, y2)
point_3 = DRPoint(x3, y3)
point_4 = DRPoint(x4, y4)

point_5 = DRPoint(x5, y5)
point_6 = DRPoint(x6, y6)
point_7 = DRPoint(x7, y7)
point_8 = DRPoint(x8, y8)

line_1 = DRLine(point_1, point_2)
line_2 = DRLine(point_2, point_3)
line_3 = DRLine(point_3, point_4)
line_4 = DRLine.create_from_coords(x1, y1, x2, y2)
line_5 = DRLine(point_5, point_6)
line_6 = DRLine(point_7, point_8)

circle_1 = DRCircle.create_from_coords(x1, y1, r)
circle_2 = DRCircle(point_1, r)

print("create point from constuctor:", point_1)
print()
print("create line from constuctor:", line_1)
print("create line from \"create_from_coords\":", line_4)
print(f"reverse line from {line_2}: {DRLine.reverse_line(line_2)}")
print()
print("create circle from constuctor:", circle_1)
print("create circle from \"create_from_coords\":", circle_2)
print()

print("----- Test Parsers -----")
x, y = dr_geometry.Parsers.point_to_coords(point_1)
print(f"point_to_coords from {point_1}: x = {x}, y = {y}")
print()

x1, y1, x2, y2 = dr_geometry.Parsers.line_to_coords(line_1)
print(f"line_to_coords from {line_1.start_point, line_1.end_point}: x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
p1, p2 = dr_geometry.Parsers.line_to_points(line_1)
print(f"line_to_points from {line_1.start_point, line_1.end_point}: point_1 = {p1}, point_2 = {p2}")
print()

x, y, r = dr_geometry.Parsers.circle_to_coords(circle_1)
print(f"circle_to_coords from {circle_1}: x = {x}, y = {y}, r = {r}")
p, r = dr_geometry.Parsers.circle_to_point(circle_1)
print(f"circle_to_point from {circle_1}: point = {p}, r = {r}")
print()

print("----- Test Base -----")

result = dr_geometry.Base.pythagorean_theorem(3,4)
print("pythagorean_theorem from 3 and 4:", result)

result = dr_geometry.Base.calc_cos(line_1, line_2)
print(f"calc_cos from {line_1.start_point, line_1.end_point} and {line_2.start_point, line_2.end_point}: cos =", result)
print()

print("----- Test Equation -----")

k, b = dr_geometry.Equation.create_equation_line(x1, y1, x2, y2)
print(f"equation from [[0, 0], [5, 10]]: y = {k}x + {b}")

k, b = dr_geometry.Equation.create_equation_perpendicular_line(point_2, k)
print(f"perpendicular equation from [[0, 0], [5, 10]] on point [5, 10]: y = {k}x + {b}")
print()

print("----- Test Intersection -----")

result = dr_geometry.Intersection.find_line_intersect_circle(line_1, circle_1)
print(f"find_line_intersect_circle from {circle_1} and {line_3.start_point, line_3.end_point}: point = {result}")

result = dr_geometry.Intersection.find_segment_intersect_line(line_5, line_6)
print(f"find_segment_intersect_line from {line_5.start_point, line_5.end_point} and {line_6.start_point, line_6.end_point}: point = {result}")

result = dr_geometry.Intersection.find_segment_intersect_line(line_6, line_5)
print(f"find_segment_intersect_line from {line_6.start_point, line_6.end_point} and {line_5.start_point, line_5.end_point}: point = {result}")

result = dr_geometry.Intersection.find_segment_intersect_segment(line_5, line_6)
print(f"find_segment_intersect_segment from {line_5.start_point, line_5.end_point} and {line_6.start_point, line_6.end_point}: point = {result}")

result = dr_geometry.Intersection.find_line_intersect_line(line_5, line_6)
print(f"find_line_intersect_line from {line_5.start_point, line_5.end_point} and {line_6.start_point, line_6.end_point}: point = {result}")

start_point, end_point = dr_geometry.Parsers.line_to_points(line_6)
owner_result = dr_geometry.Intersection.check_point_ownership_line(start_point, end_point, result)
print(f"check_point_ownership_line from {line_6.start_point, line_6.end_point} and {result}: point = {owner_result}")

start_point, end_point = dr_geometry.Parsers.line_to_points(line_5)
owner_result = dr_geometry.Intersection.check_point_ownership_line(start_point, end_point, result)
print(f"check_point_ownership_line from {line_5.start_point, line_5.end_point} and {result}: point = {owner_result}")
print()

print("----- Test Vector -----")

result = dr_geometry.Vector.get_vector_angle(line_1, line_2)
print(f"get_vector_angle from {line_1.start_point, line_1.end_point} and {line_2.start_point, line_2.end_point}: angle = {result}")

result = dr_geometry.Vector.get_vector_direction(line_1)
print(f"get_vector_direction from {line_1.start_point, line_1.end_point} and {line_2.start_point, line_2.end_point}: direction = {result}")
string_result = dr_geometry.Vector.string_direction(result)
print(f"string_direction from direction = {result}, string_direction = {string_result}")

x, y, _, _ = dr_geometry.Parsers.line_to_coords(line_2)
result = dr_geometry.Vector.vector_normalization(x, y)
print(f"vector_normalization from x, y: {x, y}, result = {result}")
print()

print("----- Test Line -----")
value = 5
result = dr_geometry.Line.change_line_distance(line_1, value)
print(f"change_line_distance from point: {line_3} and value: {value}, new_point = {result}")
value = -5
result = dr_geometry.Line.change_line_distance(line_3, value)
print(f"change_line_distance from point: {line_3} and value: {value}, new_point = {result}")
