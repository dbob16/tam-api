# TAM FastAPI

This version of Ticket Auction Manager is done up somewhat properly using an API interface instead of pushing the DB calls right out onto the network. It is a bit more efficient and easier to secure (theoretically should be able to be used through an SSH tunnel).

**This is still in active development.**

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

[User demonstration video](https://www.youtube.com/watch?v=xHAemt5uIRo)

