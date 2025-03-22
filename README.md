# Plex IMDb/TMDb/TVDB NFO Creator

A Python script to generate NFO files for movies and TV shows from Plex metadata.  
It extracts IMDb, TMDb, and TVDB IDs and creates NFO files with appropriate links, enabling Jellyfin to identify media just as Plex does.  
This tool is ideal for users who want to preserve their Plex library data quality when switching to Jellyfin.

This accomplishes the following mentioned in the Jellyfin Docs: [Jellyfin local NFO](https://jellyfin.org/docs/general/server/metadata/nfo/)

```You can also use your .nfo files to help Jellyfin identify your media. You can just enter an IMDb, TMDb or TVDb link, to link the media to the specific provider id.```

> **⚠️ Warning:** This program is to be used at your own risk.  
> Before using your real movies folder, please test on an overlay file storage (or similar safe environment) as advised by your preferred AI.  
> The author is not liable for any data loss.

## Features

- Connects to a Plex server.
- Retrieves movies or TV shows from a specified library.
- Extracts IMDb, TMDb, and TVDB IDs.
- Creates .nfo files with links to corresponding media pages beneath the Movie Files or at the TV Show root folder.
- Maps Plex file paths to local filesystem paths with drive-letter mapping support on Windows.

## Prerequisites

- Python 3.13
- Plex Media Server
- PlexAPI (dependency)
- tqdm (dependency)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/b1ggi/plex-nfo-creator
   cd plex-nfo-creator
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with your Plex token and necessary options:

```bash
python plex_nfo_creator.py --token YOUR_PLEX_TOKEN --root-path YOUR_LIBRARY_FOLDER [options]
```

### Options

- `--url`: Plex server URL  (needs full url `http(s)://<ip:port>` or `<url>`, default: `http://localhost:32400`)
- `--token`: Plex authentication token (required)
- `--library`: Plex library name (default: Movies)
- `--type`: Library type: `movie` or `tv` (default: movie)
- `--root-path`: Local root path corresponding to the regarding library, e.g. Y:\Movies or /data/movies (required for proper path mapping)
- `--dry-run`: Simulate operations without writing .nfo files

## Example

For processing a movie library:

```bash
python plex_nfo_creator.py --url https://plex.xyz.com --token my_plex_token --library "Movies" --type movie --root-path "/data/movies"
```

For processing a TV show library:

```bash
python plex_nfo_creator.py --url http://192.168.0.1:32400 --token my_plex_token --library "TV Shows" --type tv --root-path "D:\Media\TV Shows"
```

## Logging

Logs are written to `plex_nfo_creator.log` in the project directory.

## Screenshot

![image](https://github.com/user-attachments/assets/2f40fa36-e6f5-4bd0-afb0-460b492d2bb4)


## Troubleshooting

- Verify your Plex token and server URL.
- Ensure the library name, type, and root-path are correct.
- Check `plex_nfo_creator.log` for any error messages.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Feel free to submit issues or pull requests to help improve this project.
