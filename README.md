# one-piece-group-bot

[![LOC](https://sloc.xyz/github/nickelza/one-piece-group-bot/?category=code)](https://github.com/nickelza/one-piece-group-bot/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/nickelza/one-piece-group-bot/blob/master/LICENSE)
[![Project Status](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

## Official Links

- [Telegram Bot](https://t.me/onepiecegroupbot)
- [Support Group](https://t.me/bountysystem)

## Quick Links

> - [Overview](#overview)
> - [Features](#features)
> - [Getting Started](#getting-started)
    >

- [Installation](#installation)

> - [Running one-piece-group-bot](#running-one-piece-group-bot)
>   - [Dashboard](#dashboard)
> - [Project Roadmap](#project-roadmap)
> - [Contributing](#contributing)
> - [License](#license)

---

## Overview

Bring a One-Piece Bounty System to your Telegram Group


---

## Features

- Bounty for each user
- Bounty Poster
- Leaderboard
- Crews
- Devil Fruits

[Non-Exhaustive List of Features](https://telegra.ph/One-Piece-Group---Bounty-System-10-26)

## Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **Python**: `3.11 or higher`
* **MySQL**: `8.0 or higher`

- Create a Telegram Bot using the [BotFather](https://core.telegram.org/bots#6-botfather) and
  obtain the bot token
- Create a Telegram Group in which the Bot will be used

### Installation

1. Clone the one-piece-group-bot repository:

```sh
git clone https://github.com/Nickelza/one-piece-group-bot
```

2. Change to the project directory:

```sh
cd one-piece-group-bot
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

4. Create a `.env` file under the project root folder and set the required environment variables as
   described in the `environment/env.example` file.

- `BOT_TOKEN` - Telegram Bot Token obtained from BotFather
- `BOT_ID` - Created Bot ID
- `BOT_USERNAME` - Created Bot Username
- `DB_NAME` - MySQL Database Name
- `DB_HOST` - MySQL Database Host
- `DB_PORT` - MySQL Database Port
- `DB_USER` - MySQL Database User
- `DB_PASSWORD` - MySQL Database Password

- `UPDATES_CHAT_ID` - Telegram Chat ID for Updates, used for global leaderboard

For a full list of environment variables and their descriptions, refer to
the `resources/Environment.py` file.

### Running one-piece-group-bot

Use the following command to run one-piece-group-bot:

```sh
python main.py [optional path to .env file]
```

### Dashboard

Some features, such as Devil Fruit or Warlord management, require setting up the dashboard.
To do so, follow the instructions in
the [dashboard repository](https://github.com/Nickelza/one-piece-group-bot-dashboard).

---

## Project Roadmap

- [GitHub Project](https://github.com/users/Nickelza/projects/1)

---

## Contributing

Contributions are welcome! Here are several ways you can contribute:

-
    *
*[Submit Pull Requests](https://github.com/Nickelza/one-piece-group-bot/blob/main/CONTRIBUTING.md)
**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://t.me/bountysystem)**: Share your insights, provide feedback, or
  ask questions.
- **[Report Issues](https://github.com/Nickelza/one-piece-group-bot/issues)**: Submit bugs found or
  log feature requests for One-piece-group-bot.

---

## License

This project is protected under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

[**Return**](#quick-links)

---
