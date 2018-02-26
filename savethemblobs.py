#!/usr/bin/env python
# -*- coding: utf-8 -*-
# savethemblobs.py
#   A simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally and on Cydia server.
#   And now also grabs blobs already cached on Cydia servers to save them locally.
#
# Copyright (c) 2013 Neal <neal@ineal.me>
#   Updated 2016 iApeiron
#       deprecated and obsolete APIs removed
#   Upgraded/Updated 2018
#       New TSS-Saving Solution crawler by /u/1Conan
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

def request_blobs_from_apple(board, build, ecid, cpid=None, bdid=None):
    #url = 'http://localhost:8080/'
    url = 'http://gs.apple.com/TSS/controller?action=2'
    r = requests.post(url, headers={'User-Agent': 'InetURL/1.0', 'Accept-Encoding': '*/*', 'Content-type': 'text/xml; charset="utf-8"'}, data=tss_request_manifest(board, build, ecid, cpid, bdid))
    if not r.status_code == requests.codes.ok:
        return { 'MESSAGE': 'TSS HTTP STATUS:', 'STATUS': r.status_code }
    return parse_tss_response(r.text)

def request_blobs_from_cydia(board, build, ecid, cpid=None, bdid=None):
    url = 'http://cydia.saurik.com/TSS/controller?action=2'
    r = requests.post(url, headers={'User-Agent': USER_AGENT}, data=tss_request_manifest(board, build, ecid, cpid, bdid))
    if not r.status_code == requests.codes.ok:
        return { 'MESSAGE': 'TSS HTTP STATUS:', 'STATUS': r.status_code }
    return parse_tss_response(r.text)

