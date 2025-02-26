from storages.backends.azure_storage import AzureStorage
import os

class AzureMediaStorage(AzureStorage):
    account_name = os.environ.get('AZURE_ACCOUNT_NAME', 'questcontent')
    azure_container = os.environ.get('AZURE_CONTAINER', 'questplusict')
    connection_string = os.environ.get('AZURE_CONNECTION_STRING', 'DefaultEndpointsProtocol=https;AccountName=questcontent;AccountKey=Pz9jVbmzLexr14V4IA0ZDtQqtjwVPixxBB6CxpLM/yOVgRng9oJOhxLYUn30Kc88JG8eWfIB6m+PJbVRD5YXhg==;EndpointSuffix=core.windows.net')
    # Set the default folder within the container
    location = 'coderz'