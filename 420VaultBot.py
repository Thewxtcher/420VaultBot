import discord
from discord.ext import commands
import asyncio
import random
import os
import re
from urllib.parse import urlparse # For cleaning up URLs for better search

# --- CONFIGURATION SECTION: Adjust these values to control your Intelligent Retriever! ---
# This section allows you to customize the bot's behavior and target channels.

# COMMAND PREFIX: The character your bot will listen for (e.g., "!", "#", ">").
PREFIX = "#" 

# BOT TOKEN: Your bot's secret key. Obtain this from the Discord Developer Portal.
# IMPORTANT: DO NOT hardcode your token directly in publicly shared code for security.
# It's highly recommended to set this as an environment variable (e.g., DISCORD_RETRIEVER_TOKEN).
# For initial testing, you can replace 'YOUR_BOT_TOKEN_HERE' with your actual token.
BOT_TOKEN = "YOUR_BOT_TOKEN"
# LINKS FILES: A LIST of text file names containing your harvested links.
# Each file should contain one link per line, without category headers.
# The bot will combine links from all these files.
LINKS_FILES = [
    "lists.txt",
    "lists_part_2.txt",
    "lists_part_3.txt"
]

# TARGET CHANNEL NAMES: A list of Discord Channel NAMES (strings) that the bot will pre-resolve.
# When you use the '!sendlink' command, you will refer to these names.
# The bot will attempt to find channels matching these names in any guild it is a part of.
# Ensure these names exactly match your Discord channel names (case-insensitive will be handled by bot).
TARGET_CHANNEL_NAMES = [ 
    "zenology-bank", 
    "serum-1-and-2-banks",
    "portal-banks", 
    "midi", 
    "gross-beat-presets", 
    "omnisphere-bank", 
    "loops", 
    "fx-sounds",
    "presets-banks",
    "🥁-drumkits-sounds", # Note: Emojis and special characters are part of the name
    "one-shots",  
    "🔓-cracked-plugins", # Note: Emojis and special characters are part of the name
    "🔓keygens"          # Note: Emojis and special characters are part of the name
]

# MAX SEARCH RESULTS TO DISPLAY: How many matching links !searchkit should show in the Discord channel.
MAX_SEARCH_RESULTS_DISPLAY = 25

# --- GLOBAL VARIABLES & BOT INITIALIZATION: Do not modify below this point! ---
# These are managed by the bot itself.

all_loaded_links = [] # This list will hold all links loaded from ALL LINKS_FILES
# This dictionary will store resolved channel objects: {'lowercase_channel_name': <discord.TextChannel object>, ...}
resolved_target_channels = {} 

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True # Required for the bot to read commands
intents.members = True # Required for resolving channel names reliably across guilds

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# --- Helper Functions ---

def load_all_links_from_files(filenames: list):
    """Loads all links from a list of specified text files into a single list."""
    links = set() # Use a set to automatically handle duplicates across all files
    total_files_processed = 0
    total_links_found_in_files = 0
    
    for filename in filenames:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                links_in_current_file = 0
                for line in f:
                    line = line.strip()
                    # Skip comments, empty lines, and category headers from harvester output
                    if line and not line.startswith('#') and not line.startswith('---'):
                        links.add(line)
                        links_in_current_file += 1
            print(f"Successfully loaded {links_in_current_file} links from '{filename}'.")
            total_files_processed += 1
            total_links_found_in_files += links_in_current_file
        except FileNotFoundError:
            print(f"WARNING: The file '{filename}' was not found. Skipping this file.")
        except Exception as e:
            print(f"ERROR: Failed to load links from '{filename}': {e}. Skipping this file.")
            
    print(f"Finished loading from {total_files_processed} files. Total unique links loaded: {len(links)}.")
    return list(links) # Convert back to list for random selection

