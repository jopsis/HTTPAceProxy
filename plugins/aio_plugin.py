# -*- coding: utf-8 -*-
'''
All-In-One (AIO) Playlist Plugin
http://ip:port/aio
'''
__author__ = 'AIO'

import logging
import time
from urllib3.packages.six.moves.urllib.parse import quote
from urllib3.packages.six import ensure_str, ensure_binary
from PlaylistGenerator import PlaylistGenerator
import config.aio as config

class Aio(object):
    
    handlers = ('aio',)

    def __init__(self, AceConfig, AceProxy):
        self.AceConfig = AceConfig
        self.AceProxy = AceProxy
        self.logger = logging.getLogger('AIO')

    def handle(self, connection):
        self.logger.debug('Generating AIO playlist for client: %s' % connection.clientip)

        # Create a fresh generator for this request
        generator = PlaylistGenerator(m3uchanneltemplate=config.m3uchanneltemplate)

        # Iterate over all loaded plugins in the proxy
        processed_plugins = set()

        # Sorted keys for consistent order in playlist
        sorted_handlers = sorted(self.AceProxy.pluginshandlers.keys())

        # Log which plugins will be included
        if config.included_plugins is None:
            self.logger.debug('AIO mode: Including all enabled plugins')
        else:
            self.logger.debug('AIO mode: Including only: %s' % ', '.join(config.included_plugins))

        for handler_name in sorted_handlers:
            plugin = self.AceProxy.pluginshandlers[handler_name]

            # Skip system plugins and self
            if handler_name in ('aio', 'stat', 'statplugin', 'torrenttv_api'):
                continue

            # Skip if not in included list (if list is specified)
            if config.included_plugins is not None:
                if handler_name.lower() not in config.included_plugins:
                    self.logger.debug('Skipping plugin %s (not in AIO_PLUGINS filter)' % handler_name)
                    continue

            # Avoid processing the same plugin instance twice (one plugin can have multiple handlers)
            if id(plugin) in processed_plugins:
                continue
            processed_plugins.add(id(plugin))
            
            try:
                count = 0
                # Method 1: High Fidelity (PlaylistGenerator based plugins like NewEra, Elcano, MisterChire)
                # We extract from the internal itemlist to preserve original groups and logos
                if hasattr(plugin, 'playlist') and hasattr(plugin.playlist, 'itemlist'):
                    for item in plugin.playlist.itemlist:
                        new_item = item.copy()
                        
                        # Fix URL: if it's a local name, resolve it to direct AceStream URL
                        if hasattr(plugin, 'channels') and new_item['name'] in plugin.channels:
                            new_item['url'] = plugin.channels[new_item['name']]
                        
                        # Fallback for group if empty
                        if not new_item.get('group'):
                            new_item['group'] = handler_name.capitalize()
                            
                        generator.addItem(new_item)
                        count += 1
                        
                # Method 2: Fallback (Simple dict based plugins)
                elif hasattr(plugin, 'channels'):
                    for name, url in plugin.channels.items():
                        generator.addItem({
                            'name': name,
                            'url': url,
                            'group': handler_name.capitalize(), # Use Plugin Name as group
                            'logo': plugin.picons.get(name) if hasattr(plugin, 'picons') else ''
                        })
                        count += 1
                        
                self.logger.debug('Added %d channels from plugin %s' % (count, handler_name))
                
            except Exception as e:
                self.logger.error('Error extracting channels from %s: %s' % (handler_name, repr(e)))

        # Export the combined playlist
        try:
            exported = generator.exportm3u(
                hostport=connection.headers['Host'],
                header=config.m3uheadertemplate,
                query=connection.query
            )
            
            connection.send_response(200)
            connection.send_header('Content-Type', 'audio/mpegurl; charset=utf-8')
            connection.send_header('Content-Length', len(exported))
            connection.send_header('Connection', 'close')
            connection.end_headers()
            connection.wfile.write(exported)
            
        except Exception as e:
            self.logger.error('Error exporting AIO playlist: %s' % repr(e))
            connection.send_error(500, 'AIO Generation Error')