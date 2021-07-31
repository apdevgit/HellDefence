from flask_zookeeper import FlaskZookeeperClient
from kazoo.client import KazooClient, KazooState
from kazoo.retry import KazooRetry
from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError
from kazoo.exceptions import ConnectionLoss
from kazoo.protocol.states import EventType
from functools import partial
import json
import socket 


class ZooKeeperUIClient(FlaskZookeeperClient):
    def __init__(self, authentication_update_callback, game_master_update_callback):
        super(ZooKeeperUIClient, self).__init__()
        self.zk = None
        self.name = ''
        self.__authentication_update_callback = authentication_update_callback
        self.__game_master_update_callback = game_master_update_callback

    def Start(self):
        self.zk = self.connect()
        
        if not self.zk.connected:
            print("Connection failed.")
        
        self.zk.add_listener(self.state_listener)
        print("Connected to ZooKeeper server")
        self.create_ui_root_node()
        
    def state_listener(self, state):
        if state == KazooState.LOST:
            print("\nConnection Lost!\n")
        elif state == KazooState.SUSPENDED:
            print("\nConnection Suspended!\n")
        elif state == KazooState.CONNECTED:
            print("\nConnected!\n")
            self.create_ui_root_node()

    def create_ui_root_node(self):
        async_obj = self.zk.create_async('/user_interface')
        async_obj.rawlink(self.create_ui_root_node_callback)

    def create_ui_root_node_callback(self, async_obj):
        try:
            async_obj.get()
        except NodeExistsError:
            pass
        except Exception as e:
            print(str(e))
            return # state listener will handle any connection loss
        self.create_ui_node()

    def create_ui_node(self):
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name)
        host_ip = host_ip if host_ip != '127.0.1.1' else '127.0.0.1'
        async_obj = self.zk.create_async('/user_interface/user_interface', \
            json.dumps({'hostname': host_name, 'ip': host_ip, 'port': 5000, 'url': 'http://{}:{}/'.format(host_ip, 5000)}).encode('utf-8'), ephemeral=True, sequence=True)
        async_obj.rawlink(self.create_ui_node_callback)

    def create_ui_node_callback(self, async_obj):
        try:
            path = async_obj.get()
            self.name = path.split('/')[2]
            self.auth_node_exists()
            self.gm_node_exists()
        except NodeExistsError:
            pass # sequential: not going to happen
        except Exception as e:
            print(str(e))
            pass # state listener will handle any connection loss

    def auth_node_exists(self):
        async_obj = self.zk.exists_async('/auth/auth', self.auth_node_exists_watcher)
        async_obj.rawlink(self.auth_node_exists_callback)

    def auth_node_exists_callback(self, async_obj):
        try:
            stat = async_obj.get()
            if stat != None:
                self.get_node_data('/auth/auth')
        except Exception as e:
            print(str(e))
            pass

    def auth_node_exists_watcher(self, watched_event):
        self.auth_node_exists()

    def gm_node_exists(self):
        async_obj = self.zk.exists_async('/gamemaster/gamemaster', self.gm_node_exists_watcher)
        async_obj.rawlink(self.gm_node_exists_callback)

    def gm_node_exists_callback(self, async_obj):
        try:
            stat = async_obj.get()
            if stat != None:
                self.get_node_data('/gamemaster/gamemaster')
        except Exception as e:
            print(str(e))
            pass

    def gm_node_exists_watcher(self, watched_event):
        self.gm_node_exists()

    def get_node_data(self, node):
        async_obj = self.zk.get_async(node)
        async_obj.rawlink(partial(self.get_node_data_callback, node))

    def get_node_data_callback(self, node, async_obj):
        try:
            data, stat = async_obj.get()
            if data != None:
                if node.startswith('/auth/'):
                    self.__authentication_update_callback(json.loads(data.decode('utf-8')).get('url'))
                elif node.startswith('/gamemaster/'):
                    self.__game_master_update_callback(json.loads(data.decode('utf-8')).get('url'))
        except:
            pass
