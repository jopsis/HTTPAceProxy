#-*- coding: utf-8 -*-
'''
New Era Playlist Downloader Plugin
http://ip:port/newera
'''

__author__ = 'jocebal'

import traceback
import gevent, requests, os, time
import logging, zlib
from urllib3.packages.six.moves.urllib.parse import urlparse, quote, unquote
from urllib3.packages.six import ensure_str, ensure_text, ensure_binary
from PlaylistGenerator import PlaylistGenerator
from requests_file import FileAdapter
from utils import schedule, query_get
import config.newera as config

class Newera(object):

    handlers = ('newera',)

    def __init__(self, AceConfig, AceProxy):
        self.picons = self.channels = self.playlist = self.etag = None
        self.playlisttime = time.time()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # Parse playlist on startup
        self.Playlistparser()
        # Schedule periodic updates if configured
        if config.updateevery:
            schedule(config.updateevery * 60, self.Playlistparser)

    def Playlistparser(self):
        try:
           s = requests.Session()
           s.mount('file://', FileAdapter())
           with s.get(config.url, headers=self.headers, proxies=config.proxies, stream=False, timeout=60) as r:
              if r.status_code != 304:
                 if r.encoding is None: r.encoding = 'utf-8'
                 self.headers['If-Modified-Since'] = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime(self.playlisttime))
                 self.playlist = PlaylistGenerator(m3uchanneltemplate=config.m3uchanneltemplate)
                 self.picons = {}
                 self.channels = {}
                 m = requests.auth.hashlib.md5()
                 logging.info('[%s]: playlist %s downloaded' % (self.__class__.__name__, config.url))

                 # Parse M3U format from New Era
                 # Format:
                 # #EXTINF:-1 tvg-logo="..." tvg-id="..." group-title="...", Channel Name
                 # acestream://hash
                 lines = r.text.split('\n')
                 i = 0
                 while i < len(lines):
                    line = lines[i].strip()

                    # Look for #EXTINF lines
                    if line.startswith('#EXTINF:'):
                       # Extract channel info
                       itemdict = {}

                       # Extract tvg-logo
                       if 'tvg-logo="' in line:
                          start = line.find('tvg-logo="') + 10
                          end = line.find('"', start)
                          itemdict['logo'] = line[start:end]
                       else:
                          itemdict['logo'] = ''

                       # Extract tvg-id
                       if 'tvg-id="' in line:
                          start = line.find('tvg-id="') + 8
                          end = line.find('"', start)
                          itemdict['tvgid'] = line[start:end]
                       else:
                          itemdict['tvgid'] = ''

                       # Extract group-title
                       if 'group-title="' in line:
                          start = line.find('group-title="') + 13
                          end = line.find('"', start)
                          itemdict['group'] = line[start:end]
                       else:
                          itemdict['group'] = 'Unknown'

                       # Extract channel name (after the last comma)
                       if ',' in line:
                          name = line[line.rfind(',') + 1:].strip()
                          itemdict['name'] = name
                          itemdict['tvg'] = name
                       else:
                          itemdict['name'] = 'Unknown Channel'
                          itemdict['tvg'] = 'Unknown Channel'

                       # Get the next line which should be the acestream URL
                       i += 1
                       if i < len(lines):
                          url = lines[i].strip()

                          # Check if it's an acestream URL (acestream:// or http://127.0.0.1:6878/ace/getstream?id=)
                          acestream_url = None
                          if url.startswith('acestream://'):
                             acestream_url = url
                          elif '/ace/getstream?id=' in url or '/ace/getstream?infohash=' in url:
                             # Extract acestream ID from HTTP URL format
                             # Format: http://127.0.0.1:6878/ace/getstream?id=XXXXX
                             parsed = urlparse(url)
                             query_params = parsed.query.split('&')
                             for param in query_params:
                                if param.startswith('id='):
                                   ace_id = param[3:]
                                   acestream_url = 'acestream://' + ace_id
                                   break
                                elif param.startswith('infohash='):
                                   ace_id = param[9:]
                                   acestream_url = 'acestream://' + ace_id
                                   break

                          if acestream_url:
                             name = itemdict['name']
                             self.channels[name] = acestream_url
                             self.picons[name] = itemdict.get('logo', '')
                             itemdict['url'] = quote(ensure_str(name), '')

                             self.playlist.addItem(itemdict)
                             m.update(ensure_binary(name))

                    i += 1

                 self.etag = '"' + m.hexdigest() + '"'
                 logging.info('[%s]: plugin playlist generated with %d channels' % (self.__class__.__name__, len(self.channels)))

              self.playlisttime = time.time()

        except requests.exceptions.RequestException as e:
           logging.error("[%s]: can't download %s playlist! Error: %s" % (self.__class__.__name__, config.url, str(e)))
           return False
        except Exception as e:
           logging.error("[%s]: Error parsing playlist: %s" % (self.__class__.__name__, str(e)))
           logging.error(traceback.format_exc())
           return False

        return True

    def handle(self, connection):
        logging.debug('[%s]: handle() called for path: %s' % (self.__class__.__name__, connection.path))
        # 30 minutes cache
        if not self.playlist or (time.time() - self.playlisttime > 30 * 60):
           logging.debug('[%s]: Refreshing playlist' % self.__class__.__name__)
           if not self.Playlistparser(): connection.send_error()

        # Default to m3u8 for better compatibility
        connection.ext = query_get(connection.query, 'ext', 'm3u8')
        logging.debug('[%s]: Request type: %s, ext: %s' % (self.__class__.__name__, connection.reqtype, connection.ext))

        # Handle individual channel requests (/newera/channel/CHANNEL_NAME.ts or .m3u8)
        if connection.path.startswith('/{reqtype}/channel/'.format(**connection.__dict__)):
           # Accept both .ts and .m3u8 extensions for channels
           if not (connection.path.endswith('.ts') or connection.path.endswith('.m3u8')):
              connection.send_error(404, 'Invalid path: {path} - must end with .ts or .m3u8'.format(**connection.__dict__), logging.ERROR)
           # Extract channel name and determine the extension used
           basename = os.path.basename(connection.path)
           name = ensure_text(unquote(os.path.splitext(basename)[0]))
           # Use the extension from the request path
           connection.ext = basename.split('.')[-1] if '.' in basename else 'm3u8'
           url = self.channels.get(name)
           if url is None:
              connection.send_error(404, '[%s]: unknown channel: %s' % (self.__class__.__name__, name), logging.ERROR)
           connection.__dict__.update({'channelName': name,
                                       'channelIcon': self.picons.get(name),
                                       'path': {'acestream': '/content_id/%s/%s.%s' % (urlparse(url).netloc, name, connection.ext),
                                                'infohash' : '/infohash/%s/%s.%s' % (urlparse(url).netloc, name, connection.ext),
                                                'http'     : '/url/%s/%s.%s' % (quote(url,''), name, connection.ext),
                                                'https'    : '/url/%s/%s.%s' % (quote(url,''), name, connection.ext),
                                               }[urlparse(url).scheme]})
           connection.__dict__.update({'splittedpath': connection.path.split('/')})
           connection.__dict__.update({'reqtype': connection.splittedpath[1].lower()})
           return

        elif self.etag == connection.headers.get('If-None-Match'):
           logging.debug('[%s]: ETag matches. Return 304 to [%s]' % (self.__class__.__name__, connection.clientip))
           connection.send_response(304)
           connection.send_header('Connection', 'close')
           connection.end_headers()
           return

        else:
           logging.debug('[%s]: Exporting M3U playlist' % self.__class__.__name__)
           try:
              exported = self.playlist.exportm3u( hostport=connection.headers['Host'],
                                                  path='' if not self.channels else '/newera/channel',
                                                  header=config.m3uheadertemplate,
                                                  query=connection.query
                                                 )
              logging.debug('[%s]: Playlist exported, size: %d bytes' % (self.__class__.__name__, len(exported)))
           except Exception as e:
              logging.error('[%s]: Error exporting playlist: %s' % (self.__class__.__name__, str(e)))
              connection.send_error(500, 'Error exporting playlist: %s' % str(e), logging.ERROR)
              return
           # Use proper Content-Type for M3U8
           content_type = 'audio/mpegurl; charset=utf-8'
           response_headers = {'Content-Type': content_type, 'Connection': 'close', 'Access-Control-Allow-Origin': '*'}
           try:
              h = connection.headers.get('Accept-Encoding').split(',')[0]
              compress_method = { 'zlib': zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS),
                                  'deflate': zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS),
                                  'gzip': zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16) }
              exported = compress_method[h].compress(exported) + compress_method[h].flush()
              response_headers['Content-Encoding'] = h
           except: pass
           response_headers['Content-Length'] = len(exported)
           if connection.request_version == 'HTTP/1.1':
              response_headers['ETag'] = self.etag
           connection.send_response(200)
           for key, value in response_headers.items():
              connection.send_header(key, value)
           connection.end_headers()
           try:
              connection.wfile.write(exported)
              connection.wfile.flush()
           except Exception as e:
              logging.error('[%s]: Error writing response: %s' % (self.__class__.__name__, repr(e)))
              raise
           logging.info('[%s]: plugin sent playlist with %d channels (%d bytes) to [%s]' % (self.__class__.__name__, len(self.channels), len(exported), connection.clientip))
           return

