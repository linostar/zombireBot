# ZombireBot
Zombire IRC bot: a multiplayer mini-RPG battle game between zombies and vampires

## Pre-requisites in IRC environment
ZombireBot works properly if run on Rizon IRC network. It would also work on other IRC networks that use Anope services.

## How to Install
1. You need `Python3` and `pip3` installed on your system.

2. Run: `pip3 install -r requirements.txt`

3. Register the bot nick on the IRC network you want it to run on, and gives it half-op or higher access in its channel.

4. Copy `conf/config.example.yml` to `conf/config.yml` and change the configuration parameters to your needs.

5. Create the mysql database and user, then run:
```
mysql -u <mysql_user> -D <mysql_db> -p < conf/create_tables.sql
```
6. Make sure you give the bot the ability to change its channel access.

7. Run: `python3 zombire.py` and enjoy!

## How to Play
Vampires and zombies are trying to annihilate and destroy each other. Every player joining the game will be either a vampire or a zombie at random. Vampires can attack zombies only, and vice versa. Furthermore, vampires can heal vampires, and zombies can heal zombies.

Each player has the following stats:
- **HP**  those are the health points (they have no maximum limit per player)
- **MP**  those represent how many remaining actions the player can do in the current hour
- **Maximum MP**  those are the maximum actions per hour for the player
- **Score**  each successful attack will gives the player one point in Score
- **Bonus**  if present, it will give a positive or negative boost to the player attack/defense

Each player upon registration will have an HP of 10, and an MP and Maximum MP of 5.

Each player can take two types of **actions** against other players. Both actions will consume 1 MP from the player stats:
- **!attack**  Both players (attacker and target) will throw a dice each. The difference in dice numbers will be subtracted from the loser's HP and added to the winner's HP. In case of a tie, nothing happens. **If a player's HP reaches 0, he/she will transform automatically to the opposite type (vampire -> zombie or zombie -> vampire)**. Players cannot attack players of the same type.
- **!heal**  The player will sacrifice 2 HP to give an ally 1 HP. The player needs at least 3 HP to make this action. Players cannot heal players of the opposite type.

**Each one hour**, the MP of all players will be regenerated and filled up to their respective Maximum MP.

**About Maximum MP**, if a player makes 5 successful attacks in a row (with no ties in between), his/her Maximum MP will go up by 1 point. However, if he/she makes 5 failed attacks in row, his/her Maximum MP will go down by 1 point.

**Concerning bonus**, every 3 hours, some players may find random items or get affected by random objects, leading to a temporary positive or negative effect on their attack/defense. The bonus effect will last for 1 hour only.

**The game will end** when all players become vampires, or all players become zombies. The highscorer player will have his/her name added to the highscore table, and the round will end removing all players from the game. To participate in a new round, the players will have to type the `!register` command again.

### List of user commands
- **!howtoplay**  displays a link to this page
- **!register**  transforms te player into a vampire or a zombie and let him/her participate in the game
- **!unregister**  removes the player from the game
- **!attack _player_**  lets the player attack a player of the opposite type (an enemy)
- **!heal _player_**  lets the player heal a player of the same type (an ally)
- **!status _player_**  displays the stats of the mentioned player
- **!vampires**  lists all vampires in the current round
- **!zombies**  lists all zombies in the current round
- **!topscores** or **!highscores**  displays the top 10 highscores in the game

### List of admin commands
All admin commands are in the following syntax:
```
/msg <botname> admin <admin_passwd> <command> ...
```
where `<botname>` is the registered nick used by the bot, and `<admin_passwd>` is the one configured in `config.yml` file.

The possible commands are:

- **quit _message_**  makes the bot disconnect (*message* is optional and will appear in the bot quitting message)
- **kick _player_**  removes `player` from the game
- **stats**  displays the total of vampires and zombies in the current round
- **topscores** or **highscores**  displays the top 10 highscores with more details
