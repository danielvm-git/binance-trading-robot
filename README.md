# binance-trading-robot
 @amfchef binance-trading-robot running on Firebase and Cloud Run hosting a Flask server using Docker
 
## Setup

### Install a text editor or IDE
The guy on the video is using https://code.visualstudio.com/ (recommended, I'm usind as well)

### Install Google Cloud SDK
you can find how to do that here https://cloud.google.com/sdk/docs/quickstart

### login to gcloud
gcloud auth login

### initialize gcloud
gcloud init
    give it a name - 
    select your email
    create a new project -
    
### Enable Cloud Buid API 
you can find it searching on https://console.cloud.google.com/

### Enable Cloud Run API
you can find it searching on https://console.cloud.google.com/
    
### Follow the video
Follow the video and build the application like you see on the video https://www.youtube.com/watch?v=t5EfITuFD9w

#### Install Firebase Tools
npm init -y
npm i -D firebase-tools

#### Download the original code
Clone @amfchef bot at https://github.com/amfchef/binance-trading-bot Great job guy, the code is amazing

#### Move the files
Move original files and replace the ones on your tutorial exercise. The idea is to run @amfchef's code on this structure instead of the presenter's one

#### Create the Docker
create docker file like you see on the video then you add this to the run line:  
python-binance binance Werkzeug google-cloud google-cloud-bigquery google-cloud-secret-manager firebase-admin pandas pyarrow

#### Put your keys
Edit the config files and put your keys on
1st here: /server/src/serviceAccountKey.json (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)
2nd here: /server/src/config.py (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)

#### create de build
gcloud builds submit --tag gcr.io/binance-trading-robot/binance-trading-robot-fire

#### deploy new build
gcloud run deploy --image gcr.io/binance-trading-robot/binance-trading-robot-fire

#### Create firebase project binance-trading-robot
go to https://firebase.google.com/ and create a new project to host the role thing

#### init firebase hosting
use this command:
firebase init hosting

That's it!
