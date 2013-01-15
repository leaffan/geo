#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: spectrum.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/09/12 11:04:40

u"""
A simple class to contain Spectrum objects, i.e. structured lists of reflectance
or DN values extracted from an image or acquired in-situ. Spectrums consist of a
number of SingleBandMeasurements, i.e. sub-objects that represent a reflectance
or DN measurement for a certain band or wavelength.
"""

from types import DictType, NoneType

class Spectrum(object):
    u"""
    A class to contain Spectrum objects, i.e. structured lists of reflectance
    or DN values extracted from an image or acquired in-situ.
    """
    
    def __init__(self, spectrum_id = '', location = ('','')):
        u"""
        Initialize a Spectrum object using the specified id and location
        (usually given by a coordinate pair of x and y).
        """
        self.id = spectrum_id
        self.x, self.y = location
        # setting default attributes
        self.description = ''
        self.values = dict()
        self.attributes = dict()
        # the pixel neighborhood for which the spectrum is valid
        self.neighborhood = 1
        self.context_range = 1
        # the type of neighborhood for which the spectrum is valid, i.e.
        # 'square' or 'circle' neighborhood
        self.neighborhood_type = ''
        self.context_type = ''
    
    def set_id(self, spectrum_id):
        u"""
        Set the id of the spectrum, usually related to the location
        where it is taken.
        """
        self.id = spectrum_id

    def set_location(self, location):
        u"""
        Set the location of the spectrum represented by a coordinate pair.
        """
        self.x, self.y = location

    def set_neighborhood(self, neighborhood):
        u"""
        Set the pixel neighborhood for which the spectrum is taken.
        """
        self.neighborhood = neighborhood

    def set_context_range(self, context_range = 1):
        self.context_range = context_range
    
    def set_context_type(self, context_type = 'square'):
        self.context_type = context_type
        self.neighborhood_type = context_type

    def set_neighborhood_type(self, neighborhood_type):
        u"""
        Set the type of the neighborhood of the spectrum, i.e. 'square' or
        'circle'.
        """
        self.neighborhood_type = neighborhood_type

    def set_description(self, description):
        u"""
        Set an arbitrary description of the spectrum.
        """
        self.description = description

    def set_source(self, source):
        u"""
        Set the source of the spectrum, i.e. an image that is part of a larger
        series or a flight strip number.
        """
        self.source = source

    def get_value(self, band_id):
        u"""
        Retrieve a single band measurement for the specified band id.
        """
        if self.values.has_key(band_id):
            return self.values[band_id]
        else:
            return None
    
    def set_value(self, band_id, value, overwrite = False):
        u"""
        Set a single band measurement using the specified value for the given
        band id.
        """
        if self.values.has_key(band_id) and not overwrite:
            print "Will not overwrite existing value for band_id '%s'" % str(band_id)
        else:
            self.values[band_id] = SingleBandMeasurement(self.id, band_id, value)

    def all_values(self):
        u"""
        Return the whole spectrum using their actual values.
        """
        return [v.__get__() for v in self.values.values()]

    def set_invalid(self, band_id):
        u"""
        Declare the single band measurement of the specified band id as invalid.
        """
        self.set_value(band_id, None)

    def get_attribute(self, attribute_id):
        u"""
        Get an attribute that has been added to the spectrum data.
        """
        if self.attributes.has_key(attribute_id):
            return self.attributes[attribute_id]

    def set_attribute(self, attribute_id, value):
        u"""
        Set an attribute to accompany the spectrum data.
        """
        self.attributes[attribute_id] = value

    def __str__(self, include_no_data = True, include_source = True, include_raw_data = True):
        u"""
        Return a string representation of the spectrum, either with invalid
        data and/or the source image included or not.
        """
        if include_source:
            prefix = "\t".join([str(x) for x in [self.id, self.source, self.x, self.y]])
        else:
            prefix = "\t".join([str(x) for x in [self.id, self.x, self.y]])
        if len(self.attributes) > 0:
            prefix = "\t".join([prefix] + [str(self.get_attribute(x)) for x in sorted(self.attributes.keys())])
        # if a circle neighborhood was used for extraction, add the number of
        # pixels to be found within the circle to the output
        if self.neighborhood_type == "circle":
            prefix = "\t".join([prefix] + [str(self.values.values()[0].count)])
        if include_no_data:
            return "\t".join(([prefix] + [str(v) for v in self.values.values()]))
        else:
            return "\t".join(([prefix] + [str(v) for v in self.values.values() if v.__get__() is not None]))

class SingleBandMeasurement(object):
    u"""
    A class to contain SingleBandMeasurements, i.e. objects that represent a
    single reflectance or DN value measurement for a certain band or wavelength.
    Multiple SingleBandMeasurements constitute a Spectrum object.
    """
    
    NO_DATA_VALUE = -0.01
    
    def __init__(self, loc_id, band_id, value):
        
        # storing location and band information
        self.loc_id = loc_id
        self.band_id = band_id
        
        # checking whether we received an invalid value
        if type(value) is NoneType:
            self.raw = None
            self.mean = None
            self.std_dev = None
            self.neighborhood = None
        # checking whether we're operating in a nxn-neighborhood (n > 1), which
        # is indicated by a value aggregation represented by a dictionary object
        elif type(value) is DictType:
            self.raw = value['raw']
            self.min = value['min']
            self.max = value['max']
            self.mean = value['mean']
            self.std_dev = value['std_dev']
            self.count = value['count']
            if value.has_key('neighborhood'):
                self.neighborhood = value['neighborhood']
                self.context_range = self.neighborhood
            if value.has_key('context_range'):
                self.context_range = value['context_range']
                self.neighborhood = self.context_range
            if value.has_key('neighborhood_type'):
                self.neighborhood_type = value['neighborhood_type'].lower()
                self.context_type = self.neighborhood_type
            if value.has_key('context_type'):
                self.context_type = value['context_type']
                self.neighborhood_type = self.context_type
        # otherwise we received a single value representing a single pixel
        else:
            self.raw = value
            self.mean = self.min = self.max = value
            self.std_dev = 0
            self.neighborhood = 1
            self.count = 1

    def __get__(self):
        if self.neighborhood is None:
            return None
        elif self.neighborhood > 1:
            return self.mean
        else:
            return self.raw

    def __str__(self):
        if self.neighborhood is None:
            return str(self.NO_DATA_VALUE)
        elif self.neighborhood > 1:
            # including values of all pixels contained by the region of interest
            # if we're operating in a square neighborhood
            if self.neighborhood_type == 'square':
                raw = "\t".join([str(f) for f in self.raw])
            # including minimum and maximum values of all pixels contained by
            # the region of interest if we're operating in a circle neighborhood
            elif self.neighborhood_type == 'circle':
                raw = "\t".join([str(f) for f in [self.min, self.max]])
            # including mean and standard deviation by default
            mean = str(self.mean)
            std_dev = str(self.std_dev)
            return ("\t".join((raw, mean, std_dev)))
        else:
            # including its value if we're operating on a single pixel level 
            return (str(self.raw))
