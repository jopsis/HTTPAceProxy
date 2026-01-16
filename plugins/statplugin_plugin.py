# -*- coding: utf-8 -*-
'''
Plugin Status viewer
Shows all loaded plugins with their channels and availability status

To use it, go to http://acehttp_proxy_ip:port/statplugin
'''

__author__ = 'jocebal'

import time
import logging
import gevent
from urllib3.packages.six.moves.urllib.parse import urlparse
from urllib3.packages.six import ensure_binary
from requests.compat import json
from utils import query_get

class Statplugin(object):
    handlers = ('statplugin',)
    logger = logging.getLogger('STATPLUGIN')

    def __init__(self, AceConfig, AceProxy):
        self.AceConfig = AceConfig
        self.AceProxy = AceProxy
        self.channel_status_cache = {}  # Cache: {content_id: {available, infohash, checked_at}}
        self.logger.info('[Statplugin]: Plugin initialized')

    def handle(self, connection):
        '''Main request handler'''
        action = query_get(connection.query, 'action')

        if action == 'get_plugins':
            # Return JSON with all plugins and channels
            self.logger.debug('[Statplugin]: get_plugins request from %s' % connection.clientip)
            data = self.get_plugins_data()
            Statplugin.send_json_response(data, connection)

        elif action == 'check_channel':
            # Check availability of a single channel
            plugin_name = query_get(connection.query, 'plugin')
            channel_name = query_get(connection.query, 'channel')
            content_id = query_get(connection.query, 'content_id')  # Optional: direct content_id
            self.logger.debug('[Statplugin]: check_channel request: %s/%s (content_id: %s)' % (plugin_name, channel_name or 'N/A', content_id or 'N/A'))
            data = self.check_single_channel(plugin_name, channel_name, content_id)
            Statplugin.send_json_response(data, connection)

        elif action == 'get_cache':
            # Return current cache status
            data = {'cache': self.channel_status_cache, 'total': len(self.channel_status_cache)}
            Statplugin.send_json_response(data, connection)

        else:
            # Return HTML interface
            try:
                content = Statplugin.get_html_content()
                Statplugin.send_html_response(content, connection)
            except Exception as e:
                self.logger.error('[Statplugin]: Error loading HTML: %s' % repr(e))
                connection.send_error(500, 'Internal Server Error')

    def get_plugins_data(self):
        '''
        Returns data about all loaded plugins and their channels
        Format: {plugins: [{name, total_channels, channels: [...]}, ...]}
        '''
        plugins_data = []
        processed_plugins = set()  # Track unique plugin instances by id()

        for handler_name, plugin in self.AceProxy.pluginshandlers.items():
            # Skip stat plugins
            if handler_name in ('stat', 'statplugin'):
                continue

            # Skip if we already processed this plugin instance
            # (handles cases like 'newera' and 'newera.m3u8' being the same instance)
            plugin_id = id(plugin)
            if plugin_id in processed_plugins:
                continue
            processed_plugins.add(plugin_id)

            # Only process plugins that have channels
            if not hasattr(plugin, 'channels') or not plugin.channels:
                continue

            # Use the shortest handler name for this plugin (prefer 'newera' over 'newera.m3u8')
            plugin_handlers = [h for h, p in self.AceProxy.pluginshandlers.items() if id(p) == plugin_id]
            plugin_name = min(plugin_handlers, key=len) if plugin_handlers else handler_name

            self.logger.debug('[Statplugin]: Processing plugin: %s' % plugin_name)

            # Try to get channel list from JSON source (to avoid dictionary key collisions)
            channels_list = self._get_channels_from_json_source(plugin_name, plugin)

            # Fallback to plugin.channels if JSON not available
            if channels_list is None:
                channels_list = self._get_channels_from_dict(plugin)

            self.logger.info('[Statplugin]: Plugin %s: %d channels loaded' % (plugin_name, len(channels_list)))

            plugins_data.append({
                'name': plugin_name,
                'total_channels': len(channels_list),
                'channels': channels_list
            })

        return {
            'status': 'success',
            'plugins': plugins_data,
            'total_plugins': len(plugins_data),
            'cache_size': len(self.channel_status_cache)
        }

    def _get_channels_from_json_source(self, plugin_name, plugin):
        '''
        Try to get channels directly from JSON source (e.g., IPFS hashes.json)
        This avoids dictionary key collisions that hide duplicate channel names
        Returns: list of channels or None if not available
        '''
        # Known JSON URLs for plugins
        json_urls = {
            'elcano': 'https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes.json',
            # Add more plugins here as needed
        }

        json_url = json_urls.get(plugin_name)
        if not json_url:
            return None  # No JSON source available

        try:
            import requests
            self.logger.debug('[Statplugin]: Fetching JSON from %s' % json_url)
            r = requests.get(json_url, timeout=10)
            r.raise_for_status()

            data = r.json()
            hashes = data.get('hashes', [])

            if not hashes:
                self.logger.warning('[Statplugin]: JSON has no hashes array')
                return None

            self.logger.info('[Statplugin]: Found %d channels in JSON for plugin %s' % (len(hashes), plugin_name))

            channels_list = []
            for item in hashes:
                title = item.get('title', 'Unknown')
                content_id = item.get('hash')
                logo = item.get('logo', '')
                tvg_id = item.get('tvg_id', '')
                group = item.get('group', '')

                if not content_id or len(content_id) < 10:
                    self.logger.warning('[Statplugin]: Skipping item with invalid hash: %s' % title)
                    continue

                # Get cached status if available
                cached = self.channel_status_cache.get(content_id, {})
                status = 'unknown'
                if cached:
                    status = 'available' if cached.get('available') else 'unavailable'

                channels_list.append({
                    'name': title,
                    'content_id': content_id,
                    'logo': logo,
                    'status': status,
                    'last_check': cached.get('checked_at'),
                    'infohash': cached.get('infohash', ''),
                    'tvg_id': tvg_id,
                    'group': group
                })

            return channels_list

        except Exception as e:
            self.logger.error('[Statplugin]: Error fetching JSON for %s: %s' % (plugin_name, repr(e)))
            return None  # Fallback to dict method

    def _get_channels_from_dict(self, plugin):
        '''
        Get channels from plugin.channels dictionary (fallback method)
        This may lose duplicate channel names
        Returns: list of channels
        '''
        channels_list = []
        skipped = 0

        for channel_name, url in plugin.channels.items():
            # Extract content_id from URL
            parsed = urlparse(url)

            # Handle different URL schemes
            if parsed.scheme == 'acestream':
                content_id = parsed.netloc
            elif parsed.scheme in ('http', 'https'):
                # For HTTP URLs, skip
                skipped += 1
                continue
            else:
                content_id = None

            if not content_id or len(content_id) < 10:
                self.logger.warning('[Statplugin]: Invalid or missing content_id for channel %s' % channel_name)
                skipped += 1
                continue

            # Get cached status if available
            cached = self.channel_status_cache.get(content_id, {})
            status = 'unknown'
            if cached:
                status = 'available' if cached.get('available') else 'unavailable'

            # Get logo/picon if available
            logo = ''
            if hasattr(plugin, 'picons') and plugin.picons:
                logo = plugin.picons.get(channel_name, '')

            channels_list.append({
                'name': channel_name,
                'content_id': content_id,
                'logo': logo,
                'status': status,
                'last_check': cached.get('checked_at'),
                'infohash': cached.get('infohash', ''),
            })

        if skipped > 0:
            self.logger.info('[Statplugin]: %d channels skipped (HTTP or invalid)' % skipped)

        return channels_list

    def check_single_channel(self, plugin_name, channel_name, content_id=None):
        '''
        Check availability of a single channel using LOADASYNC
        Can use either channel_name or content_id for lookup
        Returns: {status, available, infohash, error}
        '''
        try:
            # Validate plugin exists
            plugin = self.AceProxy.pluginshandlers.get(plugin_name)
            if not plugin:
                return {'status': 'error', 'error': 'Plugin not found: %s' % plugin_name}

            # If content_id is provided directly, use it
            if content_id:
                self.logger.info('[Statplugin]: Checking channel by content_id: %s' % content_id[:8])
            else:
                # Otherwise, lookup by channel name (may not work with duplicates)
                if not hasattr(plugin, 'channels'):
                    return {'status': 'error', 'error': 'Plugin has no channels'}

                # Get channel URL
                url = plugin.channels.get(channel_name)
                if not url:
                    return {'status': 'error', 'error': 'Channel not found: %s' % channel_name}

                # Extract content_id
                parsed = urlparse(url)
                content_id = parsed.netloc if parsed.scheme == 'acestream' else None

                if not content_id:
                    return {'status': 'error', 'error': 'Invalid acestream URL'}

                self.logger.info('[Statplugin]: Checking channel %s/%s (content_id: %s)' % (plugin_name, channel_name, content_id[:8]))

            # Check if already in cache and fresh (< 5 minutes)
            cached = self.channel_status_cache.get(content_id)
            if cached and (time.time() - cached.get('checked_at', 0)) < 300:
                self.logger.debug('[Statplugin]: Using cached result for %s' % content_id[:8])
                return {
                    'status': 'success',
                    'cached': True,
                    'available': cached.get('available', False),
                    'infohash': cached.get('infohash', ''),
                    'checked_at': cached.get('checked_at')
                }

            # Perform check with LOADASYNC
            result = self._check_availability_light(content_id)

            # Update cache
            self.channel_status_cache[content_id] = {
                'available': result.get('available', False),
                'infohash': result.get('infohash', ''),
                'checked_at': time.time(),
                'error': result.get('error', None)
            }

            return {
                'status': 'success',
                'cached': False,
                'available': result.get('available', False),
                'infohash': result.get('infohash', ''),
                'checked_at': time.time(),
                'error': result.get('error')
            }

        except Exception as e:
            self.logger.error('[Statplugin]: Error checking channel: %s' % repr(e))
            return {'status': 'error', 'error': str(e)}

    def _check_availability_light(self, content_id):
        '''
        Light availability check using LOADASYNC
        Does NOT start streaming, only queries content metadata
        Returns: {available: bool, infohash: str, error: str}
        '''
        try:
            import aceclient
            import aceclient.acemessages

            # Prepare parameters for AceClient (must match acehttp.py format)
            params = {
                'ace': self.AceConfig.ace,
                'acekey': self.AceConfig.acekey,
                'acesex': self.AceConfig.acesex,
                'aceage': self.AceConfig.aceage,
                'connect_timeout': self.AceConfig.aceconntimeout,
                'result_timeout': self.AceConfig.aceresulttimeout,
                'videoseekback': self.AceConfig.videoseekback,
                'videotimeout': self.AceConfig.videotimeout,
                'stream_type': ' '.join(['{}={}'.format(k,v) for k,v in self.AceConfig.acestreamtype.items()]),
                'sessionID': '0',  # Dummy session ID for check
                'connectionTime': time.time(),
                'clientDetail': None,
                'channelIcon': 'http://static.acestream.net/sites/acestream/img/ACE-logo.png',
                'content_id': content_id
            }

            # Add START_PARAMS (file_indexes, developer_id, affiliate_id, zone_id, stream_id)
            for param in aceclient.acemessages.AceConst.START_PARAMS:
                params[param] = '0'

            # Create temporary AceClient
            ace = aceclient.AceClient(params)
            ace.GetAUTH()

            # Get content info (LOADASYNC only, no START)
            # IMPORTANT: Must pass sessionID along with content_id for LOADASYNC template
            loadresp = ace.GetLOADASYNC({'content_id': content_id, 'sessionID': params['sessionID']})

            # Shutdown connection
            ace.ShutdownAce()

            # Check status
            status = loadresp.get('status', 0)
            available = status in (1, 2)  # 1 = ready, 2 = checking

            self.logger.info('[Statplugin]: Content %s - status=%d, available=%s' % (content_id[:8], status, available))

            return {
                'available': available,
                'infohash': loadresp.get('infohash', ''),
                'status_code': status
            }

        except Exception as e:
            self.logger.error('[Statplugin]: Error checking content_id %s: %s' % (content_id[:8], repr(e)))
            return {
                'available': False,
                'error': str(e)
            }

    @staticmethod
    def send_json_response(data, connection):
        '''Send JSON response'''
        try:
            content = ensure_binary(json.dumps(data, ensure_ascii=False, indent=2))
            connection.send_response(200)
            connection.send_header('Content-Type', 'application/json; charset=utf-8')
            connection.send_header('Content-Length', len(content))
            connection.send_header('Connection', 'close')
            connection.end_headers()
            connection.wfile.write(content)
        except Exception as e:
            logging.error('[Statplugin]: Error sending JSON response: %s' % repr(e))

    @staticmethod
    def send_html_response(content, connection):
        '''Send HTML response'''
        try:
            if isinstance(content, str):
                content = ensure_binary(content)

            connection.send_response(200)
            connection.send_header('Content-Type', 'text/html; charset=utf-8')
            connection.send_header('Content-Length', len(content))
            connection.send_header('Connection', 'close')
            connection.end_headers()
            connection.wfile.write(content)
        except Exception as e:
            logging.error('[Statplugin]: Error sending HTML response: %s' % repr(e))

    @staticmethod
    def get_html_content():
        '''Load HTML content from file or return inline'''
        # Try to load from file first
        try:
            with open('http/statplugin/index.html', 'rb') as f:
                return f.read()
        except:
            # Fallback to inline HTML
            return Statplugin.get_inline_html()

    @staticmethod
    def get_inline_html():
        '''Returns inline HTML when file is not available'''
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plugin Status - HTTPAceProxy</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 20px; }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-box {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            text-align: center;
        }
        .stat-box .label { font-size: 12px; color: #666; margin-bottom: 5px; }
        .stat-box .value { font-size: 24px; font-weight: bold; color: #333; }
        .plugin {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .plugin-header {
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .plugin-header h2 { font-size: 18px; text-transform: capitalize; }
        .plugin-header .count {
            background: rgba(255,255,255,0.2);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
        }
        .channels { padding: 0; }
        .channel {
            padding: 12px 20px;
            border-bottom: 1px solid #eee;
            display: grid;
            grid-template-columns: 40px 1fr 120px 100px;
            gap: 15px;
            align-items: center;
            transition: background 0.2s;
        }
        .channel:hover { background: #f8f9fa; }
        .channel:last-child { border-bottom: none; }
        .channel-logo {
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: 4px;
        }
        .channel-name {
            font-weight: 500;
            color: #333;
            font-size: 14px;
        }
        .channel-id {
            font-family: monospace;
            font-size: 11px;
            color: #999;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .status {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            text-align: center;
        }
        .status.available { background: #d4edda; color: #155724; }
        .status.unavailable { background: #f8d7da; color: #721c24; }
        .status.unknown { background: #e2e3e5; color: #383d41; }
        .status.checking { background: #fff3cd; color: #856404; }
        .check-btn {
            padding: 6px 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .check-btn:hover { background: #0056b3; }
        .check-btn:disabled { background: #ccc; cursor: not-allowed; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .refresh-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HTTPAceProxy - Plugin Status</h1>

        <button class="refresh-btn" onclick="loadPlugins()">🔄 Refresh Data</button>

        <div class="stats">
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="label">Total Plugins</div>
                    <div class="value" id="total-plugins">-</div>
                </div>
                <div class="stat-box">
                    <div class="label">Total Channels</div>
                    <div class="value" id="total-channels">-</div>
                </div>
                <div class="stat-box">
                    <div class="label">Cached Results</div>
                    <div class="value" id="cache-size">-</div>
                </div>
            </div>
        </div>

        <div id="plugins-container">
            <div class="loading">Loading plugins...</div>
        </div>
    </div>

    <script>
        let checkingChannels = new Set();

        function loadPlugins() {
            fetch('/statplugin?action=get_plugins')
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        renderPlugins(data);
                    } else {
                        showError('Failed to load plugins');
                    }
                })
                .catch(err => {
                    showError('Error: ' + err.message);
                });
        }

        function renderPlugins(data) {
            // Update stats
            document.getElementById('total-plugins').textContent = data.total_plugins || 0;
            document.getElementById('cache-size').textContent = data.cache_size || 0;

            let totalChannels = 0;
            data.plugins.forEach(p => totalChannels += p.total_channels);
            document.getElementById('total-channels').textContent = totalChannels;

            // Render plugins
            const container = document.getElementById('plugins-container');
            container.innerHTML = '';

            if (!data.plugins || data.plugins.length === 0) {
                container.innerHTML = '<div class="loading">No plugins with channels found</div>';
                return;
            }

            data.plugins.forEach(plugin => {
                const pluginDiv = document.createElement('div');
                pluginDiv.className = 'plugin';

                const headerDiv = document.createElement('div');
                headerDiv.className = 'plugin-header';
                headerDiv.innerHTML = `
                    <h2>${plugin.name}</h2>
                    <span class="count">${plugin.total_channels} channels</span>
                `;

                const channelsDiv = document.createElement('div');
                channelsDiv.className = 'channels';

                plugin.channels.forEach(channel => {
                    const channelDiv = document.createElement('div');
                    channelDiv.className = 'channel';

                    const logoHtml = channel.logo
                        ? `<img src="${channel.logo}" class="channel-logo" onerror="this.style.display='none'">`
                        : '<div class="channel-logo"></div>';

                    const statusClass = channel.status || 'unknown';
                    const statusText = {
                        'available': '✓ Available',
                        'unavailable': '✗ Unavailable',
                        'unknown': '? Unknown',
                        'checking': '⟳ Checking...'
                    }[statusClass] || '? Unknown';

                    const btnId = `check-${plugin.name}-${channel.content_id}`;

                    channelDiv.innerHTML = `
                        ${logoHtml}
                        <div>
                            <div class="channel-name">${channel.name}</div>
                            <div class="channel-id">${channel.content_id}</div>
                        </div>
                        <div class="status ${statusClass}">${statusText}</div>
                        <button class="check-btn" id="${btnId}"
                                onclick="checkChannel('${plugin.name}', '${encodeURIComponent(channel.name)}', this)">
                            Check
                        </button>
                    `;

                    channelsDiv.appendChild(channelDiv);
                });

                pluginDiv.appendChild(headerDiv);
                pluginDiv.appendChild(channelsDiv);
                container.appendChild(pluginDiv);
            });
        }

        function checkChannel(pluginName, channelName, button) {
            const key = `${pluginName}-${channelName}`;

            if (checkingChannels.has(key)) {
                return;
            }

            checkingChannels.add(key);
            button.disabled = true;
            button.textContent = 'Checking...';

            // Update status to checking
            const channelDiv = button.closest('.channel');
            const statusDiv = channelDiv.querySelector('.status');
            statusDiv.className = 'status checking';
            statusDiv.textContent = '⟳ Checking...';

            fetch(`/statplugin?action=check_channel&plugin=${pluginName}&channel=${channelName}`)
                .then(r => r.json())
                .then(data => {
                    if (data.status === 'success') {
                        const available = data.available;
                        const statusClass = available ? 'available' : 'unavailable';
                        const statusText = available ? '✓ Available' : '✗ Unavailable';

                        statusDiv.className = 'status ' + statusClass;
                        statusDiv.textContent = statusText;

                        button.textContent = data.cached ? 'Cached' : 'Checked';
                    } else {
                        statusDiv.className = 'status unavailable';
                        statusDiv.textContent = '✗ Error';
                        alert('Error: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(err => {
                    statusDiv.className = 'status unavailable';
                    statusDiv.textContent = '✗ Error';
                    alert('Error: ' + err.message);
                })
                .finally(() => {
                    checkingChannels.delete(key);
                    button.disabled = false;
                    button.textContent = 'Check';
                });
        }

        function showError(message) {
            const container = document.getElementById('plugins-container');
            container.innerHTML = `<div class="error">${message}</div>`;
        }

        // Load on page load
        loadPlugins();

        // Auto-refresh every 5 minutes
        setInterval(loadPlugins, 5 * 60 * 1000);
    </script>
</body>
</html>'''
