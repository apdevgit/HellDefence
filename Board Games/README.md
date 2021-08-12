# Board Games (2020)
In this project, a distributed system has been developed using Docker microservices and a RESTful API with the purpose of hosting and managing board games on a site, as a Semester Project for the Distributed Systems course during my Master's studies. More specifically, the users can play tic-tac-toe or chess against each other, in practice matches or in tournaments. Their scores are saved in the database and they are able to search and see their scores or other players' scores. There is also the ability to spectate ongoing matches. In case the service that is responsible for managing each match (PlayMaster Service) crashes, another PlayMaster can start and keep the matches progressing thanks to a system crash recovery implementation.

- Demonstration video: <pending>

## Frameworks/Tools
- Docker
- PostgreSQL
- Apache Zookeeper
- Python
- Flask
- Flask-socketIO
- Flask-jwt-extended
- Flask-sqlAlchemy
- Flask-migrate
- kazoo
- Javascript
- Jinja Templates
- socketIO
- XMLHttpRequest

## Structure
![Microservices Diagram](https://1drv.ms/u/s!AiPNPxTxFVuHeg62LPPdqj6BGHg?e=KlXYYp "Microservices Diagram")

The structure of the application is designed to have one active GameMaster service at a time and one Authorization service. These are the only services in the application that communicate with the Database. The Authorization service uses the database in order to keep track of the registered users and and validate their login credentials. The GameMaster service uses the database to save the completed games as well the game results and the player scores.

Contrastingly, the application can have many active UserInterface services and PlayMaster services. The UserInterface service is the only one to communicate directly with the user browser. Then, depending on the action of the user, it seeks the related information from the Authorization Service (Register, Login) or the GameMaster service (Join a game, See player scores) or the PlayMaster service (Game update, Game move). When a game is created by the GameMaster, it assigns it to an active PlayMaster that it chooses randomly. When the game is finished, the PlayMaster informs the GameMaster that the game is over, providing the game result (winner, loser, draw).

The only known hostnames in the network is the Database and the Zookeeper server. Every service connects to the Zookeeper server and it creates an ephemeral node under the corresponding path, providing its communication information. In this way, other services can notice their presence and communicate with them.

## Services
- <ins>User Interface</ins>: Provides the user interface and it is the only service that receives requests from the user directly through the browser.
- <ins>Authentication</ins>: Responsible for maintaining the user authentication information in addition to the role of the user.
- <ins>GameMaster</ins>: Responsible for keeping the player scores, for pairing players for practice plays and for creating and managing tournaments.
- <ins>PlayMaster</ins>: This service is responsible for managing individual plays. When a play is created by the GameMaster, the GameMaster Service assigns it on an available PlayMaster. Additinally, it saves the current game state on the Zookeeper Server. This way if a PlayMaster crashes, the new PlayMaster can take responsibility for those games that are not under anyone's supervision.
- <ins>Database</ins>: The database in which the user account and game information is saved. It receives information from Authentication Service and GameMaster Service.
- <ins>Zookeeper</ins>: Makes possible the service discovery and PlayMaster crash recovery.

## User Account Roles
- <ins>Player</ins>: A player is an authorized user that can join practice or tournament games as well as spectate other ongoing games.
- <ins>Offical</ins>: Apart from joining and spectating games, an Official can create tournaments.
- <ins>Admin</ins>: Apart from joining and spectating games, an Admin can create other accounts while he can specify their role.

## Zookeeper Nodes
![Zookeeper node hierarchy](https://1drv.ms/u/s!AiPNPxTxFVuHe1lDvJdgYW23YhQ?e=WHH560 "Zookeeper node hierarchy")

## How To Use
For anyone curious, in this sub-section I provide some installation and execution information. Since I haven't uploaded the Service Images on the Docker hub, they have to be built manually.
#### Build Docker Images (command line)
- Download Docker folder located in this repository
- Inside the docker folder run: 
  - sudo docker build -t="user_interface" user_interface_service/.;
  - sudo docker build -t="authentication" authentication_service/.;
  - sudo docker build -t="game_master" game_master_service/.;
  - sudo docker build -t="play_master" play_master_service/.;
  - sudo docker build -t="database" database/.;
  - sudo docker build -t="zookeeper" zookeeper/.;

#### Run The Services
- Create the following docker network by executing: 
  - sudo docker network create board_games_network
- To start every service execute the following commands:
  - sudo docker run -ti --rm --network="board_games_network" --name="database" database;
  - sudo docker run -ti --rm --network="board_games_network" --name="zookeeper" zookeeper;
  - sudo docker run -ti --rm --network="board_games_network" -p 5000:5000 user_interface;
  - sudo docker run -ti --rm --network="board_games_network" authentication;
  - sudo docker run -ti --rm --network="board_games_network" game_master;
  - sudo docker run -ti --rm --network="board_games_network" play_master;
- If you do not want the service to be deleted after it stops: remove --rm flag
- If you want the service to run in the background: remove -ti flag
- If you want to expose Zookeeper to a local port for inspection, add -p <localport>:2181
- If you want to expose postrgreSQL to a local port for inspection, add -p <localport>:5432
- If you want to change UserInterface local port, change -p 5000:5000 to -p <localport>:5000
- If you want to user many UserInterface Services and/or PlayMaster services run the corresponding command again. (Use different local port for each UserInterface Service)




