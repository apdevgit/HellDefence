# Scripts
A brief explanation for the purpose of every script.
## Drops
- <ins>Drop.cs</ins>: It drops (instantiates) a selected gameobject to its parent gameobject position based on a probability value.
- <ins>Healthkit.cs</ins>: The component script for the Healthkit functionality. The moment the player comes into the defined range, it heals the player for a certain amount of health points, creating at the same time a corresponding visual effect for a period of time.
## Enums
These scripts contain definitions of different enum types that are used: Mob, PlayerNumber (for player1 and player2), SpellName, SpellType, StatCategory, StatType.
## Menu
- <ins>GameMenuManager.cs</ins>: Manages the in-game menu, so the player can pause, resume, exit the game or go back to the main menu.
- <ins>MenuManager.cs</ins>: Manages the flow of the main menu which is the first scene when the user starts the game. More specifically, the user can start tha game, visit the HowToPlay and Controls section, select the number of players (1 or 2) or exit the game.
## Mobs Behaviour
- <ins>Cast.cs</ins>: It is used for every enemy that its attack type is casting spells. When the CastSpell method is called, whichever spell gameobject is selected it gets casted (instantiated) on a specific location. This location is searched and set on the beggining of the script/component, based on a child transform node with a tag name set to "CastPoint".
- <ins>LivingEntity.cs</ins>: Implements the functionality of a living entity in the scene (player, enemies etc). It manages and provides information of the total health points of an entity, the regeneration value as well as if the entity is alive or dead.
- <ins>MobAttackPoint.cs</ins>: Manages the collider that reflects if the weapon of the mob hits an enemy and calls the corresponding MobBehaviour script method of its parent component.
- <ins>MobBehaviour.cs</ins>: This script implements the core functionality of the enemy behaviour. This behaviour is based on 4 AI states (Roaming, Chasing, Attacking, Resting). During the Roaming state, the script calculates a new position for the enemy to move. If the player is in the predefined range, the Chasing state follows. In this state, the player in range is targeted and when the enemy reaches a the valid range of attacking, the state changes to Attacking state. During the attacking state, depending on the enemy's type of attack (meelee, ranged, spellcaster) the attack action is activated. After every attack action the enemy changes state to Resting, in which some predefined time has to pass till the enemy can move/attack again.
- <ins>Throw.cs</ins>: Implements the attack functionality of an entity which its attack type is ranged. It throws (instantiates) the selected object (arrow, dagger etc) in a specific location and with a specific velocity and rotation. The location mentioned is searched and set by the script depending on which Transform child node has the NameTag = "ThrowPoint".
- <ins>ThrowingObject.cs</ins>: This script is attached as a component to an object that was initiated from the Throw.cs script and is responsible to check for collisions, that is if it has hit an enemy or a wall. In that case, is changes the enemy damage accordingly and destroys itself. It also destroys itself if there is not any collision and a certain amount of time has passed.
## Player
- <ins>PlayerAnimation.cs</ins>: The 'middleware' between the player scripts and the Unity Animator Controller, in order to make the animation transitions correctly, based on the player actions.
- <ins>PlayerAudio.cs</ins>: A simple script that helps with playing sound clips, using the AudioSource attached to the object Transform.
- <ins>PlayerController.cs</ins>: Manages the player input and the player's core functionality, making use of other helpful player components/scripts such as PlayerAnimation, PlayerSpell and PlayerCooldown.
- <ins>PlayerCooldown.cs</ins>: Keeps track of the player spell cooldowns. In this way, it provides the information of whether a spell can be casted and also how much time is left untill the spell is ready.
- <ins>PlayerSpell.cs</ins>: Manages the spell casting system and the corresponding player movement during the casting of a spell.
- <ins>Stats.cs</ins>: Keeps track of the initial stats of the player (speed, damage, cooldown etc) and is also responsible of updating and calculating the total values of the player stats after receiving extra stats from the Buff Areas.
## Spells
The scripts in this folder implement the functionality of every spell in the game.
## UI
- <ins>HealthBar.cs</ins>: Provides the functionality (color change, health bar offset) of the health bar that is located over every living entity.
- <ins>PlayerHealthBar.cs</ins>: This script manages the color and the movement of the bar representing the player current health points on the top left side of the screen.
- <ins>SpellBar.cs</ins>: Manages the player spell bar. 
- <ins>SpellButtonBehaviour.cs</ins>: Represents the icon of a spell that is placed in the player SpellBar, providing information about the spell cooldown.
- <ins>StatField.cs</ins>: Represents the stat entity, providing information about the stat that can be visualized on the StatsPanel, such as the remaining time the stat type.
- <ins>StatsPanel.cs</ins>: Manages to show the list of the stats that the player has acquired.
## Other
- <ins>Billboard.cs</ins>: Makes the attached UI element look at direction perpendicular to the camera local-x axis. It is used on living entities health bars.
- <ins>BuffStand.cs</ins>: Implements the functionality of buff areas, that is the areas that can give the player a specific buff when he/she reaches them. It also keeps information about the probability of giving any specific buff type (spell, stat, full heal) as well as the probability of giving anything at all.
- <ins>CameraMovement.cs</ins>: Manages the camera movement as the player moves during the game. It also supports camera for two players and camera transition from Two players to One player when either one of the players is defeated.
- <ins>DamageDealtBillboard.cs</ins>: Creates a short animation showing a number moving upwards, representing the number of health points lost during an attack.
- <ins>GameController.cs</ins>: Manages the core functionality of the game. That is, loading and instantiating the enemies for each wave, keeping track of the enemies that were defeated, activating the Buff Areas at the beggining of each wave and also react to player win or defeat.
- <ins>GameDictionary.cs</ins>: It keeps data about spell and stat properties and it also provides key to value pairs that make the use of specific information to other scripts easier.
- <ins>PlayersNumber.cs</ins>: Keeps information of the game mode (1 Player or 2 Players)
- <ins>RigidbodyWrapper.cs</ins>: This script is responsible for the player movement and physics. Its main purpose is to make the player movement be affected by two parameters. First, the constant speed with which the player is moving, in addition to the speed derived from the external forces (enemy attacks). External forces are decreaced overtime under the influence of the friction.
- <ins>Stats.cs</ins>: A Class that represents a stat, its type and the category in which it belongs.
