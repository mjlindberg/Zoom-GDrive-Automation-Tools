from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import requests
from tqdm import tqdm


def start_gdrive():
    creds, _ = google.auth.default()
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
    except HttpError as error:
        print(F'An error occurred: {error}')
    else:
        return service


def create_dirs(
    gdrive_dir_id,
    service=None,
    #dir_name=input('Parent dir name (e.g. Week): '),
    #subdir_name=input('Child dir name (e.g. Day): ')
):
    try:
        ########################
        ### create directory ###
        ########################
        file_metadata = {
            'name': dir_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [gdrive_dir_id]
        }
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        dir_id = file.get("id")
        print(F'Folder {dir_name} has been created with ID: "{dir_id}".')
        # subdir
        file_metadata = {
            'name': subdir_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [file.get("id")]
        }
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        subdir_id = file.get("id")
        print(F'Folder {subdir_name} has been created with ID: "{subdir_id}".')
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    else:
        return (dir_id, subdir_id)


def create_dir(
    gdrive_dir_id,
    service=None,
    dir_name=None,
):
    while not dir_name:
        dir_name = input(f"Directory name to create: >> ")
        if not dir_name and not input("Skip? (Hit enter to skip.) "):
            return gdrive_dir_id
    try:
        ########################
        ### create directory ###
        ########################

        file_metadata = {
            'name': dir_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [gdrive_dir_id]
            }
        file = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        dir_id = file.get("id")
        print(F'Folder {dir_name} has been created with ID: "{dir_id}".')
        if input("Create additional folders? (Hit Enter to skip.) >> "):
            dir_id = create_dir(dir_id, service)
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    else:
        return dir_id


def upload(
    rec_name,
    rec_filepath,
    mimetype,
    gdrive_dir_id,
    zoom_jwt,
    service
):
    """Upload file with conversion
    Returns: ID of the file uploaded

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    #creds, _ = google.auth.default()

    try:
        ########################
        ##### upload file ######
        ########################
        file_metadata = {
            'name': rec_name,
            'parents': [gdrive_dir_id]
        }
        headers = {'Authorization': "Bearer %s" % zoom_jwt,
                   'content-type': "application/json"}
        print("Preparing file...")
        resp = requests.get(rec_filepath, headers=headers)
        filestream = BytesIO(resp.content)
        media = MediaIoBaseUpload(filestream,  # MediaFileUpload
                                  mimetype=mimetype,
                                  resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id')
        response = None
        with tqdm(total=100) as pbar:
          while not response:
            status, response = file.next_chunk()
            if status:
              pbar.update(int(status.progress() * 100))
          if file:
            pbar.close()
            print(F'File with ID: "{response.get("id")}" has been uploaded.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return response.get('id')


def upload_zoom(
    rec_name,
    rec_filepath,
    mimetype,
    gdrive_dir_id,
    zoom_jwt
):
    gdrive = start_gdrive()
    _, new_dir = create_dir(gdrive)
    upload(rec_name,
           rec_filepath,
           mimetype,
           zoom_jwt=zoom_jwt,
           service=gdrive,
           gdrive_dir_id=new_dir)
