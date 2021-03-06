# ZombireBot
Zombire IRC bot: a multiplayer mini-RPG battle game between zombies and vampires.

## Prerequisites in IRC environment
ZombireBot works properly if run on Rizon IRC network. It would also work on other IRC networks that use Anope services.

## How to Install
1. You need `Python3` and `pip3` installed on your system, and an access to a MySQL database.

2. Run: `pip3 install -r requirements.txt`

3. Register the bot nick on the IRC network you want it to run on, and gives it the ability to change the channel access.

4. Copy `conf/config.example.yml` to `conf/config.yml` and change the configuration parameters according to your needs.

5. Create the mysql database and user, then run (substituting `mysql_user` and `mysql_db` by their values):
```
mysql -u mysql_user -D mysql_db -p < conf/create_tables.sql
```
Finally, run: `python3 zombire.py` and enjoy!

## How to Play
Vampires and zombies are trying to annihilate and destroy each other. Every player joining the game will be either a vampire or a zombie at random. Vampires can attack zombies only, and vice versa. Furthermore, vampires can heal vampires only, and zombies can heal zombies only.

Each player has the following stats:
- **HP :**  those are the health points (they have no maximum limit per player)
- **MP :**  those represent how many remaining actions the player can do in the current hour
- **Maximum MP :**  those are the maximum actions per hour for the player
- **Score :**  score points awarded for healings and successful attacks
- **Bonus :**  if present, it will give a positive or negative boost to the player attack/defense
- **Equipment :**  sword and armor equipped by the player

Each player upon registration will have an HP of 10, and an MP and Maximum MP of 5.

Each player can take 3 types of **actions** against other players:
- **!attack :**  Both players (attacker and target) will throw a dice each. The difference in dice numbers will be subtracted from the loser's HP and added to the winner's HP. In case of a tie, nothing happens. **If a player's HP reaches 0, he/she will transform automatically to the opposite type (vampire -> zombie or zombie -> vampire)**. Players cannot attack players of the same type. This action consumes 1 MP from the attacking player.
- **!heal :**  The player will sacrifice 2 HP to give an ally 1 HP. The player needs at least 3 HP to make this action. Players cannot heal players of the opposite type. This action consumes 1 MP from the healing player.
- **!ambush :**  Player will attack 2 enemies simultaneously. If the ambush succeeds, he/she will gain 6 HP and the other two will loose 3 HP each. If not, he/she will loose 6 HP and the other two gain 3 HP each. The player needs at least 6 HP to make this action, and it will consume 2 MP from his/her stats.

**Every one hour**, the MP of all players will be regenerated and filled up to their respective Maximum MP.

**About Maximum MP**, if a player makes 5 successful attacks/ambushes in a row (with no ties in between), his/her Maximum MP will go up by 1 point. However, if he/she makes 5 failed attacks/ambushes in row, his/her Maximum MP will go down by 1 point.

**Concerning bonus**, every 3 hours, some players may find random items or get affected by random objects, leading to a temporary positive or negative effect on their attack/defense. The bonus effect will last for 1 hour only.

**Scoring:**
- a healing gives 1 score point
- a successful attack gives 2 score points
- a successful ambush gives 3 score points
- attacking and killing an enemy gives 5 additional score points
- successfully attacking and inflicting damage on the enemy leader gives 10 score points (instead of 2)

**Player settings:**
- `!auto register` command, when set to `on`, allows the player to automatically register when a new round of the game begins.
- `!auto heal` command, if set to `lowest`, will make the player automatically heals the ally with the lowest HP, before the current hour ends. If set to `highest`, the target of healing will be the ally with the highest HP. The player should at least 1 MP remaining for that auto-action to take place.
- `!auto attack` command, similarly to `!auto heal`, allows the player to attack the enemy with the lowest or highest HP, before the current hour ends.
- `!auto search` command, will allow the player to auto-spend 1 MP (if available) to search for an item. It won't work of the user inventory is already full.
- `!auto chest` command, will allow the player to automatically open/drop the chests right after obtaining them.
- Note that enabling `!auto attack` will cancel `!auto heal` and `!auto search`, and vice versa.

**Items:**

Players can search for items and use them. Searching for items using the `!search` command will consume 1 MP. The chance of finding an item is 25%. Be aware that the player inventory has a limited capacity of 3 items.

Some of the items are considered **rare items**. A player cannot have more than 1 unit of the same rare item in his/her inventory.

Here is a full list of the items that can be found:

Item | Can be used on others? | Rare? | Description
---- | ---------------------- | ----- | -----------
Small apple | no | no | +2 HP
Medium apple | no | no | +5 HP
Large apple | no | no | +10 HP
Small lemon | no | no | +1 MP (MP will not go over Maximum MP)
Medium lemon | no | no | +2 MP (MP will not go over Maximum MP)
Large lemon | no | no | +3 MP (MP will not go over Maximum MP)
Transformic | no | yes | tranforms the player to the opposite type without affecting his/her stats
Explodic | yes | yes | suicidal attack (renders the HP of the user and the target to 1)
Neutralic | yes | yes | removes any bonus effect of a particular player
Switchic | yes | yes | switches the HP stats between player and target (consumes the full MP of the player)
Drainic | yes | yes | sacrifices 1 MP to decrease the target's HP by 5
Revealic | yes | yes | reveals the inventory contents of the target
Thievic | yes | yes | steals a random item from the target (if the target has any)
Summonic | no | yes | sacrifices 20 HP to summon the player's leader for 15 minutes
Maintainic | no | yes | increases the lifespan of a sword or an armor by 20

