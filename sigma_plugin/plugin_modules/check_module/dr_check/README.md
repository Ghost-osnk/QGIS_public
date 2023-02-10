

# DR_CheckGeometry
## Апдейт от 03.10.22

Данный проект представляет собой собственную реализацию модуля проверки геометрии от компании [**Digital Research**](https://research.dclouds.ru/) для [*QGIS*](https://www.qgis.org/ru/site/). Проект необходим для автоматизации процесса проверки и выполнения последующих действий, таких как, например, "исправление геометрии".

### Ускоренные проверки (пригодны для демонстрации)
1) Проверка на дублирующиеся вершины полигона;          *(DRDuplicateNodes)*
2) Проверка на полигоны, числом вершин менее трёх;      *(DRMissingVertex)*
3) Проверка на дублирующиеся полигоны;                  *(DRDuplicateGeometry)*
4) Проверка на полигон внутри полигона;                 *(DRInsideObject)*
5) Проверка на самопересечение полигона;                *(DRSelfIntersection)*
6) Проверка на самоприкосновение полигона;              *(DRSelfContact)*
7) Проверка на отсутствие геометрии;                    *(DREmptyGeometry)*
8) Проверка на наличие отверстий.                       *(DRHoleCheck)*

### Реализованные проверки
1) Проверка на самопересечение полигона. Доступные классы: *Polygon*, *MultiPolygon*.
2) Проверка на самоприкосновения полигона. Доступные классы: *Polygon*, *MultiPolygon*.
3) Проверка на дублирующиеся узлы. Доступные классы: *Polygon*, *MultiPolygon*, *LineString*, *MultiLineString*
4) Проверка на полигоны, числом вершин менее трёх. Доступные классы: *Polygon*, *MultiPolygon*.
5) Проверка на дублирующиеся геометрии. Доступные классы: *Polygon*, *MultiPolygon*, *LineString*, *MultiLineString*, *Point*, *MultiPoint*.
6) Проверка на полигон внутри полигона. Доступные классы: *Polygon*, *MultiPolygon*.
7) Проверка на наличие перекрытий. Доступные классы: *Polygon*, *MultiPolygon*.
8) Проверка на отсутствие геометрии. Доступные классы: *Polygon*, *MultiPolygon*, *LineString*, *MultiLineString*, *Point*, *MultiPoint*.
9) Проверка на наличие отверстий. Доступные классы: *Polygon*, *MultiPolygon*.

### Реализованные классы
Основным классом является класс *DRGeometryCheck*. Классом, выполняющим функцию enum, является класс *DRCheckTypeList*, он находится в файле *DR_GeometryCheck.py*

### Косяки, о которых я в курсе
1) Вообще есть функционал, отвечающий за точность данных, однако сейчас он захардкожен на 17 знаков после запятой, ибо меньшее количество знаков при расчётах ведёт к косякам;
2) `import *` не всегда есть хорошо, но пока похеру...


## Класс *DRCheckTypeList*
Как уже было сказано выше, представляет собой аналог enum, отвечает за выбор выполняемой проверки:

    #python3
    class DRCheckTypeList:
      selfintersection    = 0
      selfcontact         = 1
      duplicatenodes      = 2
      missingvertex       = 3
      hole                = 4
      duplicategeometry   = 5
      insideobject        = 6
      intersection        = 7
      emptygeometry       = 8

## Пример вызова класса *DRGeometryCheck*
    #python3
    from qgis.core import *
    from qgis.analysis import *
    
    from .DR_SelfContactCheck import DRSelfContact
    from .DR_SelfIntersectionCheck import DRSelfIntersection
    
    project = QgsProject.instance()
    checkTypes = [DRCheckTypeList.selfcontact,
    DRCheckTypeList.selfintersection]
    layers = ["polygon_layer"]
    
    errorList = DRGeometryCheck.runCheck(project, checkTypes, layers)