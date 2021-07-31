from flask_zookeeper import FlaskZookeeperClient
from kazoo.client import KazooClient, KazooState
from kazoo.retry import KazooRetry
from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError
from kazoo.exceptions import ConnectionLoss
from kazoo.protocol.states import EventType
import json
import socket 


class ZooKeeperAuthClient(FlaskZookeeperClient):
    def __init__(self):
        super(ZooKeeperAuthClient, self).__init__()
        self.zk = None

    def Start(self):
        self.zk = self.connect()
        
        if not self.zk.connected:
            print("Connection failed.")
        
        self.zk.add_listener(self.state_listener)
        print("Connected to ZooKeeper server")
        self.create_auth_root_node()
        
    def state_listener(self, state):
        if state == KazooState.LOST:
            print("\nConnection Lost!\n")
        elif state == KazooState.SUSPENDED:
            print("\nConnection Suspended!\n")
        elif state == KazooState.CONNECTED:
            print("\nConnected!\n")
            self.create_auth_root_node()

    def create_auth_root_node(self):
        async_obj = self.zk.create_async('/auth')
        async_obj.rawlink(self.create_auth_root_node_callback)

    def create_auth_root_node_callback(self, async_obj):
        try:
            async_obj.get()
        except NodeExistsError:
            pass
        except:
            return # state listener will handle any connection loss
        self.create_auth_node()

    def check_auth_node_exists(self):
        async_obj = self.zk.exists_async('/auth/auth')
        async_obj.rawlink(self.check_auth_node_exists_callback)

    def check_auth_node_exists_callback(self, async_obj):
        try:
            stat = async_obj.get()
            if stat == None:
                self.create_auth_node()
            else:
                self.zk.get_async('/auth/auth', watch=self.auth_node_watcher)
        except:
            pass

    def create_auth_node(self):
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name)
        host_ip = host_ip if host_ip != '127.0.1.1' else '127.0.0.1'
        async_obj = self.zk.create_async('/auth/auth', \
            json.dumps({'hostname': host_name, 'ip': host_ip, 'port': 5000, 'url': 'http://{}:{}/auth/'.format(host_ip, 5000)}).encode('utf-8'), ephemeral=True)
        async_obj.rawlink(self.create_auth_node_callback)

    def create_auth_node_callback(self, async_obj):
        try:
            async_obj.get()
            self.zk.exists_async('/auth/auth', self.auth_node_watcher)
        except NodeExistsError:
            self.zk.exists_async('/auth/auth', self.auth_node_watcher)
        except:
            pass # state listener will handle any connection loss

    def auth_node_watcher(self, watched_event):
        ev_type, state, path = watched_event
        try:
            if ev_type == EventType.CREATED:
                self.zk.exists_async('/auth/auth', self.auth_node_watcher)
            elif ev_type == EventType.DELETED:
                self.create_auth_node()
        except:
            pass # state listener will handle any connection loss
