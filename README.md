# 420VaultBot
🌿 420VaultBot

Advanced Discord Search & Indexing Bot

420VaultBot is a high-performance Discord utility bot built to index, search, and intelligently route large libraries of external links (plugins, presets, kits, tools, resources, etc.) without flooding channels or hosting files.

Designed for scale, precision, and automation.

🚀 What Is 420VaultBot?

420VaultBot acts like a search engine inside Discord.

Instead of dumping thousands of links into channels, it:

indexes link lists

intelligently parses URLs

ranks results by relevance

returns clean, searchable results on demand

No files are hosted.
No content is downloaded.
Only external HTTPS links are indexed.

✨ Features

🔎 Advanced multi-keyword search

🧠 URL path cleaning & keyword normalization

🖥️ Platform-aware filtering (Windows / macOS / installers)

📊 Confidence-based result ranking

🎯 Randomized sampling to prevent spam

📦 Supports multiple large link files

🧵 Embed pagination (no message flooding)

🔐 Admin-only maintenance commands

📡 Channel-aware result dispatching

⚡ Runs locally, via WSL, or on a server

❌ What 420VaultBot Does NOT Do

420VaultBot does not:

host files

upload content

download resources

bypass DRM

modify third-party software

All indexed links are user-provided.
Server owners are responsible for their own content sources.

🛠️ Requirements
System

Python 3.10+

Internet connection

Discord account with developer access

Python Dependencies

discord.py

Standard Python libraries (asyncio, os, re, random, etc.)

📦 Installation
1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/420VaultBot.git
cd 420VaultBot

2️⃣ Create a Virtual Environment (Recommended)
Windows
python -m venv venv
venv\Scripts\activate

Linux / macOS / WSL
python3 -m venv venv
source venv/bin/activate

3️⃣ Install Dependencies
pip install -U discord.py

🤖 Discord Bot Setup
1️⃣ Create the Bot

Visit https://discord.com/developers/applications

Click New Application

Go to Bot → Add Bot

Copy the Bot Token

⚠️ Never share your bot token publicly

2️⃣ Enable Required Intents

In the Discord Developer Portal, enable:

✅ Message Content Intent

✅ Server Members Intent

✅ Presence Intent (optional)

⚙️ Configuration

All configuration is located at the top of the main bot file.

🔑 Bot Token (Environment Variable Recommended)
Windows (PowerShell)
setx DISCORD_420VAULT_TOKEN "YOUR_BOT_TOKEN"

Linux / macOS / WSL
export DISCORD_420VAULT_TOKEN="YOUR_BOT_TOKEN"


The bot will automatically prefer the environment variable over hardcoded values.

🧵 Command Prefix
PREFIX = "#"


Example usage:

#searchkit omnisphere win installer

📂 Link Files
LINKS_FILES = [
    "lists.txt",
    "lists_part_2.txt",
    "lists_part_3.txt"
]


Each file:

One URL per line

No categories required

Supports tens of thousands of links

Duplicate links are automatically removed

📡 Target Channels
TARGET_CHANNEL_NAMES = [
    "zenology-bank",
    "omnisphere-bank",
    "🥁-drumkits-sounds"
]


Channels are resolved on startup.
420VaultBot will only post where it has permission.

▶️ Running 420VaultBot
python bot.py


Expected output:

420VaultBot is online.
Loaded XXXX unique links.
Target channels resolved successfully.

🧠 How the Search Engine Works

Links are loaded into memory from text files

URL paths are cleaned and normalized

Keywords are matched against:

raw URL paths

cleaned semantic paths

Platform terms (win, mac, installer) use explicit detection

Results are ranked by confidence

A clean, randomized subset is displayed

This prevents:

spam

repetitive results

channel flooding

📜 Command Reference
🔎 #searchkit

Searches indexed links using advanced logic.

Examples

#searchkit omnisphere win installer
#searchkit serum preset bank
#searchkit scope:plugin vital mac
#searchkit drumkit trap loops


Supports:

multiple keywords

platform filtering

result ranking

embed pagination

📤 #sendlink

Searches and sends one random match to a target channel.

#sendlink omnisphere zenology-bank

🔄 #reloadlinks (Admin)

Reloads all link files without restarting the bot.

📡 #resolvelinks (Admin)

Re-resolves configured target channels.

📋 #showchannels

Displays all configured channels and their status.

📊 #status

Shows:

number of loaded links

resolved channels

command prefix

🔐 Permissions

Minimum required permissions:

Read Messages

Send Messages

Embed Links

Read Message History

Admin commands require elevated permissions.

🧪 Development Notes

No database required

No cloud dependencies

Designed for local or VPS hosting

Easily forkable and extendable

Modular functions for reuse in other bots

🧭 Roadmap Ideas

Live link scraping

Database-backed indexing

Per-server datasets

Web dashboard

API access

Plugin-based modules

⚠️ Disclaimer

420VaultBot is provided as-is for educational and organizational purposes.
The developer does not host, distribute, or control third-party content indexed by this bot.

🧠 Author

420VaultBot was built from scratch, with original logic, architecture, and systems design.