async def resolve_target_channels():
    """
    Resolves TARGET_CHANNEL_NAMES to actual Discord Channel objects across all guilds the bot is in.
    Stores resolved objects in `resolved_target_channels` dictionary.
    """
    global resolved_target_channels
    resolved_target_channels.clear() # Clear any previous resolutions

    print("\nAttempting to resolve configured target channel names to objects...")
    
    # Iterate through all guilds the bot is a member of
    for guild in bot.guilds:
        print(f"  Searching in guild: '{guild.name}' ({guild.id})")
        for target_name in TARGET_CHANNEL_NAMES:
            # Find text channels in the current guild that match the target name (case-insensitive)
            # discord.utils.get is efficient for this.
            # Handle special characters/emojis by direct comparison as names are often exact
            channel = discord.utils.get(guild.text_channels, name=target_name) # Exact match for emoji names
            if not channel: # Fallback to lowercase comparison if exact match fails
                 channel = discord.utils.get(guild.text_channels, name=target_name.lower())

            if channel:
                if channel.permissions_for(guild.me).send_messages:
                    # Store resolved channel object using its lowercase name as key for consistent lookup
                    if target_name.lower() not in resolved_target_channels: # Avoid duplicates if channel name exists in multiple guilds
                        resolved_target_channels[target_name.lower()] = channel
                        print(f"    Resolved '{target_name}' in '{guild.name}' to {channel.mention} (ID: {channel.id})")
                else:
                    print(f"    WARNING: Bot lacks 'Send Messages' permission in '{channel.name}' ({channel.id}) in guild '{guild.name}'. Skipping.")
            # else:
            #     print(f"    Channel '{target_name}' not found in guild '{guild.name}'.") # Uncomment for more verbose debug

    if not resolved_target_channels:
        print("WARNING: No target channels were successfully resolved or bot lacks permissions in them. Check `TARGET_CHANNEL_NAMES` and bot's guild permissions.")
    else:
        print(f"Successfully resolved {len(resolved_target_channels)} unique channel names to objects.")

