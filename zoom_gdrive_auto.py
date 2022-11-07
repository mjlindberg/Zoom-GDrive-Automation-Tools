import manage_zoom_recordings as zoom
import upload_gdrive as gdrive
import yaml

with open("config.yaml") as f:
    config = yaml.load(f, Loader = yaml.FullLoader)

user = config['user_id']
cred = zoom.read_zoom_cred(config['zoom_cred'])
gdrive_dir = config['gdrive_dir']

mimetypes = {
		"shared_screen_with_speaker_view":'video/mp4',
		"chat_file":'text/plain'
		}

recordings = zoom.get_zoom_recordings(
		**cred,
		user_id = user
		)

files = zoom.get_listed_meetings(recordings, 16)
#print(f"{len(files)} files meeting criteria found.")
print('_'*30, '\n')
print("Creating folders in Google Drive...")
gdrive_inst = gdrive.start_gdrive()
new_dir = gdrive.create_dir(gdrive_dir, gdrive_inst)
print('_'*30, '\n')

for file in files:
	#z.download_file(file[])
	print(
			file['recording_type'],
			file['download_url'],
			file["duration"],
			file["recording_end"],
			sep = "\t")
	name = input("File name: ")
	if name:
		gdrive.upload(
			name,
			file['download_url'],
			mimetypes[file['recording_type']],
			new_dir,
			cred['jwt_token'],
			gdrive_inst
			)
	else:
		print("Skipping...")
	print('_'*30, '\n')

print("\nDone!")
