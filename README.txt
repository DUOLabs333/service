This is the repository for service, an alternative to systemd, written completely in Python. This is not meant to a complete replacement for systemd, but is meant to be a lightweight alternative to managing services (similar to OpenRC).


To start, move service to a location in your PATH. Then, create the folder ~/Services.

To make a new service with name $NAME, run 'service init $NAME'. Then, edit ~/Services/$NAME/service with how to run the service, relative to the data directory, which is where all the things needed to run the service is held.

To run the service $NAME, run service start $NAME. To stop it, run service stop $NAME. You can optionally use instead the same options you use for list.

You can also:
* List services with list, with options --all, --enabled, and --running
* Read the log with log
* Get status with status
* Enable and disable with enable and disable, respectively.
* Edit script on the command line with edit
* Restart with restart, with the same options you can use for list.
* Make a new service with init

If you want to start service at boot, put this script in the appropriate area: 

service start --enabled


Commands:
In your service script for each service, you can have different commands.

Down(command): When 'service stop $NAME' is run, runs command. You can run this command multiple times, and when 'service stop $NAME' is run, it will start from the first Down command onwards. command can either be a bash string or Python function

Loop(command,delay): Run command in a loop with delay seconds between each invocation in the background.

Container(container): Special support for my container program. Start $container in the background

Env(env): Adds env to your environment in the script