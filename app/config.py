from google.cloud import secretmanager

# * ###########################################################################
# * Secret Manager Configuration
# Create the Secret Manager client.
secret_manager_client = secretmanager.SecretManagerServiceClient()
# GCP project in which to store secrets in Secret Manager.
project_id = "binance-trading-robot"
# ID of the secret to get.
api_key_id = "exchange_api_key_binance_margin"
api_secret_id = "exchange_api_secret_binance_margin"
app_password_id = "trade_password_binance_margin"
# String of the request to get.
api_key_request = {"name": f"projects/101254323285/secrets/exchange_api_key_binance_margin/versions/latest"}
api_secret_request = {"name": f"projects/101254323285/secrets/exchange_api_secret_binance_margin/versions/latest"}
password_request = {"name": f"projects/101254323285/secrets/trade_password_binance_margin/versions/latest"}
# Getting the response from Secret Manager.
api_key_response = secret_manager_client.access_secret_version(api_key_request)
api_secret_response = secret_manager_client.access_secret_version(api_secret_request)
password_response = secret_manager_client.access_secret_version(password_request)

# * ###########################################################################
# * Class ConfigClient
class ConfigClient:
    # Deconding the secrets.
    API_KEY = api_key_response.payload.data.decode("UTF-8")
    API_SECRET = api_secret_response.payload.data.decode("UTF-8")
    PASSWORD = password_response.payload.data.decode("UTF-8")