def get_clean_url_path(url):
    """
    Extracts a clean, lowercase path from a URL for better keyword matching.
    Removes common file extensions, kit/preset/sound terms, and replaces
    hyphens/underscores with spaces.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/').replace('-', ' ').replace('_', ' ') 
    
    # Remove common file extensions
    path = re.sub(r'\.(html|php|asp|aspx|jsp|htm|exe|zip|rar|mp3|wav|midi|dmg|pkg)$', '', path, flags=re.IGNORECASE)
    
    # Remove common kit/preset/sound terms to make other keywords stand out
    # Added "windows", "mac", "installer", "setup" to be potentially removed if they are generic.
    # However, we will also search for these terms specifically in the more advanced search function.
    path = re.sub(r'\b(free|download|kit|kits|pack|packs|preset|presets|bank|banks|vst|midi|loops|one\s*shots|drum\s*kits|sound|sounds|windows|mac|macos|installer|win|setup)\b', '', path, flags=re.IGNORECASE).strip()
    
    # Remove any duplicate spaces left by replacements
    path = re.sub(r'\s+', ' ', path).strip()
    return path.lower()

def search_links_by_keyword(search_terms: list[str]):
    """
    Searches all loaded links where ALL provided search_terms are found in their cleaned URL paths.
    Includes special, more explicit matching logic for platform/type keywords.
    Returns a list of matching links.
    """
    if not all_loaded_links or not search_terms:
        return []

    matching_links = []
    
    for link in all_loaded_links:
        # Get the full, raw path for broad matching
        raw_path_lower = urlparse(link).path.strip('/').lower()
        # Also get a cleaned path for more general keyword searches
        cleaned_path_lower = get_clean_url_path(link)
        
        all_terms_match = True
        for term in search_terms:
            term_lower = term.lower()
            term_found_in_link = False

            # --- Specific Matching Logic for Platform/Installer Keywords ---
            if term_lower == "win":
                if "windows" in raw_path_lower or ".exe" in raw_path_lower or "installer-win" in raw_path_lower or "win-installer" in raw_path_lower or "for-windows" in raw_path_lower:
                    term_found_in_link = True
            elif term_lower == "mac":
                if "mac" in raw_path_lower or "macos" in raw_path_lower or ".dmg" in raw_path_lower or ".pkg" in raw_path_lower or "installer-mac" in raw_path_lower or "for-mac" in raw_path_lower:
                    term_found_in_link = True
            elif term_lower == "installer":
                if "installer" in raw_path_lower or ".exe" in raw_path_lower or ".dmg" in raw_path_lower or ".pkg" in raw_path_lower or "setup" in raw_path_lower:
                    term_found_in_link = True
            # --- General Keyword Matching ---
            elif term_lower in cleaned_path_lower: # Use cleaned path for non-specific terms
                term_found_in_link = True
            
            if not term_found_in_link:
                all_terms_match = False
                break # If any term is not found, this link doesn't match all criteria
        
        if all_terms_match:
            matching_links.append(link)
    
    return matching_links

async def dispatch_random_match(ctx, search_query_original: str, target_channel_obj: discord.TextChannel, matching_links: list):
    """
    Internal helper: Sends a random match from the provided list of matching links
    to the specified channel object.
    """
    if not matching_links:
        await ctx.send(f"No kits found matching '{search_query_original}' in the loaded list. This should not happen if called correctly.")
        return

    random_match = random.choice(matching_links)

    try:
        await target_channel_obj.send(f"**Kit found for '{search_query_original}'**: {random_match}")
        await ctx.send(f"Dispatched link for '{search_query_original}' to {target_channel_obj.mention}.")
        print(f"Sent search result '{random_match}' to #{target_channel_obj.name} for keyword '{search_query_original}'.")
    except discord.Forbidden:
        await ctx.send(f"ERROR: I lack permissions to send messages to {target_channel_obj.mention}.")
        print(f"ERROR: No permission to send messages to channel #{target_channel_obj.name} ({target_channel_obj.id}).")
    except Exception as e:
        await ctx.send(f"ERROR: Failed to send link to {target_channel_obj.mention}: {e}")
        print(f"ERROR: Failed to send link to channel #{target_channel_obj.name} ({target_channel_obj.id}): {e}")


# --- Discord Bot Events ---

@bot.event
async def on_ready():
    """Called when the bot awakens and connects to Discord."""
    print(f"Intelligent Retriever Bot '{bot.user.name}' has arisen! Connected to Discord.")
    print(f"Bot ID: {bot.user.id}")
    # Generic admin perm for simplicity, but adjust for specific permissions if needed
    print(f"Invite URL: https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=2147483648&scope=bot%20applications.commands") 

    global all_loaded_links
    all_loaded_links = load_all_links_from_files(LINKS_FILES) # Load from MULTIPLE files
    
    await resolve_target_channels() # Resolve channels when bot is ready

    if not all_loaded_links:
        print(f"CRITICAL: No links loaded from '{LINKS_FILES}'. Search and send commands will be limited.")
    else:
        print(f"Bot is ready to search {len(all_loaded_links)} links.")

@bot.event
async def on_command_error(ctx, error):
    """Handles errors that occur when commands are invoked."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You lack the necessary permissions to perform '{ctx.command.name}'.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"A component of your command is missing. Usage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unknown commands to keep output clean
    else:
        print(f"An unexpected error occurred: {error}")
        await ctx.send(f"An unknown force briefly resisted my command: `{error}`. I shall overcome!")

# --- Discord Bot Commands ---

