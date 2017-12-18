nohup ./server_develop.py > server.log 2>&1 &
nohup ./server_master.py > server.log 2>&1 &
nohup python3.5 server_develop.py > server.log 2>&1 &
nohup python3.5 server_master.py > server.log 2>&1 &
