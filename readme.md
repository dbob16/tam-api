# TAM FastAPI

This version of Ticket Auction Manager is done up somewhat properly using an API interface instead of pushing the DB calls right out onto the network. It is a bit more efficient and easier to secure (theoretically should be able to be used through an SSH tunnel).

## Tried and tested

I build these variations of Ticket Auction Manager for the yearly Theme Basket Auction hosted by the SPCA Serving Allegany County. Reason why is the old Excel-based variations by previous volunteers required a lot of human intervention to compile the reports (meaning that some mistakes and frustration happened), and going back to paper didn't work out either.

I found that using a SQL based application worked a lot better. First it was MS Access which was connected to a backend via ODBC. Then I made a Python version which just used a Python connector to connect it to the DB server. I originally thought that the performance bottlenecks plaguing it were solely from the ODBC overhead... but it wasn't.

So I did the only thing that makes sense for a mad computer technician working on a project like this. Learned some API stuff and went to town. This is the result.

> Work willingly at whatever you do, as though you were working for the Lord rather than for people.

Colossians 3:23 (NLT)

So stress testing this with all the resources my computer had, I ran 3-5 threads of just slamming random name and phone number ticket entries into one of its forms. I let it run for several minutes. The total count of rows after it was done got to be 140,148. It never crashed through it.

For safety sake I did add healthchecks to the docker-compose file and the ability to uncomment a section to allow for autohealing (auto restarting) if its FastAPI instance decides to just stop responding.

## Information on setup and use

I plan on making more videos on the setup of it in the future. But for now I have pretty much the same layouts and shortcut keys as the following video once it's setup.

## Textual setup

- Server: Just download and untar into a root-accessible folder on a server with Linux and Docker Engine installed, and run the create_server.sh script, like so:

```sh
sudo -s
mkdir -p /var/docker/tam
cd /var/docker/tam
wget http-path-to-server-tar-file # You can right-click and copy link location on it to get the http path
tar xvzf name-of-server-tar-file
./create_server.sh
ufw allow 80/tcp # If you're using UFW as a firewall
ufw allow 443/tcp # If you're using UFW as a firewall
```

Answer the prompts as needed (the first 5-6 are for certificate generation).

- Client: Just open the latest client then click settings. Change the Base URL to something like `https://ip-of-server/` for SSL/TLS transport, or `http://ip-of-server/` for plaintext. 
    - If you provided an API_PW when setting up the server, provide that and a description of the client computer in the name, click Generate API, then click save. 
    - Click settings again, then the Prefix manager, specify a prefix name, bootstyle (options are in gallery below), and sort order (effects how it's weighted on the dropdown), then click Add/Update (All of this step only has to be done once per server)
    - Then you should be able to close out of the Prefix manager and settings window. Then on the main menu click refresh, then select the prefix you need to enter on the dropdown then click the form button to enter data
    - Enter first and last number of sheet at the top, where it says range control
    - Then enter the data a line at the time
    - Shortcut combos are on the buttons for each task
    - Ctrl+B on the main menu opens the graphical backup and restore options
- CLI Backup and Restore
    - Backup Once
        - `./tam-client backup /path/to/directory/`
        - example: `./tam-client backup ./backups/`
            - Backs up to the backup folder in the current working directory
    - Backup on an interval
        - `./tam-client ibackup /path/to/directory number-of-minutes`
        - example: `./tam-client ibackup ./backups/ 30`
            - Backs up to the backup folder in the current working directory every 30 minutes.
    - Restore
        - `./tam-client restore /path/to/backup/file.json.gz`
        - example: `./tam-client restore ./backups/2025-02-05T12:00:00.json.gz`
            - Restores from a file named 2025-02-05T12:00:00.json.gz out of the backups folder under the current working directory
            - Restores said data to the server configured in the working config file