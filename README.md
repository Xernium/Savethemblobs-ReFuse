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
  	ecid                 device ECID
  	device               device identifier (eg. iPhone3,1)
  	version              Specify a certain version to request or use "latest" /
        	             "all" to request the latest version or all available
            	             versions for the Device (eg. 10.3.3)

	optional arguments:
  	-h, --help           show this help message and exit
  	--save-dir SAVE_DIR  local dir for saving blobs (default: ~/.shsh)
  	--overwrite          overwrite any existing blobs
  	--no-submit-cydia    don't submit blobs to Cydia server
  	--tsssaver-blobs     fetch shsh2 from 1Conan's TSSSaver
                         (http://TSSSaver.1Conan.com)
  	--cydia-blobs        fetch blobs from Cydia server (32 bit devices only)
  	--full-run, -f       Query all available Servers for ALL known versions
  	--verbose, -v        Print additional info, use twice to enable network
                         logging for Apple TSS, use three times to log responses
                         too (Warning SPAM!), and to log EVERYTHING repeat 4 times	


## License

savethemblobs is available under the MIT license. See the LICENSE file for more info.
