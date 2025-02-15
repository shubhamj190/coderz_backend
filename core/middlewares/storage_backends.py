from storages.backends.azure_storage import AzureStorage
import os

class AzureMediaStorage(AzureStorage):
    account_name = os.environ.get('AZURE_ACCOUNT_NAME', 'youraccountname')
    azure_container = os.environ.get('AZURE_CONTAINER', 'yourcontainer')
    connection_string = os.environ.get('AZURE_CONNECTION_STRING', 'your_connection_string')
    # Set the default folder within the container
    location = 'coderz'