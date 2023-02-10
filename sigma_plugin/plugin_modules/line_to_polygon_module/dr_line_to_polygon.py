"""Documentation for DRlineToPolygon class"""

from typing import List, Union
from qgis.core import QgsPointXY, QgsGeometry, QgsFeature, QgsWkbTypes, QgsVectorLayerUtils, QgsPoint
from ...help_tools.help_func import LineToPolygonData, TopologyFeatureData
# from .dr_geometry_structs import DRPoint, DRLine
# from .dr_geometry_func import DRGeometryFunctions
from ..geometry_func.dr_geometry_functions import DRGeometryFunctions as dr_geom
from ..geometry_func.dr_geometry_structs import DRPoint, DRLine, DRCircle

class LineToPolygon:
    """Documentation for DRlineToPolygon class"""

    def line_to_polygon(self, input_data: Union[LineToPolygonData, List[LineToPolygonData]]) -> Union[LineToPolygonData, List[LineToPolygonData]]:
        """Documentation for lineToPoly function"""

        copy_line = LineToPolygon.check_line(input_data)

        polygon_list = []
        for el in input_data.line_features:
            polygon_list.append(QgsFeature(el))

        for x, feat in enumerate(copy_line):
            bufferDist = input_data.buffers_size[x]
            geom = feat.geometry()
            buff = geom.buffer(bufferDist, 5, QgsGeometry.CapFlat, QgsGeometry.JoinStyleRound, 0)
            polygon_list[x].setGeometry(buff)

        output_data = LineToPolygonData(
            line_features=input_data.line_features,
            polygon_features=polygon_list.copy(),
            buffers_size=input_data.buffers_size,
            quarters_features=input_data.quarters_features,
        )

        for i in range(len(input_data.line_features)):
            result = LineToPolygon._fix_void(output_data, i)
            if result is not None:
                output_data.polygon_features[i].setGeometry(result)

        output_data = LineToPolygon._cut_polygons(output_data)        

        return output_data

    @staticmethod
    def check_line(input_data):
        line_features = []
        quarter_features = []
        buffers_size = input_data.buffers_size.copy()
        counter = 0
        for feat in input_data.line_features:
            line_features.append(QgsFeature(feat))

        for feat in input_data.quarters_features:
            quarter_features.append(QgsFeature(feat))

        for index in range(len(line_features)):
            line_geometry = line_features[index].geometry()
            quarter_geometry = quarter_features[index].geometry()

            if quarter_geometry.isMultipart():
                quarter_points_list = quarter_geometry.asMultiPolygon()
            else:
                quarter_points_list = [quarter_geometry.asPolygon()]

            # if line_features[index].id() == 25:
            #     print(quarter_points_list)

            if line_geometry.isMultipart():
                line_points_list = line_geometry.asMultiPolyline()
                # if line_features[index].id() == 344:
                #     for line_points in line_points_list:
                #         print(line_points)
            else:
                line_points_list = [line_geometry.asPolyline()]

            for y, line_points in enumerate(line_points_list):

                new_start_point = DRPoint(line_points[0][0], line_points[0][1])
                new_end_point = DRPoint(line_points[-1][0], line_points[-1][1])

                start_point = DRPoint(line_points[0][0], line_points[0][1])
                pre_start_point = DRPoint(line_points[1][0], line_points[1][1])

                end_point = DRPoint(line_points[-1][0], line_points[-1][1])
                pre_end_point = DRPoint(line_points[-2][0], line_points[-2][1])

                for quarter_points in quarter_points_list:
                    quarter_points = quarter_points[0]
                    # if line_features[index].id() == 25:
                    #     # quarter_points = quarter_points_list[1]
                    #     print()

                    ownership_full_line = LineToPolygon._check_line_owership(
                        line_points, quarter_points, buffers_size[index])

                    ownership_start = LineToPolygon._check_point_ownership(
                        DRLine(pre_start_point, start_point), quarter_points, buffers_size[index])

                    if ownership_start:
                        cur_line = DRLine(pre_start_point, start_point)
                        new_start_point = dr_geom.Line.change_line_distance(cur_line, 30 * buffers_size[index])

                    ownership_end = LineToPolygon._check_point_ownership(
                        DRLine(pre_end_point, end_point), quarter_points, buffers_size[index])
                    if ownership_end:
                        cur_line = DRLine(pre_end_point, end_point)
                        new_end_point = dr_geom.Line.change_line_distance(cur_line, 30 * buffers_size[index])

                    if new_start_point != start_point:
                        line_points[0] = QgsPointXY(new_start_point.x, new_start_point.y)

                    if new_end_point != end_point:
                        line_points[-1] = QgsPointXY(new_end_point.x, new_end_point.y)
                    line_points_list[y] = line_points

            if line_geometry.isMultipart():
                line_geometry = QgsGeometry.fromMultiPolylineXY(line_points_list)
            else:
                line_geometry = QgsGeometry.fromPolylineXY(line_points_list)

            line_features[index].setGeometry(line_geometry)

        return line_features

    def _check_line_owership(line_points, quarter_points, buffers_size):
        result = None
        for line_index in range(len(line_points)):

            if not result and result is not None:
                break
            else:
                pass 
        
            line_point = DRPoint(line_points[line_index][0], line_points[line_index][1])

            for quarter_index in range(len(quarter_points)):
                quarter_point = DRPoint(
                    quarter_points[quarter_index][0], quarter_points[quarter_index][1])

                result = dr_geom.Intersection.check_point_ownership_circle(
                    line_point, DRCircle(quarter_point, buffers_size))
                if result:
                    break

        return result


    def _check_point_ownership(segment_line, quarter_points, buffers_size, asd=False):
        result = False
        intersections = []
        _, point = dr_geom.Parsers.line_to_points(segment_line)
        for i in range(len(quarter_points) - 1):
            quarter_line = DRLine(
                DRPoint(quarter_points[i][0], quarter_points[i][1]),
                DRPoint(quarter_points[i + 1][0], quarter_points[i + 1][1]),
                )
            intersection = dr_geom.Intersection.find_segment_intersect_line(quarter_line, segment_line)
            if intersection is not None:
                intersections.append(intersection)
                result = True

        # if asd:
        #     print(intersections)

        if result:
            _, point = dr_geom.Parsers.line_to_points(segment_line)
            min_intersection = LineToPolygon._find_min_distance(point, intersections)
            result = dr_geom.Intersection.check_point_ownership_circle(
                min_intersection, DRCircle(point, buffers_size))

        return result


    def _find_min_distance(main_point, points):
        distances = []
        main_x, main_y = dr_geom.Parsers.point_to_coords(main_point)
        for point in points:
            x, y = dr_geom.Parsers.point_to_coords(point)
            distance = dr_geom.Base.pythagorean_theorem(
                main_x - x, main_y - y)
            distances.append(distance)
        
        return points[distances.index(min(distances))]


    # @staticmethod
    # def _check_point_ownership_circle(point, circle):
    #     pass

    @staticmethod
    def _check_point_ownership_line(point, quarter_points):
        ownership = False
        for index in range(len(quarter_points) - 1):
            start_point = DRPoint(quarter_points[index].x(), quarter_points[index].y())
            end_point = DRPoint(quarter_points[index + 1].x(), quarter_points[index + 1].y())
            ownership = dr_geom.Intersection.check_point_ownership_line(start_point, point, end_point)
            if ownership:
                break

        return ownership


    @staticmethod
    def _longer_line(line, mode, value):
        if mode:
            segment = DRLine(
                DRPoint(line[1][0], line[1][1]),
                DRPoint(line[0][0], line[0][1]),
            )
        else:
            segment = DRLine(
                DRPoint(line[-2][0], line[-2][1]),
                DRPoint(line[-1][0], line[-1][1]),
            )

        new_line = dr_geom.Line.change_line_distance(segment, value)
        return line

    @staticmethod
    def _fix_void(input_data, index):

        line = input_data.line_features[index]
        polygon = input_data.polygon_features[index]
        buffer_size = input_data.buffers_size[index]
        geometry = line.geometry()
        extreme_points = []

        if not geometry.isMultipart():
            return None

        input_lines = geometry.asMultiPolyline()

        if len(input_lines) < 2:
            return None


        for input_line in input_lines:
            extreme_points.append([input_line[0].x(), input_line[0].y()])
            extreme_points.append([input_line[-1].x(), input_line[-1].y()])

        templist = []
        repeat_points = []

        for point in extreme_points:
            if point not in templist:
                templist.append(point)
            else:
                repeat_points.append(point)

        if repeat_points == []:
            return None

        result = None

        for point in repeat_points:
            geom_point = QgsGeometry.fromPointXY(QgsPointXY(point[0], point[1]))
            buff = geom_point.buffer(buffer_size, 50, QgsGeometry.CapRound, QgsGeometry.JoinStyleRound, 0)
            if result is None:
                result = polygon.geometry().combine(buff)
            else:
                result = result.combine(buff)

        del templist
        del repeat_points
        del extreme_points

        return result

    @staticmethod
    def _cut_polygons(input_data: Union[LineToPolygonData, List[LineToPolygonData]]) -> Union[LineToPolygonData, List[LineToPolygonData]]:

        quarters_features = input_data.quarters_features
        polygon_features = input_data.polygon_features

        polygon_list = []
        for el in input_data.polygon_features:
            polygon_list.append(QgsFeature(el))

        for index in range(len(quarters_features)):
            polygon_geom = polygon_features[index].geometry()
            quarter_geom = quarters_features[index].geometry()
            result = polygon_geom.makeDifference(polygon_geom.makeDifference(quarter_geom))
            polygon_list[index].setGeometry(result)

        input_data.polygon_features = polygon_list

        return input_data