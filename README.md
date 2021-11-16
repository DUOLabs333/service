This is the repository for `service`, an alternative to systemd, written completely in bash (a benefit of this is that it's completely cross-platform). To start, move `service` to a location in your PATH. Then, create the folder `~/Services`.

To make a new service, make a folder $SERVICE in Services, and a bash script in $SERVICE with the name $SERVICE (notice that the file has no extension). Remember to write a shell shebang at the top. In the script, write how to run the service, save and make it executable

To run the service in $SERVICE, run `service start $SERVICE`. To stop them, run `service stop $SERVICE`.

This is not meant to a complete replacement for systemd, but is meant to be a lightweight alternative to managing services without having to resort to something like Docker.

If you want to start `service` at boot, put this script in the appropiate area: 
```
service start --all
```
