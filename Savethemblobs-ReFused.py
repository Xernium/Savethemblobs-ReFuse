#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Savethemblobs-ReFused.py
#   A simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally and on Cydia server.
#   And now also grabs blobs already cached on Cydia servers to save them locally.
#
# Copyright (c) 2013 Neal <neal@ineal.me>
#   Updated 2016 iApeiron
#       deprecated and obsolete APIs removed
#   Upgraded/Updated 2018
#       New TSS-Saving Solution crawler by /u/1Conan
#       Completely reworking the entire thing :P
#
# examples:
#   savethemblobs.py 1050808663311 iPhone3,1
#   savethemblobs.py 0x000000F4A913BD0F iPhone3,1 --overwrite
#   savethemblobs.py 1050808663311 n90ap --skip-cydia

from __future__ import absolute_import
from __future__ import print_function
import sys, os, argparse
import requests
import json
import six
import re

# There won't be any new 32 bit devices with this technology
__definedshshdevices__ = [
    'iPhone1,1', 'iPhone1,2', 'iPhone2,1', 'iPhone3,1', 'iPhone3,2', 'iPhone3,3', 'iPhone4,1', 'iPhone5,1', 'iPhone5,2', 'iPhone5,3', 'iPhone5,4',
    'iPad1,1', 'iPad2,1', 'iPad2,2', 'iPad2,3', 'iPad2,4', 'iPad2,5', 'iPad2,6', 'iPad2,7',
    'iPad3,1', 'iPad3,2', 'iPad3,3', 'iPad3,4', 'iPad3,5', 'iPad3,6',
    'iPod1,1', 'iPod2,1', 'iPod3,1', 'iPod4,1', 'iPod5,1'
]

__version__ = '2.2'

USER_AGENT = 'savethemblobs/%s' % __version__

def firmwares_being_signed(device):
    url = 'https://api.ipsw.me/v2.1/firmwares.json'
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    tmp1 = json.loads((r.text))
    return tmp1['devices'][device]

def firmwares(device):
    url = 'http://api.ineal.me/tss/%s/all' % (device)
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    return r.text

def beta_firmwares(device):
    url = 'http://api.ineal.me/tss/beta/%s/all' % (device)
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    return r.text

def tss_request_manifest(board, build, ecid, cpid=None, bdid=None):
    url = 'http://api.ineal.me/tss/manifest/%s/%s' % (board, build)
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    return r.text.replace('<string>$ECID$</string>', '<integer>%s</integer>' % (ecid))

def request_blobs_from_apple(verbose_level, board, build, ecid, cpid=None, bdid=None):
    d = tss_request_manifest(board, build, ecid, cpid, bdid)
    if verbose_level>3:
        print(d)
    url = 'http://gs.apple.com/TSS/controller?action=2'
    r = requests.post(url, headers={'User-Agent': 'InetURL/1.0', 'Accept-Encoding': '*/*', 'Content-type': 'text/xml; charset="utf-8"'}, data=d)
    if not r.status_code == requests.codes.ok:
        return { 'MESSAGE': 'TSS HTTP STATUS:', 'STATUS': r.status_code }
    if verbose_level>=1:
        print('MESSAGE: TSS HTTP STATUS: %s' % (r.status_code ))
    if verbose_level>=2:
        print(r.text)
    return parse_tss_response(r.text)

def request_blobs_from_cydia(verbose_level, board, build, ecid, cpid=None, bdid=None):
    d = tss_request_manifest(board, build, ecid, cpid, bdid)
    if verbose_level>3:
        print(d)
    url = 'http://cydia.saurik.com/TSS/controller?action=2'
    r = requests.post(url, headers={'User-Agent': USER_AGENT}, data=d)
    if not r.status_code == requests.codes.ok:
        return { 'MESSAGE': 'TSS HTTP STATUS:', 'STATUS': r.status_code }
    if verbose_level>=1:
        print('MESSAGE: TSS HTTP STATUS: %s' % (r.status_code ))
    if verbose_level>2:
        print(r.text)
    return parse_tss_response(r.text)