@bot.command(
    name="searchkit",
    help=f"Searches for kits by multiple keywords (e.g., 'omnisphere win installer') and displays up to {MAX_SEARCH_RESULTS_DISPLAY} random matches."
)
@commands.has_permissions(send_messages=True)
async def search_kit_command(ctx, *, search_query: str):
    """
    Searches the loaded links for multiple keywords and displays results
    using advanced search logic (scope, identity vs content, name precision, platform, ranking).
    """

    # --- Step 0: Check if links are loaded ---
    if not all_loaded_links:
        await ctx.send(
            "❌ **ERROR:** No links loaded. Use `!reloadlinks` after adding link files."
        )
        return

    # --- Step 1: Parse search query ---
    # Extract keywords and explicit parameters like scope, os, type, format
    primary_keywords, search_params = parse_search_query(search_query)

    if not primary_keywords and "scope" not in search_params:
        await ctx.send("⚠️ Please specify what type of kit you are looking for, e.g., `scope:plugin`")
        return

    # --- Step 2: Determine search scope ---
    scope = search_params.get("scope", None)
    if scope is None:
        # Attempt to infer scope from keywords
        inferred_scope = None
        scope_keywords = {
            "plugin": ["vst", "plugin", "au-aax"],
            "preset": ["preset", "bank"],
            "drumkit": ["drum-kit", "drumkit"],
            "loops": ["loops"],
            "midi": ["midi"],
            "installer": ["installer", ".exe", ".dmg", ".pkg"],
            "expansion": ["expansion"],
            "crack": ["crack", "patch", "keygen"],
            "tutorial": ["tutorial"],
            "tool": ["tool"]
        }
        for key, words in scope_keywords.items():
            if any(word in " ".join(primary_keywords) for word in words):
                inferred_scope = key
                break
        if inferred_scope:
            scope = inferred_scope
        else:
            await ctx.send("⚠️ Unable to determine scope. Please provide `scope:<plugin/preset/drumkit/etc>` in your query.")
            return

    # --- Step 3: Determine identity vs attachment search ---
    # CORE = main plugin, CONTENT = expansions/presets/etc
    identity_keywords = ["preset", "bank", "expansion", "pack", "addon", "soundbank", "drumkit", "loop", "crack", "patch", "keygen"]
    search_mode = "CONTENT" if any(k in primary_keywords for k in identity_keywords) or scope in ["preset", "drumkit", "loops", "midi", "expansion", "crack"] else "CORE"

    # --- Step 4: Filter links by scope and search mode ---
    filtered_links = []
    for link in all_loaded_links:
        raw_path = urlparse(link).path.lower()
        clean_path = get_clean_url_path(link)

        # 4a: Scope check
        scope_match = False
        if scope == "plugin" and any(x in raw_path for x in ["vst", "plugin", "au-aax"]):
            scope_match = True
        elif scope == "preset" and any(x in raw_path for x in ["preset", "bank"]):
            scope_match = True
        elif scope == "drumkit" and "drum-kit" in raw_path:
            scope_match = True
        elif scope == "loops" and "loops" in raw_path:
            scope_match = True
        elif scope == "midi" and "midi" in raw_path:
            scope_match = True
        elif scope == "installer" and any(x in raw_path for x in ["installer", ".exe", ".dmg", ".pkg"]):
            scope_match = True
        elif scope == "expansion" and "expansion" in raw_path:
            scope_match = True
        elif scope == "crack" and any(x in raw_path for x in ["crack", "patch", "keygen"]):
            scope_match = True
        elif scope == "tutorial" and "tutorial" in raw_path:
            scope_match = True
        elif scope == "tool" and "tool" in raw_path:
            scope_match = True

        if not scope_match:
            continue

        # 4b: Identity vs content check
        if search_mode == "CORE":
            if any(x in raw_path for x in identity_keywords):
                continue  # skip content items
        elif search_mode == "CONTENT":
            if not any(x in raw_path for x in identity_keywords):
                continue  # skip core items

        # 4c: Primary keyword match (exact/loose)
        if all(k in raw_path or k in clean_path for k in primary_keywords):
            filtered_links.append(link)

    if not filtered_links:
        await ctx.send(f"⚠️ No kits found for: `{ ' '.join(primary_keywords) }` in scope `{scope}` ({search_mode})")
        return

    # --- Step 5: Rank by confidence (optional: exact name, short path, frequency) ---
    def confidence_score(link):
        raw_path = urlparse(link).path.lower()
        clean_path = get_clean_url_path(link)
        score = 0
        # exact primary keyword match
        for k in primary_keywords:
            if k in raw_path:
                score += 5
            elif k in clean_path:
                score += 3
        # shorter paths = higher score
        score += max(0, 10 - len(raw_path.split('/')))
        # prefer core over content for CORE searches
        if search_mode == "CORE" and not any(x in raw_path for x in identity_keywords):
            score += 2
        return score

    ranked_links = sorted(filtered_links, key=confidence_score, reverse=True)

    # --- Step 6: Random sampling for display ---
    display_links = random.sample(ranked_links, min(len(ranked_links), MAX_SEARCH_RESULTS_DISPLAY))

    # ---- EMBED PAGINATION ----
    EMBED_LINK_LIMIT = 10  # Safe number per embed
    chunks = [display_links[i:i + EMBED_LINK_LIMIT] for i in range(0, len(display_links), EMBED_LINK_LIMIT)]

    for idx, chunk in enumerate(chunks, start=1):
        embed = discord.Embed(
            title="🎧 Kit Search Results",
            description=(
                f"**Query:** `{ ' '.join(primary_keywords) }`\n"
                f"**Scope:** `{scope}`\n"
                f"**Mode:** `{search_mode}`\n"
                f"**Total Matches:** `{len(ranked_links)}`\n"
                f"**Showing:** `{len(display_links)}`"
            ),
            color=discord.Color.dark_purple()
        )

        for i, link in enumerate(chunk, start=1 + (idx - 1) * EMBED_LINK_LIMIT):
            embed.add_field(
                name=f"Result #{i}",
                value=f"[Click to access kit]({link})",
                inline=False
            )

        embed.set_footer(
            text="Use more keywords to narrow results • Results are randomly sampled"
        )

        await ctx.send(embed=embed)

    if len(ranked_links) > MAX_SEARCH_RESULTS_DISPLAY:
        await ctx.send(
            f"➕ `{len(ranked_links) - MAX_SEARCH_RESULTS_DISPLAY}` more matches found.\n"
            f"Refine your search or use `!sendlink` to pull a random one."
        )

    print(
        f"[SEARCHKIT] {ctx.author} searched '{search_query}' "
        f"({len(ranked_links)} matches) in #{ctx.channel.name}"
    )


