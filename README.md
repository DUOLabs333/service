This is the repository for `service`, an alternative to systemd, written completely in bash. To start,  move `service` to a location in your PATH. Then, create the folder `~/Services`.

To make a new service, make a folder $SERVICE in Services, and a bash script in $SERVICE with the name $FOLDER (notice that the file has no extension). Remember to write a shell shebang at the top. In the script, write how to run the service and save. 

To run the service in $FOLDER, run `nohup service start $SERVICE &`. To stop them, run `service stop $SERVICE`.