def save_tsssaver(ecid, model, boardconfig, version, buildid, savedir, overwrite):
    url = 'https://stor.1conan.com/tsssaver/shsh/'
    # Pre 10.2
    f_path_arg = [
        'apnonce-0dc448240696866b0cc1b2ac3eca4ce22af11cb3',
        'apnonce-352dfad1713834f4f94c5ff3c3e5e99477347b95',
        'apnonce-42c88f5a7b75bc944c288a7215391dc9c73b6e9f',
        'apnonce-603be133ff0bdfa0f83f21e74191cf6770ea43bb',
        'apnonce-9804d99e85bbafd4bb1135a1044773b4df9f1ba3',
        'noapnonce'
    ]
    r = []
    # Why did this have to change mid-way-through?!
    tmp1 = version[:4]
    if float(tmp1) <= 10.2 and not version == '10.2.1':
        # Pre 10.2.1: EASY
        for c in range(len(f_path_arg)):
            filename = ('%s-%s-%s-%s_%s.shsh2' % (ecid, model, version, buildid, f_path_arg[c]))
            save_path = os.path.join(savedir, filename)
            req_url = ('%s%s/%s/%s/%s_%s_%s-%s.shsh2' % (url, ecid, version, f_path_arg[c], ecid, model, version, buildid))
            r = requests.get(req_url, headers={'User-Agent': 'savethemblobs/2.1'} )
            if r.status_code == requests.codes.ok:
                if not (os.path.exists(save_path)) or overwrite:
                    write_to_file(save_path, (r.text))
                    print('TSSSaver blob saved to %s' % (save_path))
                else:
                    print('Blobs already exist at %s' % (save_path))
    else:
        # Post 10.2.1: Now we are in for a real treat...
        dir_listing_url = ('%s%s/%s/noapnonce' % (url, ecid, version))
        dir_r = requests.get(dir_listing_url, headers={'User-Agent': 'savethemblobs/2.1'} )
        if dir_r.status_code == requests.codes.ok:
            listing = dir_r.text
            search_str = ('<a href="%s_%s_%s_%s-%s_' % (ecid, model, boardconfig, version, buildid))
            if search_str in listing:
                for c in re.finditer(search_str, listing):
                    d = c.end()
                    e = c.end()
                    control_bit = False
                    while '.shsh2' not in listing[d:e]:
                        e=e+1
                        if e>10000:
                            print('Failed to parse TSSSaver')
                            control_bit = True
                            break
                    if control_bit:
                        return
                    else:
                        # Hello there nonce
                        nonce = listing[d:(e-6)]
                        filename = ('%s-%s-%s-%s_%s.shsh2' % (ecid, model, version, buildid, nonce))
                        save_path = os.path.join(savedir, filename)
                        req_url = ('%s%s/%s/noapnonce/%s_%s_%s_%s-%s_%s.shsh2' % (url, ecid, version, ecid, model, boardconfig, version, buildid, nonce))
                        r = requests.get(req_url, headers={'User-Agent': 'savethemblobs/2.1'} )
                        if r.status_code == requests.codes.ok:
                            if not (os.path.exists(save_path)) or overwrite:
                                write_to_file(save_path, (r.text))
                                print('TSSSaver blob saved to %s' % (save_path))
                            else:
                                print('Blobs already exist at %s' % (save_path))


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
    parser = argparse.ArgumentParser(description='Savethemblobs-ReFuse')
    parser.add_argument('ecid', help='device ECID')
    parser.add_argument('device', help='device identifier (eg. iPhone3,1)')
    parser.add_argument('version', nargs='?', help='Specify a certain version to request or use "latest" / "all" to request the latest version or all available versions for the Device (eg. 10.3.3)', default='latest')
    parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join(os.path.expanduser('~'), '.shsh'))
    parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
    parser.add_argument('--overwrite-apple', help='overwrite any existing blobs (only from Apple)', action='store_true')
    parser.add_argument('--overwrite-cydia', help='overwrite any existing blobs (only from Cydia)', action='store_true')
    parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_true')
    parser.add_argument('--tsssaver-blobs', help='fetch shsh2 from 1Conan\'s TSSSaver (http://TSSSaver.1Conan.com)', action='store_true')
    parser.add_argument('--cydia-blobs', help='fetch blobs from Cydia server (32 bit devices only)', action='store_true')
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

    d = firmwares_being_signed(args.device)
    if not d:
        print('ERROR: No firmwares found! Invalid device.')
        return 1

    board = d['BoardConfig']
    model = (args.device)
    cpid = d['cpid']
    bdid = d['bdid']
    if args.version == 'latest' or args.version == 'all':
        print('Fetching %s firmwares for %s' % (args.version, args.device))
        for f in d['firmwares']:
            if f['signed'] or args.version == 'all':
                save_path = os.path.join(args.save_dir, '%s-%s-%s-%s.shsh' % (ecid, model, f['version'], f['buildid']))

                if not os.path.exists(save_path) or args.overwrite_apple or args.overwrite:
                    print('Requesting blobs from Apple for %s/%s' % (model, f['buildid']))
                    r = request_blobs_from_apple(board, f['buildid'], ecid, cpid, bdid)

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
                if not os.path.exists(save_path) or args.overwrite_apple or args.overwrite:
                    r = request_blobs_from_apple(board, f['buildid'], ecid, cpid, bdid)
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
        if not checkbit:
            print('The device %s doesn\'t have a version %s!' % (args.device, args.version))


    if args.tsssaver_blobs:
        print('Fetching /u/1Conans TSS-SHSH2-Saver for %s with ECID %s' % (model, ecid))
        for f in d['firmwares']:
            # This helps reduce query-spam
            tmp1 = f['version'][:2]
            if '.' in tmp1:
                tmp1 = f['version'][:1]
            if float(tmp1) >= 10.0:
                save_tsssaver(ecid, model, board, f['version'], f['buildid'], args.save_dir, args.overwrite)
    else:
        print('Skipped fetching blobs from /u/1Conan\'s TSSSaver')

    if args.cydia_blobs:
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

                if not os.path.exists(save_path) or args.overwrite_cydia or args.overwrite:
                    #print 'Requesting blobs from Cydia for %s/%s' % (model, b['build'])
                    r = request_blobs_from_cydia(board, b['build'], ecid, cpid, bdid)

                    if r['MESSAGE'] == 'SUCCESS':
                        print('Cydia blobs saved to %s' % (save_path))
                        write_to_file(save_path, r['REQUEST_STRING'])

                    #else:
                        #print 'No blobs found for %s' % (b['build'])

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

                if not os.path.exists(save_path) or args.overwrite_cydia or args.overwrite:
                    #print 'Requesting beta blobs from Cydia for %s/%s' % (model, c['build'])
                    r = request_blobs_from_cydia(board, c['build'], ecid, cpid, bdid)

                    if r['MESSAGE'] == 'SUCCESS':
                        print('Cydia blobs saved to %s' % (save_path))
                        write_to_file(save_path, r['REQUEST_STRING'])

                    #else:
                        #print 'No blobs found for %s' % (c['build'])

                else:
                    print('Blobs already exist at %s' % (save_path))

    else:
        print('Skipped fetching blobs from Cydia server')

    return 0

if __name__ == '__main__':
    sys.exit(main())

