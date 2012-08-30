#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/06/11 13:38:42

u"""
... Put description here ...
"""

import urllib2
import lxml.html
import Levenshtein

class SpeciesFinder():

    URL_PREFIX = r"http://eunis.eea.europa.eu/species-names-result.jsp?typeForm=0&pageSize=300&showGroup=true&showFamily=true&showOrder=true&showScientificName=true&searchVernacular=false&sort=3&ascendency=1&showValidName=true&relationOp=2&searchSynonyms=True&submit=Search&scientificName="

    def __init__(self, search_name = ''):
        self.search_name = search_name
        self.verbose = False
    
    def set_search_name(self, search_name):
        self.search_name = search_name

    def find_species(self, verbose = False):
        u"""
        Searches the EUNIS database for a previously defined species name and
        retrieves accompanying information.
        """
        
        # setting verbosity
        self.verbose = verbose
        
        # querying species name in EUNIS database
        query_result = self.query_species()
        
        # bailing out if nothing at all was found
        if not query_result:
            return None, None, None
        
        # if more than one result was found
        if len(query_result) > 1:
            # finding best match for species name
            (sp_name, sp_type, sp_url), similarity = self.find_best_match(query_result)
        else:
            # otherwise retrieving species info from first row of the query result
            (sp_name, sp_type, sp_url) = self.get_species_info_from_row(query_result[0])

        # retrieving valid species name if a synonym was queried
        if sp_type.lower() == "(synonym)":
            sp_name, sp_url = self.find_valid_name_for_synonym(sp_name, sp_url)

        # retrieving all available information for found valid species name
        sp_info = self.get_all_information(sp_name, sp_url)

        # finally returning all information
        return sp_name, sp_url, sp_info

    def query_species(self):
        u"""
        Searches the EUNIS database for the specified species name. Usually a
        list of (at least) one or (more likely) more results is returned that
        can be later used to retrieve species information from it.
        """
        if not self.search_name:
            return list()
        
        # building query string and url
        query_str = "+".join(self.search_name.split())
        query_url = "".join((self.URL_PREFIX, query_str))
        # opening query url
        query_conn = urllib2.urlopen(query_url)

        # parsing url content
        self.query_doc = lxml.html.parse(query_conn).getroot().get_element_by_id('content')
        self.query_doc.make_links_absolute()

        # retrieving table rows containing the query results from page content
        query_result = self.query_doc.xpath("//table[@summary='Search results']/tbody/tr")
        
        return query_result

    def find_best_match(self, search_results):
        u"""
        Finds the best match from a list of species name in comparison to a
        specified species name to search for. Uses a Levenshtein algorithm for
        string comparison to accomplish this task.
        """
        # defining initial match state
        best_match = ((), -1.0)
        # finding the column containing species names from
        # the table of query results
        idx = self.find_species_column()
        # iterating over all rows
        for row in search_results:
            # retrieving species name, type and url from current table row
            sp_name, sp_type, sp_url = self.get_species_info_from_row(row)
            # calculating similarity ration between current species name and
            # species to name to find
            ratio = Levenshtein.ratio(self.search_name, sp_name)
            # replacing previous best match with current match if the similarity
            # is higher
            #print "\t", sp_name, ratio, best_match[-1]
            if ratio > best_match[-1]:
                best_match = ((sp_name, sp_type, sp_url), ratio)
            # replacing previous best match with current match if similarity is
            # equal only if we can replace it with a valid species name
            elif ratio == best_match[-1]:
                if not sp_type: # i.e. not *(synomym)*,...
                    best_match = ((sp_name, sp_type, sp_url), ratio)
        else:
            if self.verbose:
                print "+ Best match for '%s': '%s' %s [%s]" % (self.search_name, best_match[0][0], best_match[0][1], best_match[0][2])
            return best_match

    def find_species_column(self):
        u"""
        Find a column (represented as index) containing species names from a
        given table of query results using *Scientific name* as keyword to
        search for in the table header.
        """
        table_header = self.query_doc.xpath("//table[@summary='Search results']/thead/tr/th")
        i = 0
        for th in table_header:
            if th.text_content().strip() == 'Scientific name':
                idx = i
                break
            i += 1
        return idx

    def get_species_info_from_row(self, row):
        u"""
        Retrieve species information, i.e. name, type and url from a specified
        row extracted from a table of query results.
        """
        # finding column containing species information
        idx = self.find_species_column()
        # retrieving corresponding html elements
        species_element = row.xpath("./td")[idx]
        species_link_element = species_element.xpath("./a")[0]
        
        # retrieving species url, name and type from extracted elements
        sp_url = species_element.xpath("./a")[0].attrib['href']
        sp_name = species_link_element.text_content().strip()
        sp_type = species_link_element.tail.strip()
        
        return sp_name, sp_type, sp_url

    def find_valid_name_for_synonym(self, synonym, synonym_url):
        u"""
        Find a valid species name for the given synonym.
        """
        # accessing synonym url and parsing page contents
        species_conn = urllib2.urlopen(synonym_url)
        species_doc = lxml.html.parse(species_conn).getroot().get_element_by_id('content')
        species_doc.make_links_absolute()

        # retrieving valid name and url from page heading
        heading = species_doc.xpath("//h1[@class='documentFirstHeading']")[0]
        valid_name = heading.xpath("./span/a/strong")[0].text_content().strip()
        tgt_url = heading.xpath("./span/a")[0].attrib['href']

        # retrieving author information
        author = self.get_author(species_doc)

        if self.verbose:
            print "+ '%s' (%s) is a synonym of '%s': [%s]" % (synonym, author, valid_name, tgt_url)
        
        return valid_name, tgt_url

    def get_all_information(self, species_name, url):
        # accessing species url and parsing page contents
        species_conn = urllib2.urlopen(url)
        species_doc = lxml.html.parse(species_conn).getroot().get_element_by_id('content')
        species_doc.make_links_absolute()
        
        information = dict()
        information['vernacular'] = self.get_vernacular_name(url)
        information['author'] = self.get_author(species_doc)
        information['rank'], information['taxonomy'] = self.get_taxonomy(species_doc)
        return information

    def get_vernacular_name(self, species_url, lang = 'de'):
        u"""
        Retrieve vernacular name for species specified by its EUNIS url.
        """
        
        languages = dict()
        languages['de'] = 'german'
        
        if species_url.endswith('/'):
            join_str = ''
        else:
            join_str = '/'
        vernacular_url = join_str.join((species_url, 'vernacular'))

        vernacular_conn = urllib2.urlopen(vernacular_url)
        vernacular_doc = lxml.html.parse(vernacular_conn).getroot().get_element_by_id('content')
        vernacular_doc.make_links_absolute()

        vernacular_info = vernacular_doc.xpath("//table[@class='listing fullwidth']/tbody/tr")
        
        for row in vernacular_info:
            cells = row.xpath("//td")
            row_lang = cells[4].text.strip().lower()
            if languages[lang] == row_lang:
                vernacular_name = cells[3].text.strip()
                return vernacular_name
        
        return None

    def get_author(self, species_doc):
        u"""
        Retrieve author information from a parsed species page.
        """
        author_info = species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[2]
        if not author_info.text is None:
            author = author_info.text.strip()
        else:
            author = ''
        
        return author

    def get_taxonomy(self, species_doc):
        taxonomic_rank = species_doc.xpath("//table[@class='datatable fullwidth']/tr/td")[1].text.strip().lower()
        
        if not taxonomic_rank.lower().endswith("species"):
            return None
        tax_info = species_doc.xpath("//table[@class='datatable fullwidth'][2]/tbody/tr")
        tax_dict = dict()
        
        for row in tax_info:
            level = row.xpath("./td")[0].text_content().strip()
            if level == "Class":
                level = "Klass"
            info = row.xpath("./td")[1].text_content().strip()
            tax_dict[level] = info

        return taxonomic_rank, tax_dict

if __name__ == '__main__':
    
    spf = SpeciesFinder()
    
    search_names = ['Betula pendula', 'Betula pubescens',
                    'Betula alba', 'Betula concina']
    
    for search_name in search_names[:]:
        spf.set_search_name(search_name)
        print "Searching for: '%s'" % (search_name)
        sp_name, sp_url, sp_info = spf.find_species(True)
        #print "-> %s [%s]" % (sp_name, sp_url)
        #print spf.get_all_information(sp_name, sp_url)
        print spf.get_vernacular_name(sp_url)
        print "=============================================================="
