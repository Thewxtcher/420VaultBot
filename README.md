# 420VaultBot
420VaultBot 🌿🔍

A smart Discord bot for searching, filtering, and delivering plugin & kit links on demand

420VaultBot is a custom Discord search bot designed to handle huge, messy link vaults (5,000+ links) and return clean, relevant results based on user keywords — without spamming channels.

Instead of dumping links endlessly, the bot works like a search bar for your server.

✨ Features

🔎 Keyword-based searching (multiple keywords supported)

📂 Reads from large link lists (lists.txt, lists_part_2.txt, etc.)

🎯 Randomized results to avoid repeats

🧠 Smart filtering (plugin names, platforms, installers, keywords)

📦 Clean embeds (no spam walls)

⚙️ Fully customizable & self-hosted

🛠 Built for VS Code + WSL (easy setup)

🧾 Requirements

You only need:

Windows 10 or 11

Visual Studio Code

Discord Bot Token

WSL (Windows Subsystem for Linux)

No Docker. No paid services. No nonsense.

🚀 Installation (Simple Method)
1️⃣ Download the Bot

Download or clone this repository from GitHub

Extract the folder somewhere easy (Desktop is fine)

2️⃣ Install VS Code

Download and install VS Code:
👉 https://code.visualstudio.com/

During install, check these boxes:

✅ Add to PATH

✅ Open with Code

🐧 Installing WSL (Beginner-Friendly, Step by Step)

What is WSL?
WSL (Windows Subsystem for Linux) lets you run Linux inside Windows without dual-booting or virtual machines.

420VaultBot runs best in a Linux environment — WSL gives you that with almost no effort.

You do not need prior Linux knowledge.
Open PowerShell as Administrator, then run:

wsl --install


Restart your PC when it finishes.

Ubuntu will be installed automatically.

4️⃣ Open the Bot in VS Code (WSL Mode)

Open VS Code

Press Ctrl + Shift + P

Type:

WSL: Open Folder


Select the 420VaultBot folder

You are now running inside Linux (WSL).

⚙️ Configuration
1️⃣ Install Python Dependencies

Open the VS Code terminal (Ctrl + `) and run:

sudo apt update
sudo apt install python3 python3-pip -y
pip3 install -r requirements.txt

2️⃣ Add Your Discord Bot Token

Open the main bot file (example: bot.py)
Find:

BOT_TOKEN = "YOUR_TOKEN_HERE"


Replace it with your real token from:
👉 https://discord.com/developers/applications

⚠️ Never upload your real token to GitHub

3️⃣ Link Files Setup

Make sure your files exist in the bot folder:

lists.txt
lists_part_2.txt
lists_part_3.txt


You can add or remove list files — the bot auto-loads them.

▶️ Running the Bot

In the VS Code terminal:

python3 bot.py


If you see:

Bot is online


You’re live 🚀

💬 Example Commands
#searchkit omnisphere win installer
#searchkit kontakt drum kit
#searchkit serum preset pack


The bot will:

Search all lists

Filter junk

Send a clean result to the correct channel

🧠 How It Works (High Level)

Loads thousands of links into memory

Normalizes URLs for better matching

Scores results based on keyword relevance

Randomizes output to prevent repeats

Limits results to avoid spam

This makes it fast, quiet, and scalable.

🔐 Security Notes

Do NOT commit your bot token

Keep private vault links private

This bot is intended for controlled servers only

🛠 Customization

You can easily:

Change command names

Add platform filters (Win / Mac)

Add per-channel restrictions

Expand to paid/custom client bots

This project is designed to be extended.

📜 License

This project is for educational and private server use.
DO NOT SELL OR REDISTROBUT UNDER ANYT CIRCUMSTANCES PERSONAL USE ONLY AUTHOR IS NOT RESPONSIBLE FOR ACTIONS TAKEN AGAINST ACCOUNTS 