@bot.command(name="sendlink", help="Searches for a kit by keyword(s) and sends a random match to a named channel.")
@commands.has_permissions(send_messages=True) # Basic permission to send messages in the current channel for response
async def send_link_by_search_and_channel(ctx, search_query: str, target_discord_channel_name: str):
    """
    Searches the loaded links for specific keywords (e.g., 'bloodhound win')
    and sends a random matching link to the specified Discord channel by name.
    Example: #sendlink bloodhound zenology-banks
    """
    search_terms = search_query.split() # Split the query into individual terms
    await ctx.send(f"Searching for kits matching '{' '.join(search_terms)}' to send to channel '{target_discord_channel_name}'...")

    final_target_channel_obj = resolved_target_channels.get(target_discord_channel_name.lower())

    if not final_target_channel_obj:
        await ctx.send(f"ERROR: Channel '{target_discord_channel_name}' not found or I lack permissions for it. Please use `!showchannels` to see available resolved channels.")
        return
    
    if not final_target_channel_obj.permissions_for(final_target_channel_obj.guild.me).send_messages:
        await ctx.send(f"ERROR: I lack permissions to send messages in the specified channel {final_target_channel_obj.mention}.")
        return

    # Perform the search
    matching_links = search_links_by_keyword(search_terms)

    if not matching_links:
        await ctx.send(f"No kits found matching '{' '.join(search_terms)}' in the loaded list. Try different keywords!")
        return

    # Dispatch a random match from the found links
    await dispatch_random_match(ctx, search_query, final_target_channel_obj, matching_links) # Use original search_query for message


