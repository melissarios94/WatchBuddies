# WatchBuddies

WatchBuddies is a Discord bot which enables groups of friends to collaborate on a movie watchlist. 

## Getting Started

### Dependencies

* WatchBuddies depends on the Discord API. Before running the script you will need to run `pip3 install discord.py`.
* If you want to use the optional web server which is used to trigger the bot to restart in response to a call to a webhook, you will need to run `pip3 install flask`.

### Installing

1. Clone the repository and install the dependencies.
2. Create a text file called `.env` in the WatchBuddies folder. This file should have 2 lines:
	```
	TOKEN=replace-this-with-your-discord-api-key
	TMDB_API_KEY=replace-this-with-your-tmdb-api-key
	```
*The TMDB_API_KEY is not currently used, so you may choose to provide a dummy value instead. Note that future updates may integrate TMDB functionality, in which case you will need to update your .env file to include an API key.*
3. Configure a new Discord bot with the appropriate permissions.

### Executing program

There are 2 ways to run the program.

#### Run Manually

Run the program manually. Note that this will attach the script to your shell session, which may present an issue if you want to use this as a 24/7, always-on bot. 
	`./WatchBuddies.py`

#### Run Automatically
Run it as a systemd service with an associated Flask server to restart the WatchBuddies script in response to a webhook. This is the recommended method.

1. Create a systemd service file for the Flask server.
	```
	sudo nano /etc/systemd/system/FlaskServer.service
	```
2. Add the following content to the systemd service file, being sure to replace `path-to-repository` with the actual path on your system:
	```
	[Unit]
	Description=Flask Server for tracking changes to WatchBuddies
	After=network.target
	
	[Service]
	User=your_username
	WorkingDirectory=/path-to-repository/WatchBuddies/
	ExecStart=/usr/bin/python3 /path-to-repository/WatchBuddies/flask_server.py
	Restart=always
	
	[Install]
	WantedBy=multi-user.target
	```
3. Enable and start the service, then verify it's running.
	```
	sudo systemctl enable FlaskServer.service
	sudo systemctl start  FlaskServer.service
	sudo systemctl status FlaskServer.service

	```
4. Create a systemd service file:
	```
	sudo nano /etc/systemd/system/WatchBuddies.service
	```
5. Add the following content to the systemd service file, being sure to replace `path-to-repository` with the actual path on your system:
	```
	[Unit]
	Description=WatchBuddies Service
	After=multi-user.target
	
	[Service]
	Type=simple
	ExecStart=/usr/bin/python3 /path-to-repository/WatchBuddies/WatchBuddies.py
	Restart=on-abort
	
	[Install]
	WantedBy=multi-user.target
	```
6. Enable and start the service, then verify it's running.
	```
	sudo systemctl enable WatchBuddies.service
	sudo systemctl start  WatchBuddies.service
	sudo systemctl status WatchBuddies.service
	
	```
7. Set up your version control system to POST a webhook to your server when there are updates to the repository. For example, if your server's IP is 1.1.1.1, you would have the webhook call http://1.1.1.1:5000/webhook.