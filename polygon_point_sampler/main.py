#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from shapely.geometry import Polygon
from shapely.wkt import loads

from sampler import CentroidSampler
from sampler import RepresentativePointSampler
from sampler import RegularGridSampler
from sampler import UniformRandomSampler
from sampler import SkeletonLineSampler

if __name__ == '__main__':

    py = Polygon(((0., 0.), (0., 1.), (1., 1.), (1., 0.)))

    wkt_src = R"_data\p.txt"
    py = loads(open(wkt_src).read())
    print(py)

    t0 = time.time()

    print("Centroid sampling:")
    cs = CentroidSampler(py)
    cs.perform_sampling()
    cs.print_samples()

    print("Representative point sampling:")
    ls = RepresentativePointSampler(py)
    ls.perform_sampling()
    ls.print_samples()

    print("Regular grid sampling:")
    rs = RegularGridSampler(py, 500, 500)
    rs.perform_sampling()
    rs.print_samples()

    print("Uniform random sampling:")
    us = UniformRandomSampler(py, 25)
    # us.set_sample_count(500)
    us.perform_sampling()
    us.print_samples()

    # us.print_triangles()

    print("Skeleton line sampling:")
    sls = SkeletonLineSampler(py)
    sls.perform_sampling()
    sls.print_samples()
    print(sls.skel)

    print("elapsed time: %f" % (time.time() - t0))