@bot.command(name="reloadlinks", help="Reloads all links from the configured LINKS_FILES.")
@commands.has_permissions(administrator=True) # Only administrators can reload critical data
async def reload_links_command(ctx):
    """Reloads all links from the configured LINKS_FILES."""
    global all_loaded_links
    all_loaded_links = load_all_links_from_files(LINKS_FILES) # Load from MULTIPLE files
    if all_loaded_links:
        await ctx.send(f"Successfully reloaded {len(all_loaded_links)} links from {len(LINKS_FILES)} files.")
    else:
        await ctx.send(f"WARNING: No links loaded after reload from the configured LINKS_FILES.")

@bot.command(name="resolvelinks", help="Re-resolves configured target channel names to objects.")
@commands.has_permissions(administrator=True)
async def resolve_channels_cmd(ctx):
    """Re-resolves the target channel names to objects."""
    await ctx.send("Re-resolving configured target channel names to objects now...")
    await resolve_target_channels()
    if resolved_target_channels:
        resolved_mentions = [c.mention for c in resolved_target_channels.values()]
        await ctx.send(f"Successfully resolved {len(resolved_target_channels)} channels: {', '.join(resolved_mentions)}")
    else:
        await ctx.send("No channels could be resolved. Check `TARGET_CHANNEL_NAMES` and bot's permissions.")

@bot.command(name="showchannels", help="Shows configured Discord channel names and their resolved status.")
@commands.has_permissions(manage_channels=True)
async def show_configured_channels(ctx):
    """Displays the list of configured target channel names and their resolved status."""
    if not TARGET_CHANNEL_NAMES:
        await ctx.send("No target channel names are currently configured in `TARGET_CHANNEL_NAMES` list.")
        return

    response_lines = ["**Configured Target Discord Channels:**"]
    if not resolved_target_channels:
        response_lines.append("  (No channels currently resolved - use `!resolvelinks` or check bot's permissions and guild presence.)")
    
    for name in sorted(TARGET_CHANNEL_NAMES): # Sort for consistent display
        channel_obj = resolved_target_channels.get(name.lower())
        if channel_obj:
            response_lines.append(f"  - `{name}` (Resolved to: {channel_obj.mention} - ID: `{channel_obj.id}`)")
        else:
            response_lines.append(f"  - `{name}` (Not yet resolved or bot lacks access)")
    
    await ctx.send("\n".join(response_lines))


@bot.command(name="status", help="Displays the bot's current operational status.")
async def bot_status(ctx):
    """Displays current status and number of loaded links."""
    status_msg = f"Intelligent Retriever Bot is online!\n" \
                 f"Loaded links: {len(all_loaded_links)}\n" \
                 f"Resolved target channels: {len(resolved_target_channels)}\n" \
                 f"Prefix: `{PREFIX}`"
    await ctx.send(status_msg)

# --- Bot Execution ---

def run_bot():
    """Starts the bot's connection to Discord."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or BOT_TOKEN is None:
        print("ERROR: BOT_TOKEN is not set. Please update the 'CONFIGURATION SECTION' or set the 'DISCORD_RETRIEVER_TOKEN' environment variable.")
        print("Your bot cannot awaken without its divine key!")
        return
    try:
        # Use provided hardcoded token for convenience, but recommend environment variable for security.
        final_bot_token = os.getenv("DISCORD_RETRIEVER_TOKEN", BOT_TOKEN) # Prioritize env variable, then hardcoded
        if final_bot_token == "YOUR_BOT_TOKEN_HERE": # If still placeholder
            print("ERROR: BOT_TOKEN is still set to 'YOUR_BOT_TOKEN_HERE'. Please update it in the CONFIGURATION SECTION or set the environment variable.")
            return

        # Check if the token is the user's previously provided token and warn
        if final_bot_token == "Your_Bot_Token":
             print("WARNING: Using the hardcoded BOT_TOKEN you previously provided. For production, strongly consider using an environment variable for security.")
        
        bot.run(final_bot_token)
    except discord.LoginFailure:
        print("ERROR: Invalid BOT_TOKEN provided. Ensure your BOT_TOKEN is correct and valid in the CONFIGURATION SECTION.")
    except Exception as e:
        print(f"ERROR: Bot encountered an unexpected error during Discord connection: {e}")

if __name__ == "__main__":
    run_bot()
