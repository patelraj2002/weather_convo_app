import requests
import json
from groq import Groq
import streamlit as st
from datetime import datetime
GROQ_API_KEY = "Enter Your Api"
def is_weather_related(query, GROQ_API_KEY):
    messages = [
        {
            "role": "system",
            "content": "You are a weather specialist. Your task is to determine if a given query is related to weather. Respond with 'Yes' if the query is weather-related, and 'No' if it's not. Only respond with 'Yes' or 'No'."
        },
        {
            "role": "user",
            "content": f"Is this query weather-related? Query: {query}"
        }
    ]
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="gemma-7b-it",
        messages=messages,
        temperature=0.5
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == 'yes'

def get_city(query, GROQ_API_KEY):
    messages = [
        {
            "role": "system",
            "content": f"Find city name from query: {query}, answer should be in one word."
        },
        {
            "role": "user",
            "content": query
        }
    ]

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="gemma-7b-it",
        messages=messages,
        temperature=0.5
    )

    city = response.choices[0].message.content.strip()
    return city

def get_weather(city):
    api_key = "b3c62ae7f7ad5fc3cb0a7b56cb7cbda6"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['cod'] != 200:
            return None, f"Error: {data['message']}"
    except requests.exceptions.HTTPError as err:
        return None, f"Error: {err}"
    except json.JSONDecodeError as err:
        return None, f"Error: Failed to parse response JSON - {err}"

    return data, None

def process_weather_data(data):
    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']

    # Convert temperature from Kelvin to Celsius
    temperature = round(temperature - 273.15, 2)

    return {
        "description": weather_description,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }

def handle_query(query, data, GROQ_API_KEY):
    messages = [
        {
            "role": "system",
            "content": "Act as a weather chatbot that responds to user queries about weather. "
                       "Your primary function is to provide accurate information on current conditions, forecasts, and meteorological phenomena. "
                       "Follow these guidelines: Focus solely on weather-related topics, Provide details on current conditions, forecasts, severe weather alerts, and general meteorological information."
                       "Ask for the user's location if not provided. Clarify time frames for forecasts. "
                       "Offer temperatures in Celsius and Fahrenheit, wind speeds in km/h and mph. "
                       "Emphasize severe weather warnings. "
                       "Briefly explain weather phenomena when relevant."
                       "Mention data comes from reliable sources if asked. "
                       "State limitations if unable to provide certain information. "
                       "Remind users to check for updates on rapidly changing conditions. "
                       "Maintain a helpful, friendly tone."
        },
        {
            "role": "user",
            "content": query + str(data)
        }
    ]

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="gemma-7b-it",
        messages=messages,
        temperature=0.5
    )

    return response.choices[0].message.content

def determine_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

# Streamlit UI
st.header("Check the current weather or ask a weather-related question")

query = st.text_input("Ask a weather-related question")

if st.button("Response"):
    if query:
        if is_weather_related(query, GROQ_API_KEY):
            city = get_city(query, GROQ_API_KEY)
            if city and city.lower() != "none":
                weather_data, error = get_weather(city)
                if weather_data:
                    processed_data = process_weather_data(weather_data)
                    st.write(f"Weather in {city}: {processed_data['description']}")
                    st.write(f"Temperature: {processed_data['temperature']}°C")
                    st.write(f"Humidity: {processed_data['humidity']}%")
                    st.write(f"Pressure: {processed_data['pressure']} hPa")

                    answer = handle_query(query, processed_data, GROQ_API_KEY)
                    st.write(answer)
                else:
                    st.write(error)
            else:
                st.write("I couldn't identify a city in your query. Could you please rephrase your question and include a city name?")
        else:
            st.write("I'm a weather specialist. Could you please ask me something about the weather instead? I'd be happy to help with any weather-related questions.")
    else:
        st.write("You can ask a question related to the weather in the provided input box.")