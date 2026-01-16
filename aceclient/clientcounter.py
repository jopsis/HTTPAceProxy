'''
Client counter for BroadcastStreamer
Multi-channel support with Broadcast Manager
'''
__author__ = 'ValdikSS, AndreyPavlenko, Dorik1972'

from itertools import chain
import gevent
import logging

class Broadcast(object):
    '''
    Represents a single broadcast channel with dedicated AceClient
    Each broadcast has its own AceClient instance and shared queue for its clients
    '''
    def __init__(self, infohash, params):
        import aceclient
        self.infohash = infohash
        self.clients = set()  # Set of clients watching this broadcast
        self.aceClient = None  # Dedicated AceClient for this broadcast
        self.params = params

        # Create dedicated AceClient for this broadcast
        logging.debug('[Broadcast %s]: Creating dedicated AceClient' % infohash[:8])
        self.aceClient = aceclient.AceClient(params)
        self.aceClient.GetAUTH()
        self.aceClient._title = 'Broadcast_%s' % infohash[:8]  # Set title for logging
        logging.info('[Broadcast %s]: AceClient created and authenticated' % infohash[:8])

    def addClient(self, client):
        '''Add a client to this broadcast'''
        self.clients.add(client)

        # Assign broadcast's AceClient to the client
        client.ace = self.aceClient

        # Create INDIVIDUAL queue for this client (not shared!)
        import acedefconfig as AceConfig
        client.q = gevent.queue.Queue(maxsize=AceConfig.AceDefConfig.videotimeout)

        logging.debug('[Broadcast %s]: Client added (total clients: %d)' % (self.infohash[:8], len(self.clients)))
        return len(self.clients)

    def removeClient(self, client):
        '''Remove a client from this broadcast'''
        self.clients.discard(client)
        remaining = len(self.clients)
        logging.debug('[Broadcast %s]: Client removed (remaining: %d)' % (self.infohash[:8], remaining))
        return remaining

    def shutdown(self):
        '''Shutdown this broadcast and cleanup resources'''
        logging.debug('[Broadcast %s]: Shutting down...' % self.infohash[:8])
        try:
            if self.aceClient:
                self.aceClient.StopBroadcast()
                self.aceClient.ShutdownAce()
                logging.info('[Broadcast %s]: AceClient shutdown completed' % self.infohash[:8])
        except Exception as e:
            logging.error('[Broadcast %s]: Error during shutdown: %s' % (self.infohash[:8], repr(e)))

class BroadcastManager(object):
    '''
    Manages multiple broadcast channels
    Creates, reuses, and destroys Broadcast instances based on demand
    '''
    def __init__(self):
        self.broadcasts = {}  # Dictionary: {'infohash': Broadcast}
        self.idleAce = False  # Temporary AceClient for getting content info (not for streaming)
        logging.info('[BroadcastManager]: Initialized')

    def getOrCreateBroadcast(self, infohash, params):
        '''
        Get existing broadcast for this infohash or create a new one
        Returns: Broadcast instance
        '''
        if infohash not in self.broadcasts:
            logging.info('[BroadcastManager]: Creating new broadcast for infohash: %s (total broadcasts: %d -> %d)'
                        % (infohash[:8], len(self.broadcasts), len(self.broadcasts) + 1))
            self.broadcasts[infohash] = Broadcast(infohash, params)
        else:
            logging.debug('[BroadcastManager]: Reusing existing broadcast for infohash: %s' % infohash[:8])

        return self.broadcasts[infohash]

    def removeBroadcast(self, infohash):
        '''
        Remove and shutdown a broadcast when no more clients are watching
        '''
        if infohash in self.broadcasts:
            logging.info('[BroadcastManager]: Removing broadcast for infohash: %s (total broadcasts: %d -> %d)'
                        % (infohash[:8], len(self.broadcasts), len(self.broadcasts) - 1))
            self.broadcasts[infohash].shutdown()
            del self.broadcasts[infohash]
        else:
            logging.warning('[BroadcastManager]: Tried to remove non-existent broadcast: %s' % infohash[:8])

    def getBroadcastCount(self):
        '''Returns the number of active broadcasts'''
        return len(self.broadcasts)

    def getAllClientsList(self):
        '''
        List of all connected clients across all broadcasts
        '''
        return set(chain.from_iterable([b.clients for b in self.broadcasts.values()]))

    def getClientsList(self, infohash):
        '''
        List of clients for a specific broadcast
        '''
        if infohash in self.broadcasts:
            return self.broadcasts[infohash].clients
        return set()

class ClientCounter(BroadcastManager):
    '''
    ClientCounter with BroadcastManager capabilities
    Maintains backward compatibility while adding multi-channel support
    '''
    def __init__(self):
        super(ClientCounter, self).__init__()
        self.clients = {}  # For backward compatibility: {'infohash': set([client1, client2,...])}
        logging.info('[ClientCounter]: Initialized with BroadcastManager support')

    def getClientsList(self, infohash):
        '''List of Clients by infohash (backward compatible)'''
        return self.clients.setdefault(infohash, set())

    def addClient(self, client):
        '''
        Adds client to a broadcast
        Creates new broadcast if needed, or reuses existing one
        Returns the number of clients in this broadcast
        '''
        logging.debug('[ClientCounter]: Adding client for infohash: %s' % client.infohash[:8])

        # Get or create broadcast for this channel
        broadcast = self.getOrCreateBroadcast(client.infohash, client.__dict__)

        # Add client to broadcast (assigns ace and queue to client)
        client_count = broadcast.addClient(client)

        # Maintain backward compatible clients dict (ensure set exists first)
        self.getClientsList(client.infohash).add(client)

        logging.info('[ClientCounter]: Client added to infohash %s (clients in this broadcast: %d, total broadcasts: %d)'
                    % (client.infohash[:8], client_count, self.getBroadcastCount()))

        return client_count

    def deleteClient(self, client):
        '''
        Remove client from broadcast
        Automatically cleanup broadcast if this was the last client
        '''
        logging.debug('[ClientCounter]: Removing client for infohash: %s' % client.infohash[:8])

        try:
            # Remove from backward compatible dict
            self.clients[client.infohash].discard(client)

            # Remove from broadcast
            if client.infohash in self.broadcasts:
                remaining = self.broadcasts[client.infohash].removeClient(client)

                # If no more clients, cleanup broadcast
                if remaining == 0:
                    logging.info('[ClientCounter]: Last client disconnected, removing broadcast for infohash: %s' % client.infohash[:8])
                    self.removeBroadcast(client.infohash)
                    # Cleanup backward compatible dict
                    if client.infohash in self.clients:
                        del self.clients[client.infohash]
                else:
                    logging.debug('[ClientCounter]: Client removed, %d clients remaining in broadcast %s'
                                % (remaining, client.infohash[:8]))

        except KeyError:
            logging.warning('[ClientCounter]: Client not found in dict for infohash: %s' % client.infohash[:8])
        except Exception as e:
            logging.error('[ClientCounter]: Error deleting client: %s' % repr(e))
