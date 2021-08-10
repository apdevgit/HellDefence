# Board Games (2020)
In this project, a distributed system has been developed with the purpose of hosting and managing board games on a site, as a Semester Project for the Distributed Systems course during my Master's studies. More specifically, the users can play tic-tac-toe or chess with each other, in practice matches or in tournaments. Their scores and matches are saved in the database and they are able to search and see their scores or other players' scores. There is also the ability to spectate ongoing matches. In case the service that is responsible for managing each match (PlayMaster Service) crashes, another Player Master can arise and keep the matches progressing thanks to a system crash recovery implementation.

## Structure
<pending>

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
