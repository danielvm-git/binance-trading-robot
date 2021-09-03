# binance-trading-robot
 @amfchef binance-trading-robot running on Firebase and Cloud Run hosting a Flask server using Docker
 
## Setup

### Download the code
Clone @amfchef bot at https://github.com/amfchef/binance-trading-bot

### Install Google Cloud SDK
https://cloud.google.com/sdk/docs/quickstart

### Install VS Code
https://code.visualstudio.com/

### Install Firebase Tools
npm init -y
npm i -g firebase-tools

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

### create de build
gcloud builds submit --tag gcr.io/binance-trading-robot/binance-trading-robot-fire

### deploy new build
gcloud run deploy --image gcr.io/binance-trading-robot/binance-trading-robot-fire

### Create firebase project binance-trading-robot
go to https://firebase.google.com/ and create a new project to host the role thing