The unused items will remain in the player inventory even after a round ends.

**Chests and Equipment:**

Every new player starts with a wooden sword and a wooden armor, both possessing a power of 0, and both upgradable. 

Upon taking an action (attack, ambush or heal), there is a chance that the player will find a chest, which they can open or drop. The chest may contain one of the seven ores: `Copper`, `Steel`, `Titanium`, `Quartz`, `Sapphire`, `Diamond` and `Bomb`. The ores collected are stored in the player's forge, which has a maximum capacity of 4. Except for `Bomb`, which causes up to 5 HP damage to the player, the other ores can be used to upgrade one's sword or armor, using the `!upgrade` command, as follows:

Sword | Ores in forge | Upgraded form
----- | ------------- | -------------
Wooden sword | 3 Copper | Copper sword (power = 1)
Copper sword | 3 Steel | Steel sword (power = 2)
Steel sword | 3 Titanium | Titanium sword (power = 3)

Armor | Ores in forge | Upgraded form
----- | ------------- | -------------
Wooden armor | 3 Quartz | Quartz armor (power = 1)
Quartz armor | 3 Sapphire | Sapphire armor (power = 2)
Sapphire armor | 3 Diamond | Diamond armor (power = 3)

Furthermore, each sword/armor (except for wooden ones) has lifespan that is decreased by 1 after each use of the sword/armor. If the lifespan reaches 0, the sword or armor will be destroyed and the player will get a wooden sword or armor instead. After successful upgrading, the lifespan of a sword/armor is reset to 100. Item `Maintainic` can also be used to increase the lifespan of a sword or an armor by 20.

Swords and armors play an important role in battles (attacks and ambushes). After rolling dices, swords can help to increase the damage and armors to reduce it. The player with the more powerful equipment used will get the favor in damage increase/decrease.

The sword and armor, along with their lifespans, will remain in the player equipment even after a round ends.

**Special apperarences:**

The respective leaders of vampires and zombies, Count Dracula and General Zombilo, will join the battle once a day at random time, for 15 minutes each. When they are around, their soldiers will have a dramatical boost in attack and defense, temporarily removing any other negative effects. When the leader leaves, his soldiers bonus stats return as they were before his arrival. 

Those leaders can be attacked when they appear using the `!challenge` command. Be aware that they use a 12-face dice though, when the player uses a 6-face dice. A successful attack will award the player 10 score points.

**End of Round:**

The game will end when all players become vampires, or all players become zombies. The highscorer player will have his/her name added to the highscore table, and the round will end removing all players from the game. To participate in a new round, the players will have to type the `!register` command again.

### List of user commands
- **!howtoplay :**  displays a link to this page
- **!register :**  transforms te player into a vampire or a zombie and let him/her participate in the game
- **!unregister :**  removes the player from the game
- **!attack _player_ :**  lets the player attack a player of the opposite type (an enemy)
- **!heal _player_ :**  lets the player heal a player of the same type (an ally)
- **!ambush _player1_ _player2_ :**  lets the player attack 2 enemy players simultaneously
- **!status [_player_] :**  displays the stats of the mentioned player, or displays your own stats if you omit _player_
- **!vampires :**  lists all vampires in the current round
- **!zombies :**  lists all zombies in the current round
- **!topscores** or **!highscores :**  displays the top 10 highscores in the game
- **!auto register [off|on] :**  for reading or changing the auto register setting
- **!auto heal [off|lowest|highest] :**  for reading or changing the auto heal setting
- **!auto attack [off|lowest|highest] :**  for reading or changing the auto attack setting
- **!auto search [off|on] :**  for reading or changing the auto search setting
- **!auto chest [off|open|drop] :**  for reading or changing the auto chest setting
- **!challenge :**  attack the enemy leader if he is around
- **!search :**  searches for a random item (add the item to the inventory if found)
- **!inventory :**  lists the items in your inventory
- **!use _number_ :**  uses item in your inventory on yourself (number can be: 1, 2 or 3)
- **!use _number_ _target_ :**  uses item in your inventory on a target (applies only on few certain items)
- **!drop _number_ :**  drops an item from your inventory (number can be: 1, 2 or 3)
- **!chest open|drop :**  for opening a chest or dropping it after finding one
- **!forge :**  lists all the ores in the forge of the player (max. capacity of the forge is 4)
- **!forge drop _number_ :**  drops an ore from the player's forge
- **!upgrade sword|armor :**  upgrades the sword or armor if the necessary ores are present in the player's forge 
- **!version :**  displays the running version of the bot

### List of admin commands
All admin commands are in the following syntax:
```
/msg <botname> admin <admin_passwd> <command> ...
```
where `<botname>` is the registered nick used by the bot, and `<admin_passwd>` is the one configured in `config.yml` file.

The possible commands are:

- **quit _message_ :**  makes the bot disconnect (*message* is optional and will appear in the bot quitting message)
- **kick _player(s)_ :**  removes player(s) from the game (you can specify a list of players separated by spaces)
- **terminate _player(s)_ :**  similar to **kick**, but delete player settings in addition (such as those set by !auto commands)
- **stats :**  displays the total of vampires and zombies in the current round
- **topscores** or **highscores :**  displays the top 10 highscores with more details
- **clearscores :**  deletes all entries from the highscore table
