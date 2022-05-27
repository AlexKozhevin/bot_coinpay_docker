## Telegram Bot, which allows you to track a certain exchange rate on Coinpay.

- For start tracking, you need to enter the pair of currencies and the time interval 
in seconds with separator "@"

Example:

    BTC_USDT @ 60

- To view available pairs, send /get_pairs
- For stop tracking - send /stop

######################################################################################.

## Try this bot in test mode:

https://t.me/coinpay_docker_bot

### To deploy You need:
- Windows 10 + WSL2 (https://docs.microsoft.com/ru-ru/windows/wsl/install)
- Or/ and Ubuntu (or other linux distro)
  (https://www.microsoft.com/ru-ru/p/ubuntu-20044-lts/9mttcl66cpxj?activetab=pivot:overviewtab)
- Docker Desktop (https://docs.docker.com/engine/install/) + enable "Use the WSL2 based engine" in Docker settings
- And your own Telegram bot (use @BotFather https://t.me/BotFather to create one)

### 1. Copy dir bot_coinpay_docker to /home/user/ or:
    mkdir -p /home/<user>/bot_coinpay_docker

    git clone https://github.com/AlexKozhevin/bot_coinpay_docker.git /home/<user>/bot_coinpay_docker

    cd /home/<user>/bot_coinpay_docker

### 2. After that open and modify ***docker-compose.yml*** file to add your Telegram bot TOKEN !
![bot_token](https://user-images.githubusercontent.com/64017080/167243944-bd8d2a76-8cc4-455b-a030-0bed375f1575.png)

### 3. If all ready, run:

    docker-compose up -d

### 4. MongoDB authentication (if you want to use your own user, modify ***docker-compose.yml*** file):

    docker exec -it mongodb bash
    mongo -u mongodbuser -p passw1
#
    show dbs;

    use bot_coinpay;

    db.createUser({user: 'user1', pwd: 'passw1', roles: [{role: 'readWrite', db: 'bot_coinpay'}]})

    exit

#
    exit

### 7. Try sending message to bot!

#######################################################################################

### MongoDB connection via MongoDbCompass:

    mongodb://user1:passw1@<host>:27018/bot_coinpay

# If something goes wrong:


### If after compose up you want to modify any files in repo again, you can run:

    docker-compose down -v

### Modify files and run:

    docker-compose build
    docker-compose up -d

### Don't remember set MongoDB authentication.
