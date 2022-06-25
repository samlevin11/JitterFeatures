from osgeo import ogr
import random
import time
import os
from typing import Union

# Enable OGR exceptions
ogr.UseExceptions()


def jitterPointFeaturesOGR(in_layer, out_shp, min_dist, max_dist):

    print('Jittering point features..')
    start = time.perf_counter()

    # # Create a new data source in memory for the output layer
    # out_driver = ogr.GetDriverByName('MEMORY')
    # out_datasource = out_driver.CreateDataSource('out_jittered_dsrc')
    # # Copy the input data source to a new layer
    # out_layer = out_datasource.CopyLayer(in_layer, 'out_jittered_lyr')

    # Specify new shapefile data source for output
    out_driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(out_shp):
        out_driver.DeleteDataSource(out_shp)
    out_datasource = out_driver.CreateDataSource(out_shp)
    out_layer = out_datasource.CopyLayer(in_layer, 'out_jittered_lyr')

    print(f'OUT LAYER {out_layer}')
    print(f'{out_layer.GetFeatureCount()} features')

    # Loop through features in the layer
    for feature in out_layer:
        print(f'FEATURE {feature}')

        # Random multiplier for positive or negative shift in direction
        posneg_x = 1 if random.randint(0, 1) == 1 else -1
        posneg_y = 1 if random.randint(0, 1) == 1 else -1
        # Generate random jitter distance for X and Y of coordinates within specified range
        # Multiply by 1 or -1 to shift N/S or E/W at random
        rand_x = random.uniform(min_dist, max_dist) * posneg_x
        rand_y = random.uniform(min_dist, max_dist) * posneg_y

        # Get geometry object from feature, do not modify this object directly
        orig_geom = feature.GetGeometryRef()
        print(f'\tORIG GEOMETRY {orig_geom}')

        # Calculate coordintes of new point with jitter noise
        new_x = orig_geom.GetX() + rand_x
        new_y = orig_geom.GetY() + rand_y
        # Create new point geometry object
        new_point = ogr.Geometry(ogr.wkbPoint)
        # Set point of the new geometry with the new point
        new_point.SetPoint_2D(0, new_x, new_y)
        print(f'\tNEW POINT {new_point}')
        # Set geometry of the feature
        feature.SetGeometryDirectly(new_point)
        # Set feature within the layer
        out_layer.SetFeature(feature)

    print('JITTER POINTS RUN TIME: {} seconds'.format(time.perf_counter() - start))

    return out_shp


if __name__ == '__main__':
    in_feat_class = os.path.join(os.path.dirname(__file__), r'TestData/points100.shp')
    out_feat_class = os.path.join(os.path.dirname(__file__), r'TestData/Output/points100_jitter00.shp')

    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_source = driver.Open(in_feat_class)
    print(f'INPUT DATA SOURCE {data_source}')
    print(data_source.GetName())
    layer = data_source.GetLayer(0)
    print(f'INPUT LAYER {layer}')

    min_d = 1500
    max_d = 5000

    jitterPointFeaturesOGR(layer, out_feat_class, min_d, max_d)
