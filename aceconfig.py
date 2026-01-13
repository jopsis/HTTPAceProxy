'''
AceProxy configuration script
Copy acedefconfig.py to aceconfig.py and change only needed options.
'''
import acedefconfig, logging, os
from aceclient.acemessages import AceConst

class AceConfig(acedefconfig.AceDefConfig):
    '''
    Configuration class for AceProxy.
    Override any settings from AceDefConfig here.
    '''
    # Ace Stream configuration
    # acespawn = True  # Set to True if you want to automatically start AceStream Engine
    # acecmd = 'acestreamengine --client-console'

    # Ace Stream Engine connection (can be overridden with environment variables)
    ace = {
        'aceHostIP': os.getenv('ACESTREAM_HOST', '127.0.0.1'),
        'aceAPIport': os.getenv('ACESTREAM_API_PORT', '62062'),
        'aceHTTPport': os.getenv('ACESTREAM_HTTP_PORT', '6878')
    }

    # HTTP Server configuration
    httphost = '0.0.0.0'  # Listen on all interfaces
    httpport = 8888  # Changed to avoid conflict with other service

    # Connection limits
    # maxconns = 20

    # Firewall settings
    # firewall = True
    # firewallnetranges = ('127.0.0.1', '192.168.0.0/16', '10.0.0.0/8')

    # Logging
    # loglevel = logging.INFO

    pass
