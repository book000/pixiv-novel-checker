# pixiv-novel-checker

Search for novels on [Pixiv](https://pixiv.net/) and notify Discord of new novels.

## Requirements

- Valid [Pixiv](https://pixiv.net/) account
- Python 3.6+
- [requirements.txt](requirements.txt): `requests`, `pixivpy3`

## Installation

1. Clone from GitHub repository: `git clone https://github.com/book000/pixiv-novel-checker.git`
2. Install the dependency package from `requirements.txt`: `pip3 install -U -r requirements.txt`

## Configuration

- Rewrite `config.sample.json` and rename to `config.json`.
  - `username`: Pixiv username
  - `password`: Pixiv password
  - `discord_token`: Discord Bot token
  - `discord_channel`: Discord Send to channel ID
- Rewrite `searchwords.sample.json` and rename to `searchwords.json`.
  - `words`: List of words to search on Pixiv (tag search)
  - `words`: List of words to search on Pixiv (text search)
  - `mutetags`: List of tags to exclude if they are included in the search results

## Usage

```shell
cd /path/to/
python3 main.py
```

The `config.json` file in the current directory will be read, so change to the root directory of the project in advance before executing.

## Warning / Disclaimer

The developer is not responsible for any problems caused by the user using this project.

## License

The license for this project is [MIT License](LICENSE).
