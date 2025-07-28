from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import re

import os
TOKEN = os.environ["TOKEN"]
# Emotion metadata
emotions = {
    "friend": {
        "emoji": "👯‍♂️",
        "lines": [
            "“Some friendships feel like group projects — one tries, the other just shows up.”",
            "“It’s always ‘I got you’ — until you fall.”"
        ]
    },
    "love": {
        "emoji": "❤️",
        "lines": [
            "“Sometimes love doesn’t fade — it just hides where they stopped looking.”",
            "“It felt full… until I realized I was loving alone.”"
        ]
    },
    "hate": {
        "emoji": "💢",
        "lines": [
            "“Hate is just attention in a cheaper outfit.”",
            "“You never hated me — you just couldn't control me.”"
        ]
    },
    "crush": {
        "emoji": "💘",
        "lines": [
            "“It’s funny how one smile can ruin your entire emotional stability.”",
            "“You were never mine, just an overplayed thought in a lonely playlist.”"
        ]
    },
    "obsession": {
        "emoji": "🌀",
        "lines": [
            "“You call it obsession — I call it remembering too much.”",
            "“I watched your silence louder than your words.”"
        ]
    },
    "doubt": {
        "emoji": "🤨",
        "lines": [
            "“Doubt always enters quietly, then lives rent-free.”",
            "“Even the clearest truths crack under whispered suspicions.”"
        ]
    },
    "anger": {
        "emoji": "😤",
        "lines": [
            "“Anger isn’t loud — sometimes it’s just silence with clenched fists.”",
            "“It’s not rage — it’s the echo of every ignored feeling.”"
        ]
    },
    "sympathy": {
        "emoji": "🫠",
        "lines": [
            "“Your sympathy feels like a compliment dipped in pity.”",
            "“Keep your concern — I’ve survived better enemies.”"
        ]
    },
    "interest": {
        "emoji": "👀",
        "lines": [
            "“Funny how fast interest dies when honesty walks in.”",
            "“They noticed you just enough to keep you confused.”"
        ]
    },
    "jealousy": {
        "emoji": "🫥",
        "lines": [
            "“It’s not envy — it’s just watching someone live what you only imagined.”",
            "“They want your life, just not your scars.”"
        ]
    }
}

def calculate_percentage(input_string, is_one_sided, first_name):
    """
    Calculate percentage based on the specified trick, splitting sums >=10 into digits.
    Input: String like "/friend Rahul and Varun" or "/love Arun for Priya"
    is_one_sided: True if command uses 'for', False if 'and'
    first_name: First name in the command for marker in one-sided emotions
    Output: Percentage as an integer between 1 and 100
    """
    # For one-sided emotions, append a marker based on the first name
    if is_one_sided:
        input_string += f"#{first_name.lower()}"
    
    # Remove spaces for 'and' commands, keep spaces for 'for' commands
    if not is_one_sided:
        input_string = input_string.replace(" ", "")
    
    # Convert string to lowercase and count each character
    char_count = {}
    for char in input_string.lower():
        char_count[char] = char_count.get(char, 0) + 1
    
    # Get counts as a list of digits
    digits = [char_count.get(char, 0) for char in input_string.lower()]
    
    while len(digits) > 2:
        new_digits = []
        # Pair first with last, second with second last, etc.
        for i in range((len(digits) + 1) // 2):
            if i < len(digits) - 1 - i:
                # Add first and last digits
                sum_value = digits[i] + digits[-(i + 1)]
                # Split sum into digits if >= 10 (e.g., 14 -> [1, 4])
                if sum_value >= 10:
                    new_digits.extend([int(d) for d in str(sum_value)])
                else:
                    new_digits.append(sum_value)
            else:
                # If odd number of digits, append middle digit as is
                new_digits.append(digits[i])
        digits = new_digits
    
    # Handle the final steps as per the example
    if len(digits) == 3:
        new_digits = []
        # Sum first and last, keep middle as is
        sum_value = digits[0] + digits[2]
        if sum_value >= 10:
            new_digits.extend([int(d) for d in str(sum_value)])
        else:
            new_digits.append(sum_value)
        new_digits.append(digits[1])
        digits = new_digits
    
    if len(digits) == 3:
        # Sum first two, keep last as is
        sum_value = digits[0] + digits[1]
        if sum_value >= 10:
            digits = [int(d) for d in str(sum_value)] + [digits[2]]
        else:
            digits = [sum_value, digits[2]]
    
    # Combine the final two digits to get percentage
    if len(digits) == 2:
        percentage = int(f"{digits[0]}{digits[1]}")
    elif len(digits) == 1:
        percentage = digits[0] * 11  # Handle single digit case (e.g., 5 -> 55%)
    else:
        percentage = 0  # Fallback for edge cases
    
    # Ensure percentage is between 1–100%
    percentage = max(1, min(100, percentage))
    return percentage

def parse_names(text):
    """
    Parse input text to extract two names and the mode ('and' or 'for').
    Returns: (name1, name2, mode)
    """
    match_and = re.search(r'(\w+)\s+and\s+(\w+)', text, re.IGNORECASE)
    match_for = re.search(r'(\w+)\s+for\s+(\w+)', text, re.IGNORECASE)
    if match_and:
        return match_and.group(1), match_and.group(2), "and"
    elif match_for:
        return match_for.group(1), match_for.group(2), "for"
    else:
        return None, None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Welcome to Closeness Calculator Bot!*\n\n"
        "This bot is designed to calculate the value of a specific emotion or feelings between two people based on different types of emotions like friendship, love, hate, jealousy, etc.\n\n"
        "🔹 *How to use this bot?*\n"
        "Use any command followed by two names to check their combined emotional percentage.\n\n"
        "*Example:*\n`/friend Rahul and Varun`\nChecks the friendship level between Rahul and Varun.\n\n"
        "🔸 *One-sided emotions:*\nUse `for` instead of `and`\n\n"
        "*Example:*\n`/hate Riya for Ankit`\nChecks how much Riya might hate Ankit.\n\n"
        "📜 *Commands List:*\n"
        "/friend\n/love\n/hate\n/crush\n/obsession\n/doubt\n/anger\n/sympathy\n/interest\n/jealousy\n/InfoBot\n\n"
        "💡 Replace *'and'* with *'for'* to check one-sided emotion.\n\n"
        "❗️If you're facing any issue or want a new command to be added, feel free to message the bot owner.\nUsername is mentioned in bot's bio."
    )
    await update.message.reply_markdown(text)

