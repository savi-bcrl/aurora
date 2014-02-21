import BaseHTTPServer
import json
import logging
import os
from pprint import pprint, pformat
import threading

from ..cls_logger import get_cls_logger

LOGGER = logging.getLogger(__name__)


class ProvisionHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    server_version= "Aurora/0.2"
    
    def __init__(self, *args):
        self.LOGGER = get_cls_logger(self)
        self.LOGGER.info("Constructing...")
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET( self ):
        # Verify request type
        if self.path.startswith("/initial_ap_config_request/"):
            # Open file with name of everything after the request
            try:
                file_name = self.path[27:]
                if ".." in file_name:
                    raise Exception("File names outside directory not permitted.")
                config_file = json.dumps(json.load(open('ap_provision/' + file_name + '.json','r')))
                
            except:
                # File does not exist/ not permitted/ not json
                self.send_response(404)
            else:
                # File OK
                self.send_page("application/json", config_file)
        # Bad request
        else:
            self.send_response( 400 )
    
    # Not implemented
    def do_POST( self ):
        self.send_response( 400 )
    
    # Sends a document
    def send_page( self, type, body ):
        self.send_response( 200 )
        self.send_header( "Content-type", type )
        self.send_header( "Content-length", str(len(body)) )
        self.end_headers()
        self.wfile.write( body )

def get_json_files():
    provision_dir = os.getcwd() + "/core/ap_provision"
    paths = os.listdir(provision_dir)
    result = []
    for fname in paths:
        if fname.endswith(".json"):
            result.append(os.path.join(provision_dir, fname))
    return result

def update_reply_queue(reply_queue):
    flist = get_json_files()
    for fname in flist:
        with open(fname, 'r') as CONFIG_FILE:
            config = json.load(CONFIG_FILE)
        config['rabbitmq_reply_queue'] = reply_queue
        with open(fname, 'w') as CONFIG_FILE:
            json.dump(config, CONFIG_FILE, indent=4)   

def update_last_known_config(ap, config):
    flist = get_json_files()
    ap_config_name = None
    for fname in flist:
        F = open(fname, 'r')
        prev_config = json.load(F)
        if prev_config['queue'] == ap:
            ap_config_name = F.name
            break
    LOGGER.debug(F)
    F.close()
    del F
    prev_config['last_known_config'] = config
    #prev_config['last_known_config']['init_database'] = config['init_database']
    #prev_config['last_known_config']['init_user_id_database'] = config['init_user_id_database']
    config = prev_config
    LOGGER.debug(pformat(config))
    with open(ap_config_name, 'w') as F:
        LOGGER.debug("Dumping config to %s", F.name)
        json.dump(config, F, indent=4)
        LOGGER.info("%s updated for %s", F.name, ap)
    
# Globals definition for starting Provision Server

provision_running = False    
handler_class = ProvisionHandler
server_address = ('', 5555)
server = BaseHTTPServer.HTTPServer(server_address, handler_class)

def run():
    global provision_running
    if not provision_running:

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        LOGGER.info("Starting provision server %s", server_thread)
        provision_running = True
    else:
        LOGGER.warning("Provision server already running")

def stop():
    LOGGER.info("Shutting down provision server...")
    server.shutdown()