def save_tsssaver(ecid, model, boardconfig, savedir, overwrite, verbose_level):
    # Thanks to 1Conan for this
    url = 'https://stor.1conan.com/json/tsssaver/shsh/'
    q_r = requests.get(('%s%s/' % (url,ecid)), headers={'User-Agent': __version__} )
    if q_r.status_code == requests.codes.ok:
        if verbose_level>3:
            print('TSSSaver has device listed')
            print(q_r.text)
        q_l = json.loads((q_r.text))
        # Loop Versions
        for c in range(len(q_l)):
            if verbose_level>3:
                print(q_l[c])
            r_r = requests.get(('%s%s/%s/' % (url,ecid,q_l[c]['name'])), headers={'User-Agent': __version__} )
            r_l = json.loads((r_r.text))
            # Loop AP's
            for d in range(len(r_l)):
                # Help differentiate between Files
                specialprefix = False
                if r_l[d]['name'] == 'noapnonce':
                    specialprefix = True
                if verbose_level>3:
                    print(r_l[d])
                i_r = requests.get(('%s%s/%s/%s' % (url,ecid,q_l[c]['name'],r_l[d]['name'])), headers={'User-Agent': __version__} )
                if verbose_level>3:
                    print(i_r.text)
                i_l = json.loads((i_r.text))
                # Loop Dir Entries
                for e in range(len(i_l)):
                    r = requests.get(('%s%s/%s/%s/%s' % (url,ecid,q_l[c]['name'],r_l[d]['name'],i_l[e]['name'])), headers={'User-Agent': __version__})
                    filename = ((i_l[e]['name']))
                    if specialprefix:
                        filename = '%s_noapnonce.shsh2' % (filename[0:(len(filename)-6)])
                    save_path = os.path.join(savedir, filename)
                    if verbose_level>2:
                        print(r.text)
                    if r.status_code == requests.codes.ok:
                        if not (os.path.exists(save_path)) or overwrite:
                            write_to_file(save_path, (r.text))
                            print('TSSSaver blob saved to %s' % (save_path))
                        else:
                            print('Blobs already exist at %s' % (save_path))
                    else:
                        if verbose_level>=1:
                            print('TSSSaver failed to respond for %s' % (i_l[e]['name']))


    else:
            print('Skipping TSSSaver, your device hasn\'t yet been saved to TSSSaver!')
    


def submit_blobs_to_cydia(cpid, bdid, ecid, data):
    url = 'http://cydia.saurik.com/tss@home/api/store/%s/%s/%s' % (cpid, bdid, ecid)
    r = requests.post(url, headers={'User-Agent': USER_AGENT}, data=data)
    return r.status_code == requests.codes.ok

def write_to_file(file_path, data):
    f = open(file_path, 'w')
    f.write(data)
    f.close()

def parse_tss_response(response):
    ret = {}
    for v in response.split('&'):
        r = v.split('=',1)
        ret[r[0]] = r[1]
    return ret

def parse_args():
    parser = argparse.ArgumentParser(description='Savethemblobs-ReFuse\'d')
    parser.add_argument('ecid', help='device ECID')
    parser.add_argument('device', help='device identifier (eg. iPhone3,1)')
    parser.add_argument('version', nargs='?', help='Specify a certain version to request or use "latest" / "all" to request the latest version or all available versions for the Device (eg. 10.3.3)', default='latest')
    parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join(os.path.expanduser('~'), '.shsh'))
    parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
    parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_true')
    parser.add_argument('--tsssaver-blobs', help='fetch shsh2 from 1Conan\'s TSSSaver (http://TSSSaver.1Conan.com)', action='store_true')
    parser.add_argument('--cydia-blobs', help='fetch blobs from Cydia server (32 bit devices only)', action='store_true')
    parser.add_argument('--full-run', '-f', help='Query all available Servers for ALL known versions', action='store_true')
    parser.add_argument('--verbose', '-v', help='Print additional info, use twice to enable network logging for Apple TSS, use three times to log responses too (Warning SPAM!), and to log EVERYTHING repeat 4 times', action='count')
    return parser.parse_args()

