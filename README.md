# binance-trading-robot
 @amfchef binance-trading-robot running on Firebase and Cloud Run hosting a Flask server using Docker
 
## What I did
### Followed the video
I Followed the video and built the application like you see on the video https://www.youtube.com/watch?v=t5EfITuFD9w
The idea is to run @amfchef's code on this structure instead of the presenter's one. 
#### Downloaded the original code
Cloned @amfchef bot at https://github.com/amfchef/binance-trading-bot Great job guy, the code is amazing
#### Moved the files
Moved original files and replace the ones on my the application I built watching the video. Created the function binance-trading-robot-fire on Cloud Run
#### Created the Docker
Created docker file like you see on the video then you add this to the RUN line:  
python-binance binance Werkzeug google-cloud google-cloud-bigquery google-cloud-secret-manager firebase-admin pandas pyarrow
#### Put my keys
Edited the config files and put my keys on

1st here: /server/src/serviceAccountKey.json (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)

2nd here: /server/src/config.py (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)
#### created de build
```bash
gcloud builds submit --tag gcr.io/binance-trading-robot/binance-trading-robot-fire
```
#### deployed new build
```bash
gcloud run deploy --image gcr.io/binance-trading-robot/binance-trading-robot-fire
```
#### Created firebase project binance-trading-robot
went to https://firebase.google.com/ and create a new project to host the role thing
#### init firebase hosting
used this command:
```bash
firebase init hosting
```

## What you should do
### Before you start
#### Install a text editor or IDE
The guy on the video is using https://code.visualstudio.com/ (recommended, I'm using as well)
#### Install Google Cloud SDK
you can find how to do that here https://cloud.google.com/sdk/docs/quickstart
#### login to gcloud
```bash
gcloud auth login
```
#### initialize gcloud
```bash
gcloud init
```

Pick configuration to use:
   Create a new configuration

Choose the account you would like to use to perform operations for 
this configuration:
   select your email

Pick cloud project to use: 
   create a new project

Enter a Project ID
   give it a name


#### Enable Cloud Buid API 
you can find it searching on https://console.cloud.google.com/
#### Enable Cloud Run API
you can find it searching on https://console.cloud.google.com/

## Let's get started
#### Clone my bundle
Clone my code bundle at https://github.com/amfchef/binance-trading-bot and put in your project folder
```bash
git clone https://github.com/amfchef/binance-trading-bot
```
#### Access police

Guarantee that you:

enable billing for the project

enable Cloud Build API

enable Cloud Run API

enable Secret Manager

create key and secret on Secret Manager

added the security rule Secret Manager Accessor for yor compute@developer.gserviceaccount.com

edit calculate.py with your secret address

#### Put your keys
Edit the config files and put your keys on

1st here: /server/src/serviceAccountKey.json (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)

2nd here: /server/src/config.py (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)

#### create de build
First go to your server folder
```bash
cd server
```
And than, inside the folder you execute this command
```bash
gcloud builds submit --tag gcr.io/binance-trading-robot/<put the name of your run function here>
```
#### deploy new build
```bash
gcloud run deploy --image gcr.io/binance-trading-robot/<put the name of your run function here>
```
#### Create firebase project binance-trading-robot
go to https://firebase.google.com/ and create a new project to host the role thing

Then go back to your project main folder

```bash
cd ..
```
And than, inside the folder you execute this command
```bash
npm init
```
and then this
```bash
npm i -D firebase-tools
```

#### init firebase hosting
use this command:
```bash
firebase init hosting
```

That's it!
Go to the https://console.cloud.google.com/ -> Cloud Run and the adress of the service is your webhook. Just use it on your TradingView with MM and this strings on the message of the alert:
 https://github.com/danielvm-git/binance-trading-robot/blob/main/server/src/Webhook/Webhook%20samples.txt
