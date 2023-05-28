#utils.py

import discord
from discord import Embed

class Utils:
    @staticmethod
    def get_questions():
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
            "Are you open to trying new exercises or incorporating different types of workouts into your routine?"
        ]
        return questions

    @staticmethod
    def create_user_session(user_id):
        # Creates an empty dictionary for each user session to be filled as the user responds to the bot's questions
        user_session = {'user_id': user_id}
        return user_session

    @staticmethod
    def create_prompt(user_session):
        # Initial prompt for the ChatGPT
        initial_prompt = "Act as a professional fitness trainer. As an expert in fitness, your goal is to provide users with the best fitness-related information and guidance. You should answer user questions, offer workout tips, suggest exercises, and provide advice on nutrition and overall well-being. Be polite, encouraging, and supportive in your responses. Help users set realistic goals, develop effective workout routines, and maintain a healthy lifestyle. Remember to personalize your advice based on individual needs and considerations. Provide accurate information and promote safe and sustainable fitness practices. Use your expertise to inspire and motivate users on their fitness journey."
        for question, answer in user_session.items():
            initial_prompt += f"\n\n{question}: {answer}"
        return initial_prompt

    @staticmethod
    def create_embed(content):
        return Embed(description=content)

    @staticmethod
    def check_author_and_channel(author, channel):
        def check(m):
            return m.author == author and m.channel == channel
        return check