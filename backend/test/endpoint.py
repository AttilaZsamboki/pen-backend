import certifi
import requests

# Set the CA certificate bundle path
ca_cert_bundle = certifi.where()
requests.get('https://pen.dataupload.xyz/order_webhook', verify=False)
