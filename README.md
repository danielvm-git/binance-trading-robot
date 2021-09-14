# binance-trading-robot
[![Project Version][version-image]][version-url]
[![Frontend][Frontend-image]][Frontend-url]
[![Backend][Backend-image]][Backend-url]

The objective of this project is to create a cryptocurrency buying and selling robot to operate from signals sent by TradingView.com indicators

## Description
This is the same [amfchef's](https://github.com/amfchef) binance-trading-robot running on Firebase and Cloud Run hosting a Flask server using Docker.
I followed this [video](https://www.youtube.com/watch?v=t5EfITuFD9w) and migrated amfchef's [code](https://github.com/amfchef/binance-trading-bot) to run on [Firebase](https://firebase.google.com/) 

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
* check your JAVA version on Terminal or CMD
```bash
java -version
```
* check your PYTHON version
```bash
python3 --version
```
* check your NVM version
```bash
nvm --version
```
* check your NODE version
```bash
node --version
```
* check your NPM version
```bash
npm --version
````
* check your PIP version
```bash
pip3 --version
````
* check your GIT version
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
* Change directory to your project
```bash
cd "your_project" folder
````
* Install virtual environment
```bash
pip3 install python3-venv
````
* Create a virtual environment
```bash
virtualenv venv 
````
* Activate virtual environment
```bash
source venv/bin/activate
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

* 1st here: /server/src/app.py (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)
     * change project_id (here is the name)
     * change password_request ("projects/<put your project number here>/secrets/trade_password_binance_margin/versions/latest") 
 
* 2nd here: /server/src/calculate.py (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)
     * change project_id (here is the name)
     * change key_request ("projects/<put your project number here>/secrets/exchange_api_key_binance_margin/versions/latest")
     * change secret_request ("projects/<put your project number here>/secrets/exchange_api_secret_binance_margin/versions/latest") 

* 3rd here: /server/src/serviceAccountKey.json (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)
 
#### create de build
Open a Terminal inside your VSCode.
If it's not on you project folder you first go to the folder where you cloned the repository
```bash
cd "your_project" folder
````
go to your server folder
```bash
cd server
```
Inside the folder you execute this command
```bash
gcloud builds submit --tag gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
```
#### deploy new build
```bash
gcloud run deploy --image gcr.io/<put the name of your Google Cloud PROJECT here>/<put the name of your Cloud Run FUNCTION here>
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
if the docker doesn't run try cleaning minikube and starting the service again
```bash
minikube delete --all
```
if the build fail try resetting the connections with gcloud, it happens sometimes at the begging of a coding session
```bash
gcloud auth application-default login
```

### What I did to get here 
Those where my notes during the process, it's a mess but maybe can help you
#### Followed the video
* I Followed the video and built the application like you see on the video https://www.youtube.com/watch?v=t5EfITuFD9w
The idea is to run @amfchef's code on this structure instead of the presenter's one. 
#### Downloaded the original code
* Cloned @amfchef bot at https://github.com/amfchef/binance-trading-bot Great job guy, the code is amazing
#### Moved the files
* Moved original files and replace the ones on my the application I built watching the video. Created the function binance-trading-robot-fire on Cloud Run
#### Created the Docker
* Created docker file like you see on the video then you add this to the RUN line:  
python-binance binance Werkzeug google-cloud google-cloud-secret-manager firebase-admin
#### Put my keys
* Edited the config files and put my keys on

 * 1st here: /server/src/serviceAccountKey.json (you find this adding an app on your Firebase console -> Project Overview -> Settings -> General)

 * 2nd here: /server/src/config.py (you find this creating a Service account on your Firebase console -> Project Overview -> Settings -> Service Account)

#### created de build
```bash
gcloud builds submit --tag gcr.io/binance-trading-robot/binance-trading-robot-fire
```
#### deployed new build
```bash
gcloud run deploy binance-trading-robot-fire --image gcr.io/binance-trading-robot/binance-trading-robot-fire
```
#### Created firebase project binance-trading-robot
* went to https://firebase.google.com/ and create a new project to host the role thing
#### init firebase hosting
```bash
firebase init hosting
```

## Contributing

1. Fork it (<https://github.com/danielvm-git/binance-trading-robot/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## Version History

* 0.0.1
    * Initial work

## License

This project is licensed under the MIT License - see the LICENSE.md file for details 
 
## Authors

[@amfchef](https://github.com/amfchef) - Original code
 
[@danielvm-git](https://github.com/danielvm-git) - Contributor

## Acknowledgments
Thanks a lot for all the good job that [@amfchef](https://github.com/amfchef) made on the original code that I used here and also for all the [Discord](https://discord.com/invite/u2FcPxy) group folks for their support

<!-- Markdown link & img dfn's -->

[version-image]: https://img.shields.io/badge/Version-0.0.2-brightgreen?style=for-the-badge&logo=appveyor
[version-url]: https://img.shields.io/badge/version-0.0.2-green
[Frontend-image]: https://img.shields.io/badge/Frontend-Bootstrap-blue?style=for-the-badge
[Frontend-url]: https://img.shields.io/badge/Frontend-Bootstrap-blue?style=for-the-badge
[Backend-image]: https://img.shields.io/badge/Backend-Python-important?style=for-the-badge
[Backend-url]: https://img.shields.io/badge/Backend-Python-important?style=for-the-badge

