from flask_zookeeper import FlaskZookeeperClient
from kazoo.client import KazooClient, KazooState
from kazoo.retry import KazooRetry
from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError
from kazoo.exceptions import ConnectionLoss
from kazoo.exceptions import ZookeeperError
from kazoo.protocol.states import EventType
from functools import partial
import json
import random
import string
import socket 


class ZooKeeperPMClient(FlaskZookeeperClient):
    def __init__(self, game_master_update_callback, update_play_manager_callback):
        super(ZooKeeperPMClient, self).__init__()
        self.zk = None
        self.name = ''
        self.__session_dir = None
        self.__game_master_update_callback = game_master_update_callback

        self.__sessions_to_check = 0
        self.__sessions_checked = 0
        self.__session_with_no_lock_found = False
        self.__is_a_new_session = False

        self.__total_games_len = 0
        self.__total_unserialized_games_count = 0
        self.__play_manager_state = None
        self.__games_state = None

        self.__update_play_manager_callback = update_play_manager_callback

    def Start(self):
        self.zk = self.connect()
        letters = string.ascii_lowercase
        self.name = ''.join(random.choice(letters) for i in range(8))

        if not self.zk.connected:
            print("Connection failed.")
        
        self.zk.add_listener(self.state_listener)
        print("Connected to ZooKeeper server")
        self.gm_node_exists()
        
    def state_listener(self, state):
        if state == KazooState.LOST:
            print("\nConnection Lost!\n")
        elif state == KazooState.SUSPENDED:
            print("\nConnection Suspended!\n")
        elif state == KazooState.CONNECTED:
            print("\nConnected!\n")
            self.gm_node_exists()

    def create_pm_root_node(self):
        async_obj = self.zk.create_async('/playmaster')
        async_obj.rawlink(self.create_pm_root_node_callback)

    def create_pm_root_node_callback(self, async_obj):
        print('create_pm_root_node_callback')
        try:
            async_obj.get()
        except NodeExistsError:
            pass
        except Exception as e:
            print(str(e)+'1')
            return # state listener will handle any connection loss
        self.create_pm_node()

    def create_pm_node(self):
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name)
        host_ip = host_ip if host_ip != '127.0.1.1' else '127.0.0.1'
        async_obj = self.zk.create_async('/playmaster/playmaster-' + self.name, \
            json.dumps({'hostname': host_name, 'ip': host_ip, 'port': 5000, 'url': 'http://{}:{}/playmaster/'.format(host_ip, 5000)}).encode('utf-8'), ephemeral=True)
        async_obj.rawlink(self.create_pm_node_callback)

    def create_pm_node_callback(self, async_obj):
        print('create_pm_node_callback')
        try:
            path = async_obj.get()
        except NodeExistsError:
            pass # unlikely
        except Exception as e:
            print(str(e)+'2')
            pass # state listener will handle any connection loss

    def gm_node_exists(self):
        async_obj = self.zk.exists_async('/gamemaster/gamemaster', self.gm_node_exists_watcher)
        async_obj.rawlink(self.gm_node_exists_callback)

    def gm_node_exists_callback(self, async_obj):
        print('gm_node_exists_callback')
        try:
            stat = async_obj.get()
            if stat != None:
                self.get_gm_node_data()
        except Exception as e:
            print(str(e)+'3')
            pass

    def gm_node_exists_watcher(self, watched_event):
        self.gm_node_exists()

    def get_gm_node_data(self):
        async_obj = self.zk.get_async('/gamemaster/gamemaster')
        async_obj.rawlink(self.get_gm_node_data_callback)

    def get_gm_node_data_callback(self, async_obj):
        print('get_gm_node_data')
        try:
            data, stat = async_obj.get()
            if data != None:
                self.__game_master_update_callback(json.loads(data.decode('utf-8')).get('url'))
                self.create_pm_session_root_node()
        except:
            pass


#######################
### SYSTEM RECOVERY ###
#######################

    def create_pm_session_root_node(self):
            async_obj = self.zk.create_async('/pm_session')
            async_obj.rawlink(self.create_pm_session_root_node_callback)

    def create_pm_session_root_node_callback(self, async_obj):
        print('create_pm_session_root_node_callback')
        try:
            async_obj.get()
            self.get_pm_sessions()
        except NodeExistsError:
            self.get_pm_sessions()
        except Exception as e:
            print(str(e)+'4')
            return # state listener will handle any connection loss

    def get_pm_sessions(self):
        async_obj = self.zk.get_children_async('/pm_session')
        async_obj.rawlink(self.get_pm_sessions_callback)

    def get_pm_sessions_callback(self, async_obj):
        print('get_pm_sessions_callback')
        try:
            sessions = async_obj.get()
            self.__sessions_to_check = len(sessions)
            self.__sessions_checked = 0
            self.__session_with_no_lock_found = False
            if self.__sessions_to_check > 0:
                for session in sessions:
                    self.check_lock_exists('/pm_session/' + session + '/lock')
            else:
                self.create_new_session()
        except Exception as e:
            print(str(e+'5'))
            pass

    def check_lock_exists(self, node_path):
        async_obj = self.zk.get_async(node_path)
        async_obj.rawlink(partial(self.check_lock_exists_callback, node_path))

    def check_lock_exists_callback(self, node_path, async_obj):
        print('check_lock_exists_callback')
        if self.__session_with_no_lock_found:
            return
        try:
            async_obj.get()
            self.__sessions_checked += 1
            if self.__sessions_checked == self.__sessions_to_check:
                self.create_new_session()
        except NoNodeError:
            self.__session_with_no_lock_found = True
            self.create_lock_node(node_path)
        except Exception as e:
            print(str(e)+'6')
            pass

        

    def create_lock_node(self, node_path):
        async_obj = self.zk.create_async(node_path, "playmaster-{}".format(self.name).encode('utf-8'), ephemeral=True)
        async_obj.rawlink(partial(self.create_lock_node_callback))

    def create_lock_node_callback(self, async_obj):
        print('create_lock_node_callback')
        try:
            lock_path = async_obj.get()
            self.__session_dir = lock_path.replace('/lock', '')
            if not self.__is_a_new_session:
                self.load_playmaster_state()
            else:
                self.check_if_loaded()
            print("Lock is set.")
        except Exception as e:
            self.get_pm_sessions() # Restart Process
            print(str(e)+'7')

    def create_new_session(self):
        async_obj = self.zk.create_async('/pm_session/session-' + self.name)
        async_obj.rawlink(self.create_new_session_callback)

    def create_new_session_callback(self, async_obj):
        print('create_new_session_callback')
        try:
            path = async_obj.get()
            self.__is_a_new_session = True
            self.__session_dir = path
            self.create_lock_node(path + '/lock')
            self.create_node(path + '/play_manager', json.dumps({'player_current_game': {}, 'player_ui_url': {}, 'player_spectators': {}}).encode('utf-8'))
        except NodeExistsError:
            pass # fine!
        except Exception as e:
            print(str(e) + '\nRestarting process..')
            self.get_pm_sessions() # Restart process


