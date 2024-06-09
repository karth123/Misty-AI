from configparser import ConfigParser

def read_openai_config():
    config = ConfigParser()
    config.read('config.dev.cfg')
    return config['openai']

def read_google_gemini_config():
    config = ConfigParser()
    config.read('config.dev.cfg')
    return config['google']

# def upload_file_to_firebase(file_name, ext) -> str: # File needs to be in same directory as this config file
#     cred = credentials.Certificate("YOUR DOWNLOADED CREDENTIALS FILE (JSON)")
#     initialize_app(cred, {'storageBucket': 'YOUR FIREBASE STORAGE PATH (without gs://)'}) 
#     bucket = storage.bucket()
#     blob = bucket.blob(f"{file_name}.{ext}")
#     blob.upload_from_filename(f"{file_name}.{ext}")
#     return blob._get_download_url
