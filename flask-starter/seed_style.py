import os
import sys
from db import memory

def seed():
    thread = memory.create_thread(user_id="casius")
    style_rule = (
        "STYLE RULE: write my daily briefing in my voice. Five top stories. For each story provide exactly three sections: "
        "1. What happened, 2. Why it matters, and 3. Your angle (my content, talk, and demo opportunities as an AI Developer Advocate at Oracle). "
        "Link stories to earlier ones when they are follow-ups. British English. No em dashes. "
        "Give a one-line top-line summary of where the day is trending at the very top."
    )
    thread.add_memory(style_rule)
    print("Successfully seeded Developer Advocate STYLE RULE.")

if __name__ == "__main__":
    seed()
