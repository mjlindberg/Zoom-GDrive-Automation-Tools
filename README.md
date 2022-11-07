# Zoom-GDrive-Automation-Tools
Automated handling of Zoom meeting recording files, using Google Drive as the object store.

## Usage

1. Create a Zoom app (**JWT**) on the [Zoom Marketplace](https://marketplace.zoom.us) with access permissions to Zoom recordings on the Zoom account in question. Save the API key and API secret as `api_key` and `api_secret` in a dedicated text/YAML file. Add its path to the config file in the directory.

2. Set up your Google Cloud credentials on your machine (using the "application default credentials" strategy).

3. Edit the `config_example.yaml` file and add your Zoom account ID (e-mail address).

4. Also add the ID of the directory in your Google Drive where you wish to store the recordings.

5. Rename `config_example.yaml` to `config.yaml`.

6. Run `zoom_gdrive_auto.py` and follow the on-screen instructions.

That's it!

![Usage example](https://github.com/mjlindberg/Zoom-GDrive-Automation-Tools/blob/main/zoom_gdrive.gif?raw=true)