def main(passedArgs = None):

    if passedArgs:
        args = passedArgs
    else:
        args = parse_args()

    try:
        ecid = int(args.ecid, 0)
    except Exception as e:
        print('Trying to interpret ECID input from HEX to Decimal')
        tmp2 = '0x'
        tmp2 += args.ecid
        try:
            ecid = int( tmp2, 0)
        except Exception as e:
             print('Cannot parse ECID! ECID must be in HEX or Decimal')
             print('Run this without parameters for usage')
             return 0

        pass

    if args.tsssaver_blobs:
        submitcydia = False
    else:
        submitcydia = args.no_submit_cydia

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)

    deviceIsViable = False
    for c in range(len(__definedshshdevices__)):
        if args.device == __definedshshdevices__[c]:
            deviceIsViable = True

    d = firmwares_being_signed(args.device)
    if not d:
        print('ERROR: No firmwares found! Invalid device.')
        return 1

    board = d['BoardConfig']
    model = (args.device)
    cpid = d['cpid']
    bdid = d['bdid']

    if deviceIsViable:
        if args.version == 'latest' or args.version == 'all' or args.full_run:
            print('Fetching %s firmwares for %s' % (args.version, args.device))
            for f in d['firmwares']:
                if f['signed'] or args.version == 'all' or args.full_run:
                    save_path = os.path.join(args.save_dir, '%s-%s-%s-%s.shsh' % (ecid, model, f['version'], f['buildid']))

                    if not os.path.exists(save_path) or args.overwrite:
                        print('Requesting blobs from Apple for %s/%s' % (model, f['buildid']))
                        r = request_blobs_from_apple(args.verbose, board, f['buildid'], ecid, cpid, bdid)

                        if r['MESSAGE'] == 'SUCCESS':
                            print('Fresh blobs saved to %s' % (save_path))
                            write_to_file(save_path, r['REQUEST_STRING'])

                            if not submitcydia:
                                print('Submitting blobs to Cydia server')
                                submit_blobs_to_cydia(cpid, bdid, ecid, r['REQUEST_STRING'])

                        else:
                            if 'This device isn' in r['MESSAGE']:
                                print('Failed: That version isn\'t signed!')
                            else:
                                print('Error receiving blobs: %s [%s]' % (r['MESSAGE'], r['STATUS']))

                    else:
                        print('Blobs already exist at %s' % (save_path))
        else:
            checkbit = False
            for f in d['firmwares']:
                if f['version'] == args.version:
                    checkbit = True
                    print('Requesting blobs from Apple for %s/%s-%s' % (model, args.version, f['buildid']))
                    save_path = os.path.join(args.save_dir, '%s-%s-%s-%s.shsh' % (ecid, model, f['version'], f['buildid']))
                    if not os.path.exists(save_path) or args.overwrite:
                        r = request_blobs_from_apple(args.verbose, board, f['buildid'], ecid, cpid, bdid)
                        if r['MESSAGE'] == 'SUCCESS':
                            print('Fresh blobs saved to %s' % (save_path))
                            write_to_file(save_path, r['REQUEST_STRING'])

                            if not submitcydia:
                                print('Submitting blobs to Cydia server')
                                submit_blobs_to_cydia(cpid, bdid, ecid, r['REQUEST_STRING'])

                        else:
                            if 'This device isn' in r['MESSAGE'] and args.verbose<=0:
                                print('Failed: That version isn\'t signed!')
                            else:
                                print('Error receiving blobs: %s [%s]' % (r['MESSAGE'], r['STATUS']))

                    else:
                        print('Blobs already exist at %s' % (save_path))
            if not checkbit:
                print('The device %s doesn\'t have a version %s!' % (args.device, args.version))
    else:
        print('Your device is too new, Skipping SHSH requests from Apple (For now use tsschecker)')

    if args.tsssaver_blobs or args.full_run:
        print('Fetching /u/1Conans TSS-SHSH2-Saver for %s with ECID %s' % (model, ecid))
        save_tsssaver(ecid, model, board, args.save_dir, args.overwrite, args.verbose)
    else:
        print('Skipped fetching blobs from /u/1Conan\'s TSSSaver')

    if (args.cydia_blobs or args.full_run) and deviceIsViable:
        print('Fetching blobs available on Cydia server')
        g = firmwares(args.device)
        if not g:
            print('ERROR: No firmwares found! Invalid device.')
            return 1
        for device in six.itervalues(json.loads(g)):
            board = device['board']
            model = device['model']
            cpid = device['cpid']
            bdid = device['bdid']
            for b in device['firmwares']:
                save_path = os.path.join(args.save_dir, '%s-%s-%s-%s.shsh' % (ecid, model, b['version'], b['build']))

                if not os.path.exists(save_path) or args.overwrite:
                    if args.verbose >= 1:
                        print ('Requesting blobs from Cydia for %s/%s' % (model, b['build']))
                    r = request_blobs_from_cydia(args.verbose, board, b['build'], ecid, cpid, bdid)

                    if r['MESSAGE'] == 'SUCCESS':
                        print('Cydia blobs saved to %s' % (save_path))
                        write_to_file(save_path, r['REQUEST_STRING'])

                    else:
                        if args.verbose >= 1:
                            print ('No blobs found for %s' % (b['build']))

                else:
                    print('Blobs already exist at %s' % (save_path))

        #print 'Fetching beta blobs available on Cydia server'
        h = beta_firmwares(args.device)
        if not h:
            print('ERROR: No firmwares found! Invalid device.')
            return 1
        for device in six.itervalues(json.loads(h)):
            board = device['board']
            model = device['model']
            cpid = device['cpid']
            bdid = device['bdid']
            for c in device['firmwares']:
                save_path = os.path.join(args.save_dir, '%s-%s-%s-%s.shsh' % (ecid, model, c['version'], c['build']))

                if not os.path.exists(save_path) or args.overwrite:
                    if args.verbose >= 1:
                        print ('Requesting beta blobs from Cydia for %s/%s' % (model, c['build']))
                    r = request_blobs_from_cydia(args.verbose, board, c['build'], ecid, cpid, bdid)

                    if r['MESSAGE'] == 'SUCCESS':
                        print('Cydia blobs saved to %s' % (save_path))
                        write_to_file(save_path, r['REQUEST_STRING'])

                    else:
                        if args.verbose >= 1:
                            print ('No blobs found for %s' % (c['build']))

                else:
                    print('Blobs already exist at %s' % (save_path))

    else:
        if deviceIsViable:
            print('Skipped fetching blobs from Cydia server')
        else:
            print('Your device is too new! Cydia TSS only works with 32-Bit devices.')

    return 0

if __name__ == '__main__':
    sys.exit(main())

