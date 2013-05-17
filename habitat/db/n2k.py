#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: n2k.py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/11 12:42:22

u"""
Includes definition and methods to use the most important elements of the
Natura2000 ontology: HabitatTypes, Species, Sites and Occurrences
"""

from operator import attrgetter

from common import Base
from common import Engine
from common import Session

from species_finder import SpeciesFinder

class Species(Base):
    __tablename__ = 'species'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}
    
    TAXA = ['Kingdom', 'Division', 'Klass', 'Order', 'Family', 'Genus', 'Species']

    def __init__(self, name, url, information):
        self.name = name
        self.url = url
        self.species_id = int(self.url.split("/")[-1])
        if information.has_key('author'):
            self.author = information['author']
        if information.has_key('vernacular'):
            self.vernacular_name = information['vernacular']
        if information.has_key('taxonomy'):
            for taxon in self.TAXA:
                if information['taxonomy'].has_key(taxon):
                    setattr(self, taxon.lower(), information['taxonomy'][taxon])

    @classmethod
    def find_by_name(self, name):
        session = Session()
        try:
            species = session.query(Species).filter(
                Species.name == name
                ).one()
        except:
            # finding species
            spf = SpeciesFinder(name)
            sp_name, sp_url, sp_info = spf.find_species()
            # creating new species
            species = Species(sp_name, sp_url, sp_info)
            # adding species to database
            session.merge(species)
            session.commit()
        finally:
            session.close()
        return species

    def get_associated_habitat_types(self):
        session = Session()
        try:
            species_habitat_links = session.query(HabitatTypesSpecies).filter(
                HabitatTypesSpecies.species_id == self.species_id
            ).all()
            type_ids = [lnk.type_id for lnk in species_habitat_links]
            habitat_types = session.query(HabitatType).filter(
                HabitatType.type_id.in_(type_ids)
                ).all()
        except:
            habitat_types = None
        finally:
            session.close()
        return habitat_types

    def __str__(self):
        return "Species: %s" % self.name

class HabitatType(Base):
    __tablename__ = 'habitat_types'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

    @classmethod
    def find_by_id(self, type_id):
        session = Session()
        try:
            habitat_type = session.query(HabitatType).filter(
                HabitatType.type_id == type_id
                ).one()
        except:
            habitat_type = None
        finally:
            session.close()
        return habitat_type

    def get_typical_species(self):
        session = Session()
        try:
            habitat_species_links = session.query(HabitatTypesSpecies).filter(
                HabitatTypesSpecies.type_id == self.type_id
            ).all()
            species_ids = [lnk.species_id for lnk in habitat_species_links]
            species = session.query(Species).filter(
                Species.species_id.in_(species_ids)
                ).all()
        except:
            species = None
        finally:
            session.close()
        return species

    def __str__(self):
        return "[%s] %s" % (self.type_id, self.shortname)

class Site(Base):
    __tablename__ = 'sites'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

#class SpeciesOccurrence(Base):
#    __tablename__ = 'fk_occurrences'
#    __autoload__ = True
#    __table_args__ = {'autoload_with': Engine}
#
#    def __init__(self):
#        pass

class QuadSpeciesOccurrence(Base):
    __tablename__ = 'quad_species_occurrences'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class MtbSpeciesOccurrence(Base):
    __tablename__ = 'mtb_species_occurrences'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class BioGeographicalRegion(Base):
    __tablename__ = 'biogeo_regions'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

#class SiteMapIntersect(Base):
#    __tablename__ = 'sites_map'
#    __autoload__ = True
#    __table_args__ = {'autoload_with': Engine}
#
#    def __init__(self):
#        pass

class SiteOnMtbTile(Base):
    __tablename__ = 'sites_on_mtb_tiles'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class SiteOnQuadTile(Base):
    __tablename__ = 'sites_on_quad_tiles'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class HabitatTypesSpecies(Base):
    __tablename__ = 'habitat_types_species'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass

class SitesHabitatTypes(Base):
    __tablename__ = 'sites_habitat_types'
    __autoload__ = True
    __table_args__ = {'autoload_with': Engine}

    def __init__(self):
        pass


if __name__ == '__main__':
    
    #sp = Species.find_by_name('Abies alba')
    #print sp
    #sp = Species.find_by_name('Fagus silvativa')
    #print sp

    #spf = SpeciesFinder()
    #session = Session()
    #
    #all_species = session.query(Species).all()
    #
    #for sp in all_species[300:]:
    #    print "Working on '%s'..." % sp.name,
    #    spf.set_search_name(str(sp.name))
    #    sp_name, sp_url, sp_info = spf.find_species()
    #    new_species = Species(sp_name, sp_url, sp_info)
    #    session.merge(new_species)
    #    session.commit()
    #    print "Done"

    from sqlalchemy import and_
    
    tgt = r"D:\work\ms.monina\wp4\florkart_2012_occurrences_eunis_characteristic_species_n2k_areas_germany.txt"
    
    habitat_type = '9120'
    
    output = list()

    session = Session()
    
    habitat_types = session.query(HabitatType).all()
    
    for ht in habitat_types[:]:
    
        habitat_type = ht.type_id
    
        # retrieving all sites with the current habitat type
        sites_with_habitat_type = session.query(SitesHabitatTypes).filter(
            SitesHabitatTypes.type_id == habitat_type).all()
        
        # bailing out if no sites were found
        if not len(sites_with_habitat_type):
            continue

        print "Working on habitat type %s (%s)..." % (habitat_type, ht.shortname)
    
        # retrieving typical species for current habitat type
        typical_species = session.query(HabitatTypesSpecies).filter(
            HabitatTypesSpecies.type_id == habitat_type).all()
    
        if not len(typical_species):
            output.append("%s\t" % habitat_type)
            continue
    
        # reducing sites to site ids
        site_ids = [site.site_id for site in sites_with_habitat_type]
        # reducing species to species ids
        species_ids = [typical_sp.species_id for typical_sp in typical_species]
    
        # retrieving all map tiles that intersect with the previously retrieved sites
        map_intersects = session.query(SiteMapIntersect).filter(
            SiteMapIntersect.site_id.in_(site_ids)).all()
    
        # reducing map tiles to map ids
        map_ids = [map_intersect.map_id for map_intersect in map_intersects]
    
        # retrieving all Florkart occurrences with one of the specified map ids and
        # one of the specified species
        occurrences = session.query(SpeciesOccurrence).filter(
            and_(
                SpeciesOccurrence.map_id.in_(map_ids),
                SpeciesOccurrence.species_id.in_(species_ids)
            )
        ).all()
    
        # reducing occurrences to corresponding map ids
        occurrence_map_ids = [occ.map_id for occ in occurrences]
    
        print "# Habitat type %s (%s) present in the following sites:" % (habitat_type, ht.shortname)
        for site_id in site_ids:
            print "\t+ %s: %s" % (site_id, session.query(Site).filter(Site.site_id == site_id).one().name)
        print "# Typical species for habitat type %s:" % habitat_type
        for species_id in species_ids:
            print "\t+ %s (%d)" % (session.query(Species).filter(Species.species_id == species_id).one().name, species_id)
        print "Found %d occurrences of typical species in %d of a maximum of %d map tiles" % (len(occurrence_map_ids), len(set(occurrence_map_ids)), len(map_ids))
        
        output.append("\t".join((habitat_type, ", ".join(occurrence_map_ids))))
        
        print "================================================================"

    open(tgt, 'wb').write("\n".join(output))
    