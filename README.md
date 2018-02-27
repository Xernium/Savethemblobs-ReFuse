# Savethemblobs-ReFuse'd

A *rather* simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally.

### CAUTION! This tool doesn't work for saving 64-Bit Device APTICKETS! (Yet)

This tool can crawl blobs already cached on Cydia's Servers or 1Conan's TSSSaver to save them locally.

Should automatically work with future firmwares!

## Dependencies

	Depends on Python 2.7 pip, requests and six. 
	With pip installed, run installdependencies.sh

## Usage

	Savethemblobs-ReFuse'd

	positional arguments:
	  ecid                 device ECID (found with iTunes or ideviceinfo)
	  device               device identifier (found with iTunes or ideviceinfo eg. iPhone3,1)
	  version	       [Optional] Specify the version to save shsh/shsh2 from. Default is 'latest'
			       but you can also specify a certain version (eg. 10.3.3) or 'all'	to force query all available versions

	optional arguments:
	  -h, --help           show this help message and exit
	  --save-dir SAVE_DIR  local dir for saving blobs (default: ~/.shsh)
	  --overwrite          overwrite any existing blobs
	  --overwrite-apple    overwrite any existing blobs (only from Apple)
	  --overwrite-cydia    overwrite any existing blobs (only from Cydia)
	  --no-submit-cydia    don't submit blobs to Cydia server
	  --tsssaver-blobs     fetch shsh2 from 1Conan's TSSSaver
                               (http://TSSSaver.1Conan.com)
	  --cydia-blobs        fetch blobs from Cydia server (32 bit devices only)
	  -f, --full-run       Query all available Servers for ALL known versions	


## License

savethemblobs is available under the MIT license. See the LICENSE file for more info.
