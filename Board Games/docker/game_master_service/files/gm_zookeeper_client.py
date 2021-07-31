from flask_zookeeper import FlaskZookeeperClient
from kazoo.client import KazooClient, KazooState
from kazoo.retry import KazooRetry
from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError
from kazoo.exceptions import ConnectionLoss
from kazoo.protocol.states import EventType
import json
import socket 


class ZooKeeperGMClient(FlaskZookeeperClient):
    def __init__(self, play_master_update_callback):
        super(ZooKeeperGMClient, self).__init__()
        self.zk = None
        self.playmaster_total_nodes_num = 0
        self.playmaster_nodes = []
        self.__play_master_update_callback = play_master_update_callback

    def Start(self):
        self.zk = self.connect()
        
        if not self.zk.connected:
            print("Connection failed.")
        
        self.zk.add_listener(self.state_listener)
        print("Connected to ZooKeeper server")
        self.create_gm_root_node()
        
    def state_listener(self, state):
        if state == KazooState.LOST:
            print("\nConnection Lost!\n")
        elif state == KazooState.SUSPENDED:
            print("\nConnection Suspended!\n")
        elif state == KazooState.CONNECTED:
            print("\nConnected!\n")
            self.create_gm_root_node()

    def create_gm_root_node(self):
        async_obj = self.zk.create_async('/gamemaster')
        async_obj.rawlink(self.create_gm_root_node_callback)

    def create_gm_root_node_callback(self, async_obj):
        try:
            async_obj.get()
        except NodeExistsError:
            pass
        except Exception as e:
            print(str(e))
            return # state listener will handle any connection loss
        self.create_gm_node()

    def check_gm_node_exists(self):
        async_obj = self.zk.exists_async('/gamemaster/gamemaster')
        async_obj.rawlink(self.check_gm_node_exists_callback)

    def check_gm_node_exists_callback(self, async_obj):
        try:
            stat = async_obj.get()
            if stat == None:
                self.create_gm_node()
            else:
                self.zk.get_async('/gamemaster/gamemaster', watch=self.gm_node_watcher)
        except Exception as e:
            print(str(e))
            pass

    def create_gm_node(self):
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name)
        host_ip = host_ip if host_ip != '127.0.1.1' else '127.0.0.1'
        async_obj = self.zk.create_async('/gamemaster/gamemaster', \
            json.dumps({'hostname': host_name, 'ip': host_ip, 'port': 5000, 'url': 'http://{}:{}/gamemaster/'.format(host_ip, 5000)}).encode('utf-8'), ephemeral=True)
        async_obj.rawlink(self.create_gm_node_callback)

    def create_gm_node_callback(self, async_obj):
        try:
            async_obj.get()
            self.zk.exists_async('/gamemaster/gamemaster', self.gm_node_watcher)
            self.pm_root_node_exists()
        except NodeExistsError:
            self.zk.exists_async('/gamemaster/gamemaster', self.gm_node_watcher)
        except Exception as e:
            print(str(e))
            pass # state listener will handle any connection loss

    def gm_node_watcher(self, watched_event):
        ev_type, state, path = watched_event

        if ev_type == EventType.CREATED:
            self.zk.exists_async('/gamemaster/gamemaster', self.gm_node_watcher)
        elif ev_type == EventType.DELETED:
            self.create_gm_node()

    def pm_root_node_exists(self):
        async_obj = self.zk.exists_async('/playmaster', self.pm_root_node_exists_watcher)
        async_obj.rawlink(self.pm_root_node_exists_callback)

    def pm_root_node_exists_callback(self, async_obj):
        try:
            stat = async_obj.get()
            if stat != None:
                self.get_pm_root_children()
        except Exception as e:
            print(str(e))
            pass

    def pm_root_node_exists_watcher(self, watched_event):
        self.pm_root_node_exists()

    def get_pm_root_children(self):
        async_obj = self.zk.get_children_async('/playmaster', self.get_pm_root_children_watcher)
        async_obj.rawlink(self.get_pm_root_children_callback)

    def get_pm_root_children_callback(self, async_obj):
        try:
            children = async_obj.get()
            self.playmaster_total_nodes_num = len(children)
            self.playmaster_nodes = []
            for child in children:
                self.get_pm_node_data(child)
        except Exception as e:
            print(str(e))
            pass

    def get_pm_root_children_watcher(self, watched_event):
        self.get_pm_root_children()

    def get_pm_node_data(self, child_node):
        async_obj = self.zk.get_async('/playmaster/{}'.format(child_node))
        async_obj.rawlink(self.get_pm_node_data_callback)

    def get_pm_node_data_callback(self, async_obj):
        try:
            data, stat = async_obj.get()
            self.playmaster_nodes.append(json.loads(data.decode('utf-8')).get('url'))
            if len(self.playmaster_nodes) == self.playmaster_total_nodes_num:
                self.__play_master_update_callback(self.playmaster_nodes)
        except NoNodeError:
            pass
        except Exception as e:
            print(str(e))
            pass # state listener will handle any connection loss
