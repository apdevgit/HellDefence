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
- <ins>PlayerAnimation.cs</ins>: 
- <ins>PlayerAudio.cs</ins>: 
- <ins>PlayerController.cs</ins>: 
- <ins>PlayerCooldown.cs</ins>: 
- <ins>PlayerSpell.cs</ins>: 
- <ins>Stats.cs</ins>: 
## Spells
- BulletStorm.cs: 
- Domestication.cs: 
- Fireball.cs: 
- Gravity.cs: 
- GroundShock.cs: 
- GroundShockTrigger.cs: 
- LavaBeam.cs: 
- MobGroundShock.cs: 
- MobLavaBeam.cs: 
- PlasmaField.cs: 
- Spell.cs: 
- Teleport.cs: 
## UI
- HealthBar.cs: 
- PlayerHealthBar.cs: 
- SpellBar.cs: 
- SpellButtonBehaviour.cs: 
- StatField.cs: 
- StatsPanel.cs: 
## Other
- Billboard.cs: 
- BuffStand.cs: 
- CameraMovement.cs: 
- DamageDealtBillboard.cs: 
- GameController.cs: 
- GameDictionary.cs: 
- PlayersNumber.cs: 
- RigidbodyWrapper.cs: 
- Stats.cs: 
