# JerkBot
A Discord bot written in Python for the Antisocial Jerks discord server community.

## Functionality

### Current
1. Add/Remove user roles based on 'Reactions' on a specific discord message
2. Ability to add/remove monitors from reaction roles via commands

### Future
1. Monitor and auto-post free games
2. Handle give-aways for provided Steam Codes

***

## Commands

### Server Admin Only
* `addrole [role name] [emoji]` - Adds a listener for the specified emoji as a response to the ROLEMESSAGEID message 

* `deleterole [role name]` - Removes the listener for the specified role

### All Users
_none_

***

## Setup
1. Update IDs in sample.env
2. Rename sample.env to .env
3. Run `python bot.py`

***

## Packages Used
|Package|Used For|Min Ver|
|-|-|-|
|discord.py|Discord Python library|none|
|dotenv|configuration file|none|
|cogwatch|load command files from directory, auto load new commands and changes|none|
|sqlite3|works with bot.db file to store info|none|