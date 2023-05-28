import discord
from discord.ext import commands
import json
import os
from logic import UserDataManager

# Create instance of bot
bot = commands.Bot(command_prefix="!")

data_file = 'user_data.json'

user_data_manager = UserDataManager(data_file)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def fitnessplan(ctx):
    await ctx.send("Let's create a custom fitness plan for you!")

    questions = [
        "What are your fitness goals? (e.g., weight loss, muscle gain, improved cardiovascular health)",
        "What is your current fitness level and exercise experience?",
        "Do you have any existing medical conditions or injuries that may affect your ability to exercise?",
        "Are you currently taking any medications that may impact your exercise or require modifications to your fitness plan?",
        "What is your preferred exercise environment? (e.g., gym, outdoors, home)",
        "How many days per week can you commit to exercise?",
        "How much time can you dedicate to each exercise session?",
        "Do you have any specific preferences or interests when it comes to types of exercises or activities? (e.g., running, swimming, weightlifting, yoga)",
        "Are there any exercises or activities you dislike or have physical limitations for?",
        "Are there any dietary considerations or restrictions that need to be taken into account?",
        "What is your current lifestyle and daily activity level? (e.g., sedentary, moderately active, highly active)",
        "Are there any specific barriers or challenges you anticipate that may affect your ability to follow an exercise plan? (e.g., time constraints, travel)",
        "Do you have access to any exercise equipment or facilities?",
        "Would you prefer to work out alone or with a partner or trainer?",
        "Are you open to trying new exercises or incorporating different types of workouts into your routine?",
    ]

    user_info = {}

    for question in questions:
        await ctx.send(question)
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        user_info[question] = msg.content

    # Create the central prompt using user's answers and fitness trainer role
    prompt = """
    Act as a professional fitness trainer. As an expert in fitness, your goal is to provide users with the best fitness-related information and guidance. You should answer user questions, offer workout tips, suggest exercises, and provide advice on nutrition and overall well-being. Be polite, encouraging, and supportive in your responses. Help users set realistic goals, develop effective workout routines, and maintain a healthy lifestyle. Remember to personalize your advice based on individual needs and considerations. Provide accurate information and promote safe and sustainable fitness practices. Use your expertise to inspire and motivate users on their fitness journey.
    
    Fitness Goals: {}
    Fitness Level: {}
    """.format(user_info["What are your fitness goals? (e.g., weight loss, muscle gain, improved cardiovascular health)"], user_info["What is your current fitness level and exercise experience?"])

    user_data_manager.set_user_data(str(ctx.author.id), user_info)

    # Create the central prompt using user's answers
    prompt = "\n".join(user_info.values())

    # Send the prompt to the ChatGPT API and receive the response
    response = generate_chatgpt_response(prompt)

    # Send the response to the user in a readable and Discord-friendly format
    await ctx.send(f"Your fitness plan:\n{response}")

def generate_chatgpt_response(prompt):
    # Make a request to the ChatGPT API with the prompt
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': 'Bearer YOUR_API_KEY',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'text-davinci-003',
            'messages': [{'role': 'system', 'content': 'Y'}, {'role': 'user', 'content': prompt}]
        }
    )

    # Retrieve the response from the API
    if response.status_code == 200:
        data = response.json()
        choices = data['choices']
        if choices and 'text' in choices[0]:
            return choices[0]['text'].strip()
    return "Failed to generate a fitness plan."
    await ctx.send("Your fitness plan has been created!")

@bot.command()
async def myplan(ctx):
    user_info = user_data_manager.get_user_data(str(ctx.author.id))
    if user_info:
        await ctx.send(f"Your fitness plan: {user_info}")
    else:
        await ctx.send("You don't have a fitness plan yet. Use !fitnessplan to create one.")

# Use your own bot's token here
bot.run("your-bot-token")

