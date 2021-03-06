#!/usr/bin/python
# -*- coding: utf-8 -*-
# Import python libs
import zettaknight_utils
import zettaknight_globs
import zettaknight_zfs
import sys


def create(*args, **kwargs):

    disk_list = bool(False)
    raid = bool(False)
    luks = bool(False)
    slog = bool(False)
    arg_list = list(args)
    pool = str(zettaknight_globs.pool_name)
    create_config = bool(False)
    ldap_flag = bool(False)
    recordsize = bool(False)
    ashift = bool(False)
    keyfile = bool(False)
    
#    if kwargs:
#        if 'disk_list' in kwargs.iterkeys():
#            disk_list = kwargs['disk_list']
#        if 'raid' in kwargs.iterkeys():
#            raid = kwargs['raid']
#        if 'luks' in kwargs.iterkeys():
#            luks = kwargs['luks']
#        if 'slog' in kwargs.iterkeys():
#            slog = kwargs['slog']
#        if 'create_config' in kwargs.iterkeys():
#            create_config = kwargs['create_config']
#        if 'ldap' in kwargs.iterkeys():
#            ldap_flag = kwargs['ldap']
#        if 'recordsize' in kwargs.iterkeys():
#            recordsize = kwargs['recordsize']
#        if 'ashift' in kwargs.iterkeys():
#            ashift = kwargs['ashift']
#        if 'keyfile' in kwargs.iterkeys():
#            keyfile = kwargs['keyfile']
#            if str(keyfile).lower() == "true":
#                keyfile = zettaknight_globs.identity_file
#                
#    else:
#        kwargs = {}
    
#    for arg in arg_list[0:]:
#        if "=" in arg:
#            k, v = arg.split("=", 1)
#            kwargs[k] = v
#            arg_list.remove(arg)

    if len(arg_list) > 1:
        print("Unexpected arguments found.  Could not parse: {0}\n All arguments other than pool_name should be in key=value pairs.".format(arg_list))
        sys.exit(0)
    
    if arg_list:
        pool = arg_list[0]
    if kwargs:
        if 'disk_list' in kwargs.iterkeys():
            disk_list = kwargs['disk_list']
        if 'raid' in kwargs.iterkeys():
            raid = kwargs['raid']
        if 'luks' in kwargs.iterkeys():
            luks = kwargs['luks']
            if 'keyfile' in kwargs.iterkeys():
                keyfile = kwargs['keyfile']
            else:
                keyfile = zettaknight_globs.identity_file
        if 'slog' in kwargs.iterkeys():
            slog = kwargs['slog']
        if 'create_config' in kwargs.iterkeys():
            create_config = kwargs['create_config']
        if 'ldap' in kwargs.iterkeys():
            ldap_flag = kwargs['ldap']
        if 'recordsize' in kwargs.iterkeys():
            recordsize = kwargs['recordsize']
        if 'ashift' in kwargs.iterkeys():
            ashift = kwargs['ashift']

    create_zpool(pool, disk_list, raid, luks, slog, create_config, ldap_flag, recordsize, ashift, keyfile)

    return


def create_zpool(pool=False, disk_list=False, raid=False, luks=False, slog=False, create_config=False, ldap=False, recordsize=False, ashift=False, keyfile=False):


    ret = {}

    ret[pool] = {}
    ret[pool]['Create Zpool'] = {}

    if not raid:
        raid = "12+2"
    try:
        disks, z_level = raid.split("+")
    except Exception as e:
        ret[pool]['Create Zpool'] = {'1': "{0}\nargument raid must be in x+y format, i.e. 2+1".format(e)}
        zettaknight_utils.parse_output(ret)
        sys.exit(0)

    create_cmd = "bash {0} -d {1} -z {2}".format(zettaknight_globs.zpool_create_script, disks, z_level)

    if disk_list:
        create_cmd = "{0} -f '{1}'".format(create_cmd, disk_list)

    if pool:
        create_cmd = "{0} -p '{1}'".format(create_cmd, pool)

    if luks:
        create_cmd = "{0} -l".format(create_cmd)

    if slog:
        create_cmd = "{0} -s '{1}'".format(create_cmd, slog)
        
    if ldap:
        create_cmd = "{0} -i".format(create_cmd)
        
    if recordsize:
        if any(i in recordsize for i in 'KM'):
            create_cmd = "{0} -r {1}".format(create_cmd, recordsize)
        else:
            print(zettaknight_utils.printcolors("Recordsize must be in number/unit format.  ie. 1M, or 512K", "FAIL"))
            sys.exit(0)
            
    if ashift:
        create_cmd = "{0} -a {1}".format(create_cmd, ashift)
    if keyfile:
        create_cmd = "{0} -k {1}".format(create_cmd, keyfile)

    try:
        ret[pool]['Create Zpool'] = zettaknight_utils.spawn_job(create_cmd)
        zettaknight_utils.parse_output(ret)
        if create_config:
            zettaknight_utils.create_config(pool)
    except Exception as e:
        print(zettaknight_utils.printcolors(e, "FAIL"))
        sys.exit(0)
        
    return ret
