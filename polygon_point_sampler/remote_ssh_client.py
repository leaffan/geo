#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File: ....py
# Author: Markus Reinhold
# Contact: leaffan@gmx.net
# Creation Date: 2012/03/19 14:33:11

u"""
... Put description here ...
"""

from types import StringType, ListType

import gzip
import os
import paramiko

from _utils.cfg_utility import CfgUtility

class RemoteSSHClient():
    
    def __init__(self, cfg_file):
        # TODO: move sensitive information to config file
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.cfg = CfgUtility(r"D:\tmp\_test.cfg")
        host = self.cfg.get_value('host')
        username = self.cfg.get_value('username')
        password = self.cfg.get_value('password')

        self.ssh.connect(host, username = username, password = password)

    def upload_file(self, local_path, remote_dir = '', gzipped = False):
        self.ftp = self.ssh.open_sftp()
        if remote_dir:
            if self.rexists(self.ftp, remote_dir):
                try:
                    self.ftp.chdir(remote_dir)
                except:
                    return None
            remote_path = "/".join((self.ftp.getcwd(), os.path.basename(local_path)))
            if self.rexists(self.ftp, remote_path):
                print "file already exists..."
            else:
                self.ftp.put(local_path, remote_path)
        return remote_path

    def download_file(self, remote_path, local_path = '', gzipped = False):
        self.ftp = self.ssh.open_sftp()
        if not self.rexists(self.ftp, remote_path):
            print "remote file '%s' does not exist" % remote_path
            return
        #self.ftp.get(remote_path, local_path, self.print_bytes)
        self.ftp.get(remote_path, local_path)

    def print_bytes(self, trf, total):
        print "%d / %d done..." % (trf, total)

    def execute_commands(self, cmds):
        if type(cmds) == StringType:
            cmd_chain = cmds
        elif type(cmds) == ListType:
            cmd_chain = ";".join(cmds)
        stdin, stdout, stderr = self.ssh.exec_command(cmd_chain)
        return cmd_chain, stdout.readlines(), stderr.readlines()
        #result.append((cmd_chain, stdout.readlines(), stderr.readlines()))
        #
        #
        #for c, o, e in result:
        #    print c
        #    print "".join(o)
        #    print "".join(e)
        #    print "======================="

    def rexists(self, sftp, path):
        try:
            sftp.stat(path)
        except IOError, e:
            if e[0] == 2:
                return False
            raise
        else:
            return True

    def gzip_file(self, local_path):
        import tempfile
        tmp = tempfile.mkstemp(suffix = '.gz', prefix = os.path.basename(local_path))
        print tmp
        f = gzip.open(tmp[1], 'wb')
        f.write(open(local_path).read())
        f.close()

if __name__ == '__main__':

    from _utils.cfg_utility import CfgUtility
    
    cfg = CfgUtility(r"D:\tmp\_test.cfg")
    host = cfg.get_value('host')
    username = cfg.get_value('username')
    password = cfg.get_value('password')
    
    local_path = r"D:\tmp\pinguicula_log.txt"
    
    rsc = RemoteSSHClient(host, username, password)

    #rsc.upload_file(r"D:\tmp\pinguicula_log.txt", "_tmp")
    
    #rsc.gzip_file(local_path)
    
    
    
    rsc.execute_commands(['cd _triangle', './triangle --help'])
    
    