# Plex IMDb/TMDb/TVDB NFO Creator

A Python script to generate NFO files for movies and TV shows from Plex metadata.  
It extracts IMDb, TMDb, and TVDB IDs and creates NFO files with appropriate links, enabling Jellyfin to identify media just as Plex does.  
This tool is ideal for users who want to preserve their Plex library data quality when switching to Jellyfin.

## Features

- Connects to a Plex server.
- Retrieves movies or TV shows from a specified library.
- Extracts IMDb, TMDb, and TVDB IDs.
- Creates .nfo files with links to corresponding media pages.
- Maps Plex file paths to local filesystem paths with drive-letter mapping support on Windows.

## Prerequisites

- Python 3.6 or later
- Plex Media Server
- PlexAPI
- tqdm

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
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
python plex_nfo_creator.py --token YOUR_PLEX_TOKEN [options]
```

### Options

- `--url`: Plex server URL (default: http://localhost:32400)
- `--token`: Plex authentication token (required)
- `--library`: Plex library name (default: Movies)
- `--type`: Library type: `movie` or `tv` (default: movie)
- `--root-path`: Local root path corresponding to your Plex media (required for proper path mapping)
- `--dry-run`: Simulate operations without writing files

## Example

For processing a movie library:

```bash
python plex_nfo_creator.py --token my_plex_token --library "Movies" --type movie --root-path "D:\Media\Movies"
```

For processing a TV show library:

```bash
python plex_nfo_creator.py --token my_plex_token --library "TV Shows" --type tv --root-path "D:\Media\TV Shows"
```

## Logging

Logs are written to `plex_nfo_creator.log` in the project directory.

## Troubleshooting

- Verify your Plex token and server URL.
- Ensure the library name, type, and root-path are correct.
- Check `plex_nfo_creator.log` for any error messages.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Feel free to submit issues or pull requests to help improve this project.
