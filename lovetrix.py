import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

FILENAME = "chamtx2.txt" #you have to give your chat.txt file name here bro i will suggest to rename the cht with something one word type shit 

def parse_chat(filename):
    with open(filename, encoding="utf-8") as file:
        raw = file.read()

    # meri chat month/day/year mee thi to usi type i am hoping aap sbki bhi export hogi 
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*)'
    messages = re.findall(pattern, raw)

    chat_data = []

    for date_str, time_str, sender, message in messages:
        timestamp_str = f"{date_str}, {time_str}"
        # month/day/year
        try:
            time_obj = datetime.strptime(timestamp_str, "%m/%d/%y, %H:%M")
        except ValueError:
            try:
                time_obj = datetime.strptime(timestamp_str, "%m/%d/%Y, %H:%M")
            except ValueError:
                continue

        chat_data.append({
            "time": time_obj,
            "sender": sender.strip(),
            "message": message.strip()
        })

    return pd.DataFrame(chat_data)

def compute_reply_times(df):
    df = df.sort_values(by="time").reset_index(drop=True)
    participants = df['sender'].unique()
    if len(participants) != 2:
        raise ValueError(f"Chat must be between exactly two participants, found: {participants}")

    user1, user2 = participants[0], participants[1]

    replies = []

    for i in range(len(df) - 1):
        current = df.iloc[i]
        next_msg = df.iloc[i + 1]

        # If current is user1 and next is user2
        if current['sender'] == user1 and next_msg['sender'] == user2:
            delay = (next_msg['time'] - current['time']).total_seconds() / 60
            replies.append({
                "date": current['time'].date(),
                "from": user1,
                "reply_time": delay
            })
        elif current['sender'] == user2 and next_msg['sender'] == user1:
            delay = (next_msg['time'] - current['time']).total_seconds() / 60
            replies.append({
                "date": current['time'].date(),
                "from": user2,
                "reply_time": delay
            })
    return pd.DataFrame(replies)

def plot_interest_graph(reply_df):
    if reply_df.empty:
        print("No reply patterns found.")
        return

    daily_avg = reply_df.groupby(['date', 'from'])['reply_time'].mean().reset_index()

    plt.figure(figsize=(12, 6))
    for sender in daily_avg['from'].unique():
        data = daily_avg[daily_avg['from'] == sender]
        plt.plot(data['date'], data['reply_time'], marker='o', label=sender)

    plt.title("Daily Average Reply Time (lower = higher interest)")
    plt.xlabel("Date")
    plt.ylabel("Average Reply Time (minutes)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = parse_chat(FILENAME)
    if df.empty:
        print("No messages parsed. Please check your file again.")
    else:
        reply_df = compute_reply_times(df)
        plot_interest_graph(reply_df)
