# ZombireBot
Zombire IRC bot: a multiplayer battle game between zombies and vampires

## How to Install
1. You need `Python3` and `pip3` installed on your system.

2. Run: `pip3 install -r requirements.txt`

3. Register the bot nick on the IRC network you want it to run on, and gives it half-op or higher access in its channel.

4. Copy `config.example.yml` to `config.yml` and change the configuration parameters to your needs.

5. Create the mysql database and user, then run:
```
mysql -u <mysql_user> -D <mysql_db> -p < create_tables.sql
```
6. Run: `python3 zombire.py` and enjoy!

## How to Play
