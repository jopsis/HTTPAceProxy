# -*- coding: utf-8 -*-
'''
All-In-One (AIO) Playlist Plugin configuration file
'''
import os

# Proxy settings (standard architecture)
proxies = {}

# Plugins to include in AIO playlist
# Can be overridden with AIO_PLUGINS environment variable (comma-separated)
# Examples:
#   AIO_PLUGINS=newera,elcano (only these two)
#   AIO_PLUGINS=all (include all enabled plugins except system ones)
#   AIO_PLUGINS= (empty, same as 'all')
# If not set, defaults to all enabled plugins
aio_plugins_env = os.getenv('AIO_PLUGINS', 'all').strip().lower()
if aio_plugins_env == 'all' or aio_plugins_env == '':
    # Include all enabled plugins (will be filtered in the plugin code)
    included_plugins = None  # None means "all"
else:
    # Parse comma-separated list
    included_plugins = [p.strip().lower() for p in aio_plugins_env.split(',') if p.strip()]

# TV Guide URL
tvgurl = 'https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv_sincolor0.xml.gz'

# Shift the TV Guide time
tvgshift = 0

# Playlist Headers
m3uheadertemplate = u'#EXTM3U url-tvg="{}" tvg-shift={} deinterlace=1 m3uautoload=1 cache=1000\n'.format(tvgurl, tvgshift)

# Channel template
m3uchanneltemplate = u'#EXTINF:-1 group-title="{group}" tvg-name="{tvg}" tvg-id="{tvgid}" tvg-logo="{logo}",{name}\n#EXTGRP:{group}\n{url}\n'