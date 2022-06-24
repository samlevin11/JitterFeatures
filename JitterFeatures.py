import arcpy
import random
import time
import os
from typing import Union


def jitterPart(part: Union[arcpy.PointGeometry, arcpy.Array],
               rand_x: float, rand_y: float) -> arcpy.Array:
    """
    Jitters a feature part by specified values.
    Iterates through each point in the specified part and applies the specified jitter values to each coordinate.

    :param part: Iterable of arcpy.Point geometries
    :param rand_x: Feature unique random distance to shift on x-axis (E/W)
    :param rand_y: Feature unique random distance to shift on y-axis (N/S)
    :return: New arcpy.Array of jittered coordinates, shifted by the specified random values
    """

    # Initialize new arcpy.Array object for the new part geometry
    new_part = arcpy.Array()

    # Loop through points in each part (array)
    for point in part:
        print(f'POINT {point}')

        # For each point, modify coordinates based on random jitter values
        # Append new point to the new part array
        new_part.append(arcpy.Point(point.X + rand_x,
                                    point.Y + rand_y))

    return new_part


def jitterFeatures(in_feature_class: str, out_feature_class: str,
                   min_dist: Union[int, float], max_dist: Union[int, float]) -> str:
    """
    Simple function for jittering the locations of points.
    Can be used to protect specific locations of sensitive data while preserving their general location.
    Points are moved randomly within a specified distance.
    The minimum and maximum distance parameters allows minimum and maximum distances to move points to be specified.

    :param in_feature_class: Path to input feature class
    :param out_feature_class: Path to output feature class
    :param min_dist: Minimum distance to move point
    :param max_dist: Maximum distance to move point
    :return: Path to output, randomized, features
    """

    print('Randomizing point features..')
    start = time.perf_counter()

    # Copy input feature class to a new specified feature class -- do not modify input data
    arcpy.CopyFeatures_management(in_feature_class, out_feature_class)

    # Dictionary to lookup the correct arcpy geometry class based on the input feature class shape type
    geometry_lookup = {
        'Polygon': arcpy.Polygon,
        'Polyline': arcpy.Polyline,
        'Point': arcpy.PointGeometry,
        'Multipoint': arcpy.Multipoint
    }

    # Store shape type of input feature class, ensure it is a supported geometry type
    shape_type = arcpy.Describe(in_feature_class).shapeType
    if shape_type not in geometry_lookup.keys():
        raise TypeError('Feature class of shape type {} not supported'.format(shape_type))

    # Cast an update cursor
    with arcpy.da.UpdateCursor(out_feature_class, ['SHAPE@']) as cursor:
        # Loop through rows (features)
        for row in cursor:
            print(f'\nROW {row[0]}')

            # Random multiplier for positive or negative shift in direction
            posneg_x = 1 if random.randint(0, 1) == 1 else -1
            posneg_y = 1 if random.randint(0, 1) == 1 else -1
            # Generate random jitter distance for X and Y of coordinates within specified range
            # Multiply by 1 or -1 to shift N/S or E/W at random
            rand_x = random.uniform(min_dist, max_dist) * posneg_x
            rand_y = random.uniform(min_dist, max_dist) * posneg_y

            # If the geometry type is arcpy.Point, immediately loop through points
            # PointGeometry features do not have parts
            if isinstance(row[0], arcpy.PointGeometry):
                # New geometry is returned as an arcpy.Array, extract single arcpy.Point, assign as new geometry
                new_geom = jitterPart(row[0], rand_x, rand_y)[0]

            else:
                # Initialize new arcpy.Array object for the new feature geometry
                new_geom = arcpy.Array()

                # Loop through parts of each feature's geometry (array object)
                for part in row[0]:
                    print(f'PART {part}')

                    new_part = jitterPart(part, rand_x, rand_y)

                    # Once all points in the part have been recalculated, append the part to the row array
                    new_geom.append(new_part)

            # Once all parts in the geometry have been processed, replace feature geometry
            # Cast as the correct geometry type based on the geometry_lookup
            row[0] = geometry_lookup[shape_type](new_geom)
            # Finally, update the row
            cursor.updateRow(row)

    print('JITTER POINTS RUN TIME: {} seconds'.format(time.perf_counter() - start))

    # Return output jittered feature class
    return out_feature_class


if __name__ == '__main__':
    # in_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPoints.shp')
    # out_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPoints_mod4.shp')

    in_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPolygons.shp')
    out_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPolygons_mod3.shp')

    min_d = 1500
    max_d = 5000

    jitterFeatures(in_feat_class, out_feat_class, min_d, max_d)