############################
### SAVE/LOAD MANAGEMENT ###
############################

    def load_playmaster_state(self):
        print('load_playmaster_state')
        self.__games_state = {}
        self.get_play_manager_state()
        self.get_games()

    def get_play_manager_state(self):
        print('get_play_manager_state')
        self.__play_manager_state = None
        async_obj = self.zk.get_async(self.__session_dir + '/play_manager')
        async_obj.rawlink(self.get_play_manager_state_callback)

    def get_play_manager_state_callback(self, async_obj):
        print('get_play_manager_state_callback')
        try:
            data, stat = async_obj.get()

            self.__play_manager_state = json.loads(data.decode('utf-8'))
            self.check_if_loaded()
        except ZookeeperError:
            self.get_play_manager_state()
        except Exception as e:
            print(str(e)+'8')

    def get_games(self):
        async_obj = self.zk.get_children_async(self.__session_dir)
        async_obj.rawlink(self.get_games_callback)

    def get_games_callback(self, async_obj):
        print('get_games_callback')
        try:
            games = async_obj.get()
            self.__total_games_len = len(games) - 2  # lock node, playmaster node
            self.__total_unserialized_games_count = 0
            for game in games:
                if game == 'lock' or game == 'play_manager':
                    continue
                self.load_game(self.__session_dir + '/{}'.format(game))
        except Exception as e:
            print(str(e)+'9')
    
    def load_game(self, node):
        async_obj = self.zk.get_async(node)
        async_obj.rawlink(partial(self.load_game_callback, node))

    def load_game_callback(self, node, async_obj):
        print('load_game_callback')
        try:
            data, stat = async_obj.get()
            data_dict = json.loads(data.decode('utf-8'))
            play_id = data_dict.get('play_id')

            self.__games_state[play_id] = data_dict
            self.__total_unserialized_games_count += 1
            self.check_if_loaded()
        except ZookeeperError:
            self.load_game(node)
        except Exception as e:
            print(str(e)+'10')


    def CreateGame(self, play_id, data):
        print('CreateGame')
        self.create_node(self.__session_dir + '/{}'.format(play_id), json.dumps(data).encode('utf-8'))
    
    def UpdateGame(self, play_id, data):
        print('UpdateGame')
        self.set_node(self.__session_dir + '/{}'.format(play_id), json.dumps(data).encode('utf-8'))

    def RemoveGame(self, play_id):
        print('RemoveGame')
        self.delete_node(self.__session_dir + '/{}'.format(play_id))

    def UpdatePlayManager(self, data):
        print('UpdatePlayManager')
        self.set_node(self.__session_dir + '/play_manager', json.dumps(data).encode('utf-8'))

    def create_node(self, node, data):
        print('create_node')
        async_obj = self.zk.create_async(node, data)
        async_obj.rawlink(partial(self.create_node_callback, node, data))

    def create_node_callback(self, node, data, async_obj):
        print('create_node_callback')
        try:
            async_obj.get()
        except ZookeeperError:
            self.create_node(node, data)
        except Exception as e:
            print(str(e)+'11')

    def set_node(self, node, data):
        print('set_node')
        async_obj = self.zk.set_async(node, data)
        async_obj.rawlink(partial(self.set_node_callback, node, data))

    def set_node_callback(self, node, data, async_obj):
        print('set_node_callback')
        try:
            async_obj.get()
        except NoNodeError:
            pass
        except ZookeeperError:
            self.set_node(node, data)
        except Exception as e:
            print(str(e)+'12')

    def delete_node(self, node):
        print('delete_node')
        async_obj = self.zk.delete_async(node)
        async_obj.rawlink(partial(self.delete_node_callback, node))

    def delete_node_callback(self, node, async_obj):
        print('delete_node_callback')
        try:
            async_obj.get()
        except ZookeeperError:
            self.delete_node(node)
        except Exception as e:
            print(str(e)+'13')

    def check_if_loaded(self):
        print('check_if_loaded')
        if not self.__is_a_new_session:
            if self.__total_games_len == self.__total_unserialized_games_count and self.__play_manager_state != None:
                self.create_pm_root_node()
                self.__update_play_manager_callback(self.__play_manager_state, self.__games_state)
        else:
            self.create_pm_root_node()
            self.__update_play_manager_callback({'player_current_game': {}, 'player_ui_url': {}, 'player_spectators': {}}, {})
