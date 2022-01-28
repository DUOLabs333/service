This is the repository for `service`, an alternative to systemd, written completely in bash (a benefit of this is that it's completely cross-platform). This is not meant to a complete replacement for systemd, but is meant to be a lightweight alternative to managing services without having to resort to something like Docker. 


To start, move `service` to a location in your PATH. Then, create the folder `~/Services`.

To make a new service with name $NAME, run `service new $NAME`. Then, edit `~/Services/$NAME/service` with how to run the service, relative to the `data` directory, which is where all the things needed to run the service is held.

To run the service `$NAME`, run `service start $NAME`. To stop it, run `service stop $NAME`. You can optionally use instead the same options you use for `list`.

You can also:
* List services with `list`, with options `--all`, `--enabled`, and `--running`
* Read the log with `log`
* Get status with `status`
* Enable and disable with `enable` and `disable`, respectively.
* Edit script on the command line with `edit`
* Restart with `restart`, with the same options you can use for `list`.

If you want to start `service` at boot, put this script in the appropiate area: 
```
service start
```
