#!/usr/bin/env python3

import sys

# Require python 3
if sys.version_info.major < 3:
    msg = "Requires python version 3; attempted with version '{}'".format(
        sys.version_info.major
        )
    raise UserWarning( msg )

import logging
logfmt = '%(levelname)s:%(funcName)s[%(lineno)d] %(message)s'
#loglvl = logging.INFO
loglvl = logging.DEBUG
logging.basicConfig( level=loglvl, format=logfmt )

import collections
import configparser
import os
import pathlib
import pprint
import subprocess
import yaml

# Custom type for R10K source data
R10KSrc = collections.namedtuple( 'R10KSrc', ['basedir', 'environments'] )

# Module level (global) settings
resources = {}

def get_install_dir():
    key = 'install_dir'
    if key not in resources:
        resources[ key ] = pathlib.Path( 
            os.getenv( 'PUP_CUSTOM_DIR', default='/etc/puppetlabs/local' ) )
    return resources[ key ]


def get_cfg():
    key = 'cfg'
    if key not in resources:
        base = get_install_dir()
        confdir = get_install_dir() / 'config' / 'config.ini'
        cfg = configparser.ConfigParser()
        cfg.read( confdir )
        resources[ key ] = cfg
    return resources[ key ]


def get_puppet_environmentpath():
    key = 'puppet_environmentpath'
    if key not in resources:
        cfg = get_cfg()
        cmd = [ cfg['PUPPET']['puppet'] ]
        cmd.extend( 'config print environmentpath --section master'.split() )
        proc = subprocess.run( cmd, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, 
                               check=True,
                               timeout=30
                             )
        resources[ key ] = pathlib.Path( proc.stdout.decode().strip() )
    return resources[ key ]


def get_r10k_sources():
    ''' Get R10K deploy display YAML output
    '''
    key = 'r10k_sources'
    if key not in resources:
        cfg = get_cfg()
        sources = {}
        cmd = [ cfg['R10K']['r10k'], 'deploy', 'display' ]
        proc = subprocess.run( cmd, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, 
                               check=True,
                               timeout=30
                             )
        data = yaml.safe_load( proc.stdout.decode().strip() )
        logging.debug( f'Raw Data:\n{pprint.pformat( data )}\n' )
        # create r10k resource list
        for s in data[':sources']:
            name = s[':name'].strip(':')
            basedir = s[':basedir'].strip(':')
            sources[name] = R10KSrc( basedir=pathlib.Path( basedir ),
                                     environments=s[':environments'] )
        logging.debug( f"SOURCES:\n{pprint.pformat(sources)}\n" )
        resources[ key ] = sources
    return resources[ key ]

def symlink_is_missing_or_wrong( linkname, linktgt ):
    rv = True
    if linkname.is_symlink():
        if linkname.resolve() == linktgt:
            logging.debug( f"existing link '{linkname}' matches expected target '{linktgt}', skipping" )
            rv = False
        else:
            logging.debug( f"existing link '{linkname}' has wrong target, unlinking" )
            linkname.unlink()
    elif linkname.exists():
        if linkname.is_dir():
            raise UserWarning( f"Refusing to replace dir '{linkname}' with a symlink" )
        else:
            logging.debug( f"found existing file '{linkname}', unlinking" )
            linkname.unlink()
    else:
        logging.debug( f"linkname doesn't exist '{linkname}'" )
    return rv


def mk_env_dirs( names ):
    cfg = get_cfg()
    envpath = get_puppet_environmentpath()
    for env in names:
        dirpath = envpath / env
        logging.debug( f"making environment: '{env}' at '{dirpath}'" )
        dirpath.mkdir( exist_ok=True )
        # create symlinks to major contents of production control env
        prod_path = envpath / 'production'
        for f in prod_path.iterdir():
            if f.is_symlink():
                pass
            elif f.is_dir() or f.is_file():
                lname = dirpath / f.name
                ltgt = prod_path / f.name
                try:
                    lname.symlink_to( ltgt )
                except ( FileExistsError ) as e:
                    pass


def find_missing_links( env_list ):
    cfg = get_cfg()
    sources = get_r10k_sources()
    control = sources[ cfg['R10K']['control_repo_name'] ]
    missing_links = {}
    other_repo_names = [ x for x in sources if x != cfg['R10K']['control_repo_name'] ]
    for env in env_list:
        for reponame in other_repo_names:
            rtksrc = sources[ reponame ]
            linkname = control.basedir / env / rtksrc.basedir.name
            # target link is same branch in other repo
            linktgt = rtksrc.basedir / env
            if not linktgt.exists():
                # use default link target ... 'production'
                linktgt = rtksrc.basedir / 'production'
            if symlink_is_missing_or_wrong( linkname, linktgt ):
                logging.debug( 
                    f'Link {env} {rtksrc.basedir.name}: {linkname} -> {linktgt}' )
                missing_links[ linkname ] = linktgt
    return missing_links


def mk_missing_links( links_to_create ):
    for lname, ltgt in links_to_create.items():
        logging.info( f'attempting: {lname} -> {ltgt}')
        try:
            lname.symlink_to( ltgt )
        except (FileExistsError) as e:
            if lname.is_symlink():
                if lname.resolve() != ltgt:
                    raise UserWarning(
                        f"'{lname}' symlink resolves to unexpected target" )
            else:
                raise UserWarning( f"{lname} exists but is not a symlink" )


def run():
    # Read config
    cfg = get_cfg()

    # read r10k yaml from stdin
    sources = get_r10k_sources()

    # Create list of all unique branch names
    branches = []
    for name, repo in sources.items():
        branches.extend( repo.environments )
    env_names = set( branches )
    logging.debug( f'env_names: {pprint.pformat(env_names)}' )

    # R10K only creates an environment dir for branches of control
    # Manually create an environment dir for other repo unique branches
    control = sources[ cfg['R10K']['control_repo_name'] ]
    need_envs = env_names - set( control.environments )
    mk_env_dirs( need_envs )

    # Build map of link sources and targets
    links_to_create = find_missing_links( env_names )
    logging.debug( f"Links to create: '{pprint.pformat(links_to_create)}'" )

    # Create missing links
    mk_missing_links( links_to_create )


if __name__ == '__main__':
    run()
