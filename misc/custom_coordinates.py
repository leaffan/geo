#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: custom_coordinates.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/28 11:44:54

u"""
Classes to represent geographic coordinates using components of degrees,
minutes, and seconds.
A convenient way to add dms coordinates as well as to substract them from each
other is added by corresponding overloaded operators.
TODO:
    - add constraints, i.e. latitude necessarily smaller than 90 degrees
    - allow for hemisphere changes
"""

import decimal as libdecimal
from decimal import Decimal as D

class GeographicCoordinates(object):
    def __init__(self, latitude = None, longitude = None):
        if latitude is None:
            self.latitude = DMSCoordinate(0, 0)
        else:
            self.latitude = latitude
        if longitude is None:
            self.longitude = DMSCoordinate(0, 0)
        else:
            self.longitude = longitude

    def __str__(self):
        return "[%s / %s]" % (self.latitude.__str__(), self.longitude.__str__())

class DMSCoordinate(object):
    def __init__(self, degrees, minutes, seconds = 0, hemisphere = ''):
        self.degrees = degrees
        self.minutes = minutes
        self.seconds = seconds
        if len(hemisphere) == 1 and hemisphere.upper() in ['N', 'S', 'E', 'W']:
            self.hemisphere = hemisphere.upper()
        else:
            self.hemisphere = None
    
    @classmethod
    def from_decimal(self, decimal_degrees, hemisphere = ''):
        degrees = D(int(decimal_degrees))

        decimal_minutes = libdecimal.getcontext().multiply((D(str(decimal_degrees)) - degrees).copy_abs(), D(60))
        minutes = D(int(decimal_minutes))
        seconds = libdecimal.getcontext().multiply((decimal_minutes - minutes), D(60))

        return DMSCoordinate(degrees, minutes, seconds, hemisphere)

    @classmethod
    def to_decimal(self, degrees, minutes, seconds):
        decimal = D(0)
        deg = D(str(degrees))
        min = libdecimal.getcontext().divide(D(str(minutes)), D(60))
        sec = libdecimal.getcontext().divide(D(str(seconds)), D(3600))
    
        if (degrees >= D(0)):
            decimal = deg + min + sec
        else:
            decimal = deg - min - sec
        
        return libdecimal.getcontext().normalize(decimal)

    def convert_to_decimal(self):
        return DMSCoordinate.to_decimal(self.degrees, self.minutes, self.seconds)

    def __str__(self):
        output = "%03g°%02g'%02g\"" % (self.degrees, self.minutes, self.seconds)
        if self.hemisphere is not None:
            output = "%s%s" % (output, self.hemisphere)
        return output

    def __add__(self, other):
        sum_seconds = self.seconds + other.seconds
        minute_overflow = 0
        while sum_seconds >= 60:
            sum_seconds -= 60
            minute_overflow += 1

        sum_minutes = self.minutes + other.minutes + minute_overflow
        degree_overflow = 0
        while sum_minutes >= 60:
            sum_minutes -= 60
            degree_overflow += 1
    
        sum_degree = self.degrees + other.degrees + degree_overflow
        
        return DMSCoordinate(sum_degree, sum_minutes, sum_seconds, self.hemisphere)

    def __sub__(self, other):
        diff_seconds = self.seconds - other.seconds
        minute_overflow = 0
        while diff_seconds < 0:
            diff_seconds += 60
            minute_overflow += 1
        
        diff_minutes = self.minutes - other.minutes - minute_overflow
        degree_overflow = 0
        while diff_minutes < 0:
            diff_minutes += 60
            degree_overflow += 1
        
        diff_degree = self.degrees - other.degrees - degree_overflow
        
        return DMSCoordinate(diff_degree, diff_minutes, diff_seconds, self.hemisphere)

if __name__ == '__main__':
    
    dms = DMSCoordinate.from_decimal(12.232323)
    print dms
    print dms.convert_to_decimal()
    print DMSCoordinate.to_decimal(dms.degrees, dms.minutes, dms.seconds)

    latlon = GeographicCoordinates(DMSCoordinate.from_decimal(52, 'n'), DMSCoordinate(12, 30, hemisphere = 'e'))
    
    print latlon
