# -*- coding: utf-8 -*-
'''
Elcano Playlist Plugin configuration file
'''
# Proxy settings.
# For example you can install tor browser and add in torrc SOCKSPort 9050
# proxies = {'http' : 'socks5h://127.0.0.1:9050','https' : 'socks5h://127.0.0.1:9050'}
# If your http-proxy need authentification - proxies = {'https' : 'https://user:password@ip:port'}

proxies = {}

# Insert your Elcano playlist URL here or path to file ('file:///path/to/file' or 'file:///C://path//to//file' for Windows OS)
url = 'https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes_acestream.m3u'

# Download playlist every N minutes to keep it fresh
# 0 = disabled (will download once on startup)
# Recommended: 30 (update every 30 minutes)
updateevery = 30

# TV Guide URL
tvgurl = 'https://github.com/davidmuma/EPG_dobleM/raw/refs/heads/master/EPG_dobleM.xml'

# Shift the TV Guide time to the specified number of hours
tvgshift = 0

# Channel playlist template
# The following values are allowed:
# name - channel name
# url - channel URL
# tvg - channel tvg-name (optional)
# tvgid - channel tvg-id (optional)
# group - channel playlist group-title (optional)
# logo - channel picon file tvg-logo (optional)
m3uheadertemplate = u'#EXTM3U url-tvg={} tvg-shift={} deinterlace=1 m3uautoload=1 cache=1000\n'.format(tvgurl, tvgshift)
# Use .m3u8 extension by default for better compatibility with apps and browsers
m3uchanneltemplate = u'#EXTINF:-1 group-title="{group}" tvg-name="{tvg}" tvg-id="{tvgid}" tvg-logo="{logo}",{name}\n#EXTGRP:{group}\n{url}\n'
