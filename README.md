# binance-trading-robot
[![Project Version][version-image]][version-url]
[![Frontend][Frontend-image]][Frontend-url]
[![Backend][Backend-image]][Backend-url]

The objective of this project is to create a cryptocurrency buying and selling robot to operate from signals sent by TradingView.com indicators

## Description
BEFORE YOU START WATCH:

* THIS VIDEO 1ST: [video](https://www.youtube.com/watch?v=t5EfITuFD9w)

* THIS VIDEO 2ND: [video](https://www.youtube.com/watch?v=WwZDwYz-3AQ)

This is the same [amfchef's](https://github.com/amfchef) binance-trading-robot running on Firebase and Cloud Run hosting a Flask server using Docker.
I followed this [video](https://www.youtube.com/watch?v=t5EfITuFD9w) and migrated amfchef's [code](https://github.com/amfchef/binance-trading-bot) to run on [Firebase](https://firebase.google.com/) 

IMPORTANT: I'm using it just for longs and just for USDT pairs, it was not tested on BTC pairs. Runned just a feel tests with SHORTS.

## Getting Started
### Dependencies

My OS is OSX_BigSur so I need [Command Line Tools](https://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/) (just for mac)
```bash
xcode-select --install
````
* I'm using these packages on it: 
  * PYTHON: 
    * 3.8.2 
  * JAVA:
    * 16.0.2
  * NODE:
    * 10.24.1 (didn't work with latest version 16) 
  * NPM:
    * 7.21.1 
  * PIP:
    * 19.2.3
  * NVM:
    * 0.38.0
  * GIT:
    * 2.30.1

## Installing
#### Install a text editor or IDE
The guy on the video is using https://code.visualstudio.com/ (this was recommended in the video above, I'm using it as well)

#### Check what you have
* check your JAVA, PYTHON, NVM, NODE, NPM, PIP and GIT versions on Terminal or CMD
```bash
java -version
```
```bash
python3 --version
```
```bash
nvm --version
```
```bash
node --version
```
```bash
npm --version
````
```bash
pip3 --version
````
```bash
git --version
````

#### Install missing packages
Install whatever package above you don't have. You can find the best way for your OS on google

I recommend using [nvm](https://github.com/nvm-sh/nvm) to install the desired node version

#### Install Google Cloud SDK
You can find how to do that here https://cloud.google.com/sdk/docs/quickstart

#### Clone my bundle

* Change directory to your project

```bash
cd "your_project" folder
````

* Clone my repo

```bash
git clone https://github.com/danielvm-git/binance-trading-robot
````

#### Install virtual environment
* Open your VSCode
* Add the folder you just cloned to the workspace
* Open a new terminal inside VSCodec(menu->terminal-> new terminal)
* Create a virtual environment
```bash
python3 -m venv env
````
* Activate virtual environment
```bash
source ./env/bin/activate
````
* Activate virtual environment
```bash
pip install --upgrade pip
````
* Install dependencies
```bash
pip3 install -r requirements.txt
````
#### login to gcloud
```bash
gcloud auth login
```
#### initialize gcloud
```bash
gcloud init
```

* Pick configuration to use:
   * Create a new configuration

* Choose the account you would like to use to perform operations for 
this configuration:
   * select your email

* Pick cloud project to use: 
   * create a new project

* Enter a Project ID
   * give it a name


#### Enable project billing and Cloud APIs 
* Go to Google Cloud Console Dashboard, select you project, click on billing and select the billing account that you will use on the project

you can find it searching for the API name on https://console.cloud.google.com/
* Enable Cloud Run API
* Enable Cloud Build API
* Enable Secret Manager API

#### Create your Binance API
*  go to [Binance API management](https://www.binance.com/en/my/settings/api-management) and do the thing there. You will receive an API-key and API-secret number. You need to add these numbers to the Secret Manager next.

#### API Key and password setup
* Go to https://console.cloud.google.com/ and search for Secret Manager
* create API key, API secret and password on Google Secret Manager. Keep the name of each secret you create
* Use these names on the keys
     *  trade_password_binance_margin
     *  exchange_api_key_binance_margin
     *  exchange_api_secret_binance_margin

#### Security Polices
* Go to https://console.cloud.google.com/ and search for IAM
* add the security rule Secret Manager Accessor for your blablabla.compute@developer.gserviceaccount.com

#### Put your keys
Open the source code folder with VSCode and edit the files to put your keys on

* 1st here: /app/config.py (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)
     * change project_id (here is the name)
     * change password_request ("projects/<put your project number here>/secrets/trade_password_binance_margin/versions/latest") 

Create the project on firebase 
go to https://firebase.google.com/ and create a new project to host the role thing
* 2nd here: /server/src/serviceAccountKey.json (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)
* change the rules on firestore database to be like that
```bash
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read;
      allow write: if false;
    }
  }
}
````
 
#### create de build
Open a Terminal inside your VSCode.
If it's not on you project folder you first go to the folder where you cloned the repository
```bash
cd "your_project" folder
````
Inside the folder you execute this command
```bash
gcloud builds submit --tag gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
```
#### deploy new build
```bash
gcloud run deploy --image gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
```
#### init firebase project 

* On your project main folder you execute this command on the VS Code Terminal
```bash
npm init
```
* and then this
```bash
npm install -g firebase-tools
```
* edit .firebaserc to put your project name
 
* edit firebase.json to put your function name
 
* init firebase hosting
use this command to select the firebase project
```bash 
firebase use --add
```
* And then deploy the firebase 
```bash
firebase deploy --only hosting
```
### That's it!
Go to [Google Cloud Console](https://console.cloud.google.com/) -> Cloud Run and the address of the service created is your webhook. Just use it on your TradingView with MM indicator
 
## Running the tests 
#### Webhook
 * You can also use [Insomnia](https://insomnia.rest/) to simulate TradingView sending a POST to your webhook
     * Find examples of how the json should be structured [here](https://github.com/danielvm-git/binance-trading-robot/tree/main/server/src/Webhook)
     * The same json should be used inside you alert on TradingView

#### Local Test
 * You can also run the firebase server and test locally. The result of the command bellow will be a localhost address
 ```bash
firebase serve
```
#### Cloud Run Test
 * Create the build and deploy is again. The result of the deploy command bellow will be an internet address to your site
 ```bash
gcloud builds submit --tag gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
``` 
 ```bash
gcloud run deploy --image gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
``` 
#### Firebase Test
 * Create the build and deploy is again. The result of the deploy command bellow will be an internet address to your site
 ```bash
firebase deploy --only hosting
``` 
## Help
### Troubleshooting
* if the docker doesn't run try cleaning minikube and starting the service again
```bash
minikube delete --all
```
* if the build fail try resetting the connections with gcloud, it happens sometimes at the begging of a coding session
```bash
gcloud auth application-default login
```
* if you get stacked on the billing piece of the process because google doesn't allow your payment method try to finish the process on your cell phone (thanks to @hardeydhoying)
 
* set the region to avoid been asked each time you run the build (I'm using US central)
```bash 
gcloud config set run/region us-central1
``` 

## Contributing

1. Fork it (<https://github.com/danielvm-git/binance-trading-robot/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Version History
* 0.0.5
 * New feature - MM's spreadsheet helper
 * Layout - new field "Side" on Open Positions table 
 * Bugfix - Fix for value calculation on Stop Loss and Stop Loss trigger condition  
* 0.0.4
 * New feature - Entry and Exit shorts
* 0.0.3
  * Layout enhancements
* 0.0.2
  * New look and feel
  * Bug fix - stop loss not being created
  * Re-factory routes.py
  * Save orders result to firestore
* 0.0.1
  * Initial work

## License

This project is licensed under the MIT License - see the LICENSE.md file for details 
 
## Authors

[@amfchef](https://github.com/amfchef) - Original code
 
[@danielvm-git](https://github.com/danielvm-git) - Contributor
 
## Support
if you want to buy me a coffee to accompany me on the programming nights I will always be grateful
* BTC 1NJ7SxaRaCaJU8BjPeP9wWM8qW4dpwEKzS
* LTC LZNGMCpeEEYpikVHwq1pDN7ugF2gMXKf3z
* TRX TNwPjgLwWSYmjjf6iSzF7nvkdYrzgvi87h
* ETH (ERC20) 0x210cee0b909dc0a4fb08f4bb7882d2fbd1f05b9a
* USDT (TRC20) TNwPjgLwWSYmjjf6iSzF7nvkdYrzgvi87h

## Acknowledgments
Thanks a lot for all the good job that [@amfchef](https://github.com/amfchef) made on the original code that I used here and also for all the [Discord](https://discord.com/invite/u2FcPxy) group folks for their support

<!-- Markdown link & img dfn's -->

[version-image]: https://img.shields.io/badge/Version-0.0.3-brightgreen?style=for-the-badge&logo=appveyor
[version-url]: https://img.shields.io/badge/version-0.0.3-green
[Frontend-image]: https://img.shields.io/badge/Frontend-Bootstrap-blue?style=for-the-badge
[Frontend-url]: https://img.shields.io/badge/Frontend-Bootstrap-blue?style=for-the-badge
[Backend-image]: https://img.shields.io/badge/Backend-Python-important?style=for-the-badge
[Backend-url]: https://img.shields.io/badge/Backend-Python-important?style=for-the-badge

