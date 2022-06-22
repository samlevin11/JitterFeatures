import arcpy
import random
import time
import os


def jitterPoints(in_feature_class, out_feature_class, min_dist, max_dist):
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

    # Cast an update cursor and loop through rows (features)
    with arcpy.da.UpdateCursor(out_feature_class, ['SHAPE@']) as cursor:
        for row in cursor:
            # Loop through parts of each feature's geometry
            for part in row[0]:
                # Random multiplier for positive or negative shift in direction
                posneg_x = 1 if random.randint(0, 1) == 1 else -1
                posneg_y = 1 if random.randint(0, 1) == 1 else -1
                # Generate random jitter distance for X and Y of coordinates within specified range
                rand_x = random.uniform(min_dist, max_dist)
                rand_y = random.uniform(min_dist, max_dist)
                # Update feature geometry with new point feature
                row[0] = arcpy.PointGeometry(arcpy.Point(part.x + rand_x * posneg_x,
                                                         part.y + rand_y * posneg_y))
            cursor.updateRow(row)

    print('JITTER POINTS RUN TIME: {} seconds'.format(time.perf_counter() - start))


if __name__ == '__main__':
    in_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPoints.shp')
    out_feat_class = os.path.join(os.path.dirname(__file__), r'TestData\testPoints_mod4.shp')

    min_d = 1500
    max_d = 5000

    jitterPoints(in_feat_class, out_feat_class, min_d, max_d)
