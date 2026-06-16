import os
import json
import requests
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

# Load secret keys
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API")
WEATHER_API_KEY = os.getenv("WEATHER_API")

# --- MAIN FUNCTION ---
def generate_briefing():
    topic = topic_entry.get()
    city = city_entry.get()
    
    if not topic or not city:
        messagebox.showwarning("Oops!", "Please enter both a topic and a city.")
        return

    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, "Fetching data, please wait...\n\n")
    root.update() # Force the window to show the loading text

    save_data = {}
    display_text = ""

   
    joke_res = requests.get("https://official-joke-api.appspot.com/random_joke")
    if joke_res.status_code == 200:
        joke_data = joke_res.json()
        joke = f"{joke_data['setup']} ... {joke_data['punchline']}"
        display_text += f"😂 JOKE OF THE DAY:\n{joke}\n\n"
        save_data["joke"] = joke

    
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    weather_res = requests.get(weather_url)
    
    if weather_res.status_code == 200:
        w_data = weather_res.json()
        condition = w_data["weather"][0]["description"]
        temp = w_data["main"]["temp"]
        display_text += f"🌤️ WEATHER IN {city.upper()}:\nCondition: {condition.title()}\nTemp: {temp}°C\n\n"
        save_data["weather"] = {"condition": condition, "temp": temp}
    else:
        messagebox.showerror("Weather Error", "Could not find that city or API key is invalid.")
        display_text += "🌤️ WEATHER: Error fetching weather data.\n\n"

    
    news_url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWS_API_KEY}&pageSize=5&language=en"
    news_res = requests.get(news_url)
    
    save_data["news"] = []
    
    if news_res.status_code == 200:
        articles = news_res.json().get("articles", [])
        if len(articles) == 0:
            display_text += f"📰 NEWS: No articles found for '{topic}'.\n"
        else:
            display_text += f"📰 TOP 5 '{topic.upper()}' NEWS:\n"
            for i, article in enumerate(articles, start=1):
                title = article.get("title", "No Title")
                url = article.get("url", "No Link")
                
                display_text += f"{i}. {title}\n   Link: {url}\n\n"
                save_data["news"].append({"title": title, "url": url})
    else:
        messagebox.showerror("News Error", "News request failed. Check your API key.")
        display_text += "📰 NEWS: Error fetching news data.\n"


    with open("saved_briefing.json", "w") as file:
        json.dump(save_data, file, indent=4)
    display_text += "📁 (Briefing saved to saved_briefing.json)"

    # Show the final text on the screen
    result_box.delete("1.0", tk.END)
    result_box.insert(tk.END, display_text)



root = tk.Tk()
root.title("My Daily Briefing")
root.geometry("500x600")

tk.Label(root, text="Enter a News Topic:").pack(pady=5)
topic_entry = tk.Entry(root, width=30)
topic_entry.pack()

tk.Label(root, text="Enter your City:").pack(pady=5)
city_entry = tk.Entry(root, width=30)
city_entry.pack()

fetch_btn = tk.Button(root, text="Get My Briefing", command=generate_briefing)
fetch_btn.pack(pady=15)

result_box = tk.Text(root, height=25, width=55)
result_box.pack(pady=5)

root.mainloop()