async def emotion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.split()[0][1:].lower()  # Extract command without '/'
    args = " ".join(context.args)
    name1, name2, mode = parse_names(args)

    if not name1 or not name2:
        await update.message.reply_text(
            f"Gawar hai kiya? Naam to daal aage jahil..\nYe dekh ese karte hai 👇🏻\n"
            f"/{command} Rahul and Farhan"
        )
        return

    emoji = emotions[command]["emoji"]
    quote = random.choice(emotions[command]["lines"])

    # Calculate percentage, passing is_one_sided and first_name
    is_one_sided = (mode == "for")
    percentage = calculate_percentage(update.message.text, is_one_sided, name1)

    # One-sided reply
    if mode == "for":
        await update.message.reply_text(f"Calculating {name1}'s {command} for {name2}...")
        await update.message.reply_text("Done ✅")
        reply = f"{emoji} {command.title()} Value: *{percentage}%*\n_{quote}_"
    else:
        await update.message.reply_text(f"Calculating the {command} value between {name1} and {name2}...")
        await update.message.reply_text("Done ✅")
        reply = f"{emoji} {name1} & {name2} — *{percentage}%* {command.title()}\n_{quote}_"

    await update.message.reply_markdown(reply)

async def info_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*🤖 Closeness Calculator Bot*\n\n"
        "This bot calculates totally real, absolutely scientific closeness between people! 😂\n"
        "Just type something like `/love Alice and Bob` or `/hate Tom for Jerry`.\n\n"
        "It throws in a random percentage, adds a pinch of drama, and serves it with emojis. 🎭\n"
        "_Don't take it seriously — it's pure fun and sarcasm._\n\n"
        "*Supported Commands:* /friend, /love, /hate, /crush, /obsession, /doubt, /anger, /sympathy, /interest, /jealousy\n"
        "*Creator:* A human with too much free time 😎"
    )
    await update.message.reply_markdown(text)

async def luck_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 100)
    await update.message.reply_text(f"🎲 Your secret luck number is: *{num}*", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Main emotion commands
    for emotion in emotions.keys():
        app.add_handler(CommandHandler(emotion, emotion_handler))

    # Extra commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("infoBot", info_bot))
    app.add_handler(CommandHandler("luck", luck_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
