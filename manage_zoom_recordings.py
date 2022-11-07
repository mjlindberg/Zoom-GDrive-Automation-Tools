import requests
import http.client
import yaml
import time
import datetime as dt
import jwt
import json

def read_zoom_cred(filepath,
		exp = dt.datetime.now() + dt.timedelta(minutes=90)
		):
	creds = yaml.load(open(filepath), Loader = yaml.SafeLoader)
	if not creds.get('jwt_token'):
		payload = {'iss':creds['api_key'], 'exp':exp}
		creds['jwt_token'] = jwt.encode(payload, creds['api_secret'])
	return creds

def get_zoom_token(
		client_id = "",
		redirect_uri = ""
		):
	url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={client_id}" #+ "&redirect_uri={redirect_uri}"
	return requests.get(url)

def get_zoom_jwt(
		api_key = None,
		api_secret = None,
		exp = dt.datetime.now() + dt.timedelta(minutes=90),
		):
	payload = {'iss':api_key, 'exp':exp}
	return jwt.encode(payload, api_secret)


def get_zoom_recordings(
                api_key = None,
                api_secret = None,
                jwt_token = None,
                exp = None,
                user_id = None,
                from_date = None
                ):
        jwt_encoded = jwt_token if jwt_token else get_zoom_jwt(api_key, api_secret, exp)
        headers = {'Authorization': "Bearer %s" % jwt_encoded,
                        'content-type': "application/json"}

        from_date = from_date if from_date else (dt.datetime.now() - dt.timedelta(days=30)).strftime('%Y-%m-%d')

        conn = http.client.HTTPSConnection("api.zoom.us")
        conn.request("GET",
                        f"/v2/users/{user_id}/recordings"+ f"?from={from_date}",
                        headers = headers)
        res = conn.getresponse()
        response_string = res.read().decode('utf-8')
        return json.loads(response_string)


def get_filesize_readable(size_bytes, reduc = 0):
	units = {0:'B', 1:'KB', 2:'MB', 3:'GB'}
	if len(str(size_bytes)) > 3 and reduc < 3:
		reduc += 1
		return get_filesize_readable(round(size_bytes/1024), reduc)
	return f'{size_bytes} {units[reduc]}'


def list_meetings(recordings_json):
  meetings = recordings_json.get('meetings')
  print(f"{len(meetings)} meetings found.\n")
  cols = "id\t\tdate\t\t\tsize\t\tduration"
  print(cols)
  print("".join(["_"]*(len(cols)+(6*cols.count('\t')))))
  for idx, meeting in enumerate(meetings):
    print(
      f"[{idx}]",
      meeting['start_time'].split('T')[0],
      get_filesize_readable(meeting['total_size']),
      meeting['duration'],
      sep = "\t|\t"
      )

def add_metadata(meeting_files,
		):
  date_format = "%Y-%m-%dT%H:%M:%SZ"
  time_conv = lambda x: dt.datetime.strptime(x, date_format)
  for file in meeting_files:
	  file["duration"] = time_conv(file['recording_end']) - time_conv(file['recording_start'])
	  file["file_size_human"] = get_filesize_readable(file['file_size'])
  return meeting_files

def get_meeting(recordings_json,
                min_length = dt.timedelta(minutes=30),
                choice = 0
                ):
  last_meeting_files = recordings_json['meetings'][choice]['recording_files']
  date_format = "%Y-%m-%dT%H:%M:%SZ"
  time_conv = lambda x: dt.datetime.strptime(x, date_format)
  for file in last_meeting_files:
          file["duration"] = time_conv(file['recording_end']) - time_conv(file['recording_start'])
          file_size_human = get_filesize_readable(file['file_size'])
          print(file['file_type'], file_size_human, file['duration'],
                          sep = ' - ')
  return [f for f in last_meeting_files if f['duration'] > min_length]

def describe_files(files):
  date_format = "%Y-%m-%dT%H:%M:%SZ"
  time_conv = lambda x: dt.datetime.strptime(x, date_format)
  spaces_10char = "          "
  prev_date = spaces_10char

  for file in sorted(files, key = lambda x:x['recording_start']):
    date = file['recording_start']
    date_print = date if prev_date != date else spaces_10char
    prev_date = date
    print(date_print.split('T')[0],
          file['file_type'],
          file['file_size_human'],
          str(file['duration']),
          sep = ' - ')

def get_chosen_meetings(recordings_json,
                min_length = 30,
                choice = 0,
		describe = True
                ):
  min_length = dt.timedelta(minutes=min_length)

  if isinstance(choice, list):
    meeting_files = []
    for c in choice:
      meeting_files += recordings_json['meetings'][c]['recording_files']
  else:
    meeting_files = recordings_json['meetings'][choice]['recording_files']
  meeting_files = add_metadata(meeting_files)
  keep, discard = [],[]
  for file in meeting_files:
    if file['duration'] > min_length:
      keep.append(file)
    else:
      discard.append(file)
  if describe:
    print(f'\n\033[1mFound {len(keep)} files >{min_length}.\033[0m')
    describe_files(keep)
    print(f'\n\033[3mFound {len(discard)} files that did not meet criteria.\033[0m')
    describe_files(discard)
  return keep


def get_listed_meetings(recordings_json,
		min_length = 30):
  list_meetings(recordings_json)
  while True:
    choice = input("\nWhich meetings do you want to choose? (If multiple, separate by commas.): >> ")
    if choice:
      choice = list(map(int, choice.split(',')))
      break
    else:
      if input('Do you wish to skip? Press Enter to skip. >> '):
        continue
      else:
        choice = 0
        print("Choosing latest meeting...")
        break
  return get_chosen_meetings(recordings_json, min_length, choice)
