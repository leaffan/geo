#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A class to allow for easy reading and writing of *ini*-like
configuration files.
"""

import os

import configparser


class CfgUtility():

    def __init__(self, cfg_file, default_section='Options'):
        self.cfg_file = cfg_file
        self.cfg = configparser.RawConfigParser()
        self.has_changed = False
        self.default_section = default_section

        # checking if config file exists
        if os.path.exists(self.cfg_file):
            self.cfg.read(self.cfg_file)
        # creating it otherwise
        else:
            open(self.cfg_file, 'wb').close()

        # creating default section if it doesn't exist
        if not self.cfg.has_section(self.default_section):
            self.cfg.add_section(self.default_section)
            self._write_changes()

    def set_value(self, value, key, section="", flush=False):
        """
        Set a configuration value for given key in given section.
        """
        if self.has_changed:
            self._reread_cfg_file()
        if not section:
            section = self.default_section
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)
        self.cfg.set(section, key, value)
        if flush:
            self._write_changes()

    def get_options(self, section=""):
        """
        Retrieve all options in a given section.
        """
        if self.has_changed:
            self._reread_cfg_file()
            self.has_changed = False
        if not section:
            section = self.default_section
        if self.cfg.has_section(section):
            return self.cfg.options(section)
        else:
            return []

    def remove_option(self, section, option, flush=True):
        if self.has_changed:
            self._reread_cfg_file()
        if not section:
            section = self.default_section
        self.cfg.remove_option(section, option)
        if flush:
            self._write_changes()

    def remove_options(self, section="", flush=True):
        """Remove all options in a given section."""
        if not section:
            section = self.default_section
        for option in self.get_options(section):
            self.cfg.remove_option(section, option)
        if flush:
            self._write_changes()

    def get_value(self, key, section=""):
        """Get a configuration value for given key in given section."""
        if self.has_changed:
            self._reread_cfg_file()
            self.has_changed = False
        if not section:
            section = self.default_section
        if self.cfg.has_option(section, key):
            value = self.cfg.get(section, key)
        else:
            value = None
        return value

    def _write_changes(self):
        u"""Write changes to configuration file."""
        cfg_fh = open(self.cfg_file, 'wb')
        self.cfg.write(cfg_fh)
        cfg_fh.close()
        self.has_changed = True

    def _reread_cfg_file(self):
        u"""Re-read configuration file."""
        self.cfg.read(self.cfg_file)
        self.has_changed = False

    def _dump(self):
        res = list()
        for section in self.cfg.sections():
            res.append(section)
            for option in self.get_options(section):
                res.append("".join(
                    ("    ", option, " : ", self.cfg.get(section, option))))
        return "\n".join(res)


if __name__ == '__main__':
    pass
