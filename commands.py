#commands.py

import logging
from discord.ext import commands
from utils import Utils
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import discord
import pytz
import os


class Commands(commands.Cog):
    def __init__(self, bot, user_data_manager, scheduler):
        self.bot = bot
        self.user_data_manager = user_data_manager
        self.scheduler = scheduler

    def register(self):
        self.bot.add_command(self.addprogress)
        self.bot.add_command(self.viewprogress)
        self.bot.add_command(self.reminder)
        self.bot.add_command(self.removereminder)
        self.bot.add_command(self.logworkout)
        self.bot.add_command(self.logmeal)
        self.bot.add_command(self.fitnessplan)
        self.bot.add_command(self.myplan)

    @commands.command()
    async def addprogress(self, ctx, category: str, value: float):
        try:
            if not isinstance(value, (int, float)):
                await ctx.send("Invalid value. Please enter a number.")
                return
            user_progress = self.user_data_manager.get_user_progress(ctx.author.id)
            if category not in user_progress:
                user_progress[category] = []
            user_progress[category].append({'date': datetime.datetime.now().strftime('%Y-%m-%d'), 'value': value})
            self.user_data_manager.set_user_progress(ctx.author.id, user_progress)
            await ctx.send(f"{category} progress added successfully!")
        except Exception as e:
            await ctx.send("An error occurred while adding progress.")
            logging.error(f"Error while adding progress: {e}")

    @commands.command()
    async def viewprogress(self, ctx, category: str, plot_type: str='line'):
        try:
            user_progress = self.user_data_manager.get_user_progress(ctx.author.id)
            if category not in user_progress:
                await ctx.send(f"No progress data found for {category}")
                return
            dates = [entry['date'] for entry in user_progress[category]]
            values = [entry['value'] for entry in user_progress[category]]

            if plot_type == 'line':
                plt.plot(dates, values)
            elif plot_type == 'bar':
                plt.bar(dates, values)
            elif plot_type == 'scatter':
                plt.scatter(dates, values)
            elif plot_type == 'histogram':
                sns.distplot(values, hist=True, kde=False, bins=30)
            else:
                await ctx.send("Invalid plot type. Please enter 'line', 'bar', 'scatter', or 'histogram'.")
                return

            plt.title(f"{category.capitalize()} Progress")
            plt.xlabel("Date")
            plt.ylabel(category.capitalize())

            # Generate a unique filename for each graph using user ID and timestamp
            filename = f"progress_{ctx.author.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            plt.savefig(filename)
            plt.clf()

            # Send the graph as a Discord file attachment
            with open(filename, 'rb') as f:
                await ctx.send(file=discord.File(f))

            # Remove the temporary file
            os.remove(filename)
        except Exception as e:
            await ctx.send("An error occurred while generating the graph.")
            logging.error(f"Error while generating the graph: {e}")

    @commands.command()
    async def reminder(self, ctx, days: str, time: str, method: str, tz: str = "UTC"):
        # Implementation for reminder command
        # Check if provided timezone is valid
        if tz not in pytz.all_timezones:
            await ctx.send("Invalid timezone provided.")
            return
        # Check if provided days are valid
        valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        days_list = days.lower().split(',')
        if not all(day in valid_days for day in days_list):
            await ctx.send("Invalid day provided. Please provide days in this format: mon,tue,wed,thu,fri,sat,sun.")
            return
        # Check if provided methods are valid
        valid_methods = ['dm', 'email', 'sms']
        methods_list = method.lower().split(',')
        if not all(m in valid_methods for m in methods_list):
            await ctx.send("Invalid method provided. Available methods: dm, email, sms.")
            return

        # Add user to reminder list
        user_data = self.user_data_manager.get_user_data(ctx.author.id)
        if not user_data:
            user_data = {}
        user_data['reminder'] = {
            'days': days_list,
            'time': time,
            'method': methods_list,
            'timezone': tz
        }
        self.user_data_manager.set_user_data(ctx.author.id, user_data)

        # If user already has a reminder, remove it
        if 'reminder_job' in user_data:
            self.scheduler.remove_job(user_data['reminder_job'])

        # Register a reminder job
        job = self.scheduler.add_job(self.send_reminder, 'cron', day_of_week=days, hour=int(time.split(':')[0]), minute=int(time.split(':')[1]), args=[ctx.author.id, methods_list], timezone=pytz.timezone(tz))
        user_data['reminder_job'] = job.id
        self.user_data_manager.set_user_data(ctx.author.id, user_data)
        await ctx.send("Your reminder has been set!")

    @commands.command()
    async def removereminder(self, ctx):
        # Implementation for removereminder command
        user_data = self.user_data_manager.get_user_data(ctx.author.id)
        if user_data and 'reminder_job' in user_data:
            self.scheduler.remove_job(user_data['reminder_job'])
            del user_data['reminder_job']
            self.user_data_manager.set_user_data(ctx.author.id, user_data)
            await ctx.send("Your reminder has been removed.")
        else:
            await ctx.send("You don't have any active reminder.")
    
    @commands.command()
    async def logworkout(self, ctx, workout_type: str):
        # Implementation for logworkout command
        workout_type = workout_type.lower()

        if workout_type not in ['weightlifting', 'running', 'swimming', 'cycling', 'yoga', 'pilates', 'cardio', 'hiit']:
            await ctx.send("Invalid workout type. Please enter a valid workout type (weightlifting, running, swimming, cycling, yoga, pilates, cardio, hiit).")
            return

        await ctx.send(f"You logged a {workout_type} workout. What was the duration of your workout in minutes?")
        duration = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))

        try:
            duration = int(duration_msg.content)
            if duration <= 0:
                await ctx.send("Invalid duration. Please enter a positive number.")
            return
        except ValueError:
            await ctx.send("Invalid duration. Please enter a number.")
            return

        workout_info = {}

    # Handle specific workout types
        if workout_type == 'weightlifting':
            await ctx.send("What exercises did you perform and how much weight did you lift for each?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'running':
            await ctx.send("What was the type of running (track, trail, treadmill) and distance covered?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'swimming':
            await ctx.send("What was the type of swimming (freestyle, backstroke, butterfly, breaststroke) and distance covered?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'cycling':
            await ctx.send("What was the distance covered and type of cycling (road, mountain, stationary)?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'yoga':
            await ctx.send("What type of yoga (hatha, vinyasa, ashtanga, etc.) did you perform?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'pilates':
            await ctx.send("What were the Pilates exercises you performed?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'cardio':
            await ctx.send("What type of cardio exercises did you do?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))
        elif workout_type == 'hiit':
            await ctx.send("What were the HIIT exercises you performed and their intervals?")
            workout_info = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))

        user_logs = self.user_data_manager.get_user_logs(ctx.author.id)
        user_logs['workouts'].append({
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'workout_type': workout_type,
            'duration': int(duration.content)
        })
        self.user_data_manager.set_user_logs(ctx.author.id, user_logs)
        
        await ctx.send("Workout logged successfully!")

    @commands.command()
    async def logmeal(self, ctx, meal_type: str):
        # Implementation for logmeal command
        meal_type = meal_type.lower()

        if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
            await ctx.send("Invalid meal type. Please enter a valid meal type (breakfast, lunch, dinner, snack).")
            return

        await ctx.send(f"You logged a {meal_type}. What did you eat? Please reply with food items separated by commas.")
        foods = await self.bot.wait_for('message', check=Utils.check_author_and_channel(ctx.author, ctx.channel))

        # Here you should call the appropriate service to fetch nutritional information
        # For each food item, fetch nutritional info and aggregate it
        total_calories = fetch_nutritional_info(foods.content.split(', '))

        user_logs = self.user_data_manager.get_user_logs(ctx.author.id)
        user_logs['meals'].append({
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'meal_type': meal_type,
            'foods': foods.content.split(', '),
            'calories': total_calories
        })
        self.user_data_manager.set_user_logs(ctx.author.id, user_logs)
        await ctx.send("Meal logged successfully!")
    

    @commands.command(help="Generate a new fitness plan.")
    async def fitnessplan(self, ctx):
        # Implementation for fitnessplan command
        user_data = self.user_data_manager.get_user_data(ctx.author.id)
        if user_data and 'fitness_plan' in user_data:
            await ctx.send("You already have a fitness plan. Type '!myplan' to see your current plan.")
        else:
            # Here you can add the logic for generating a new fitness plan
            new_plan = "This is your new fitness plan. (Replace this text with actual logic for plan creation)"
            await ctx.send(new_plan)

    @commands.command(help="See your current fitness plan.")
    async def myplan(self, ctx):
        # Implementation for myplan command
        user_data = self.user_data_manager.get_user_data(ctx.author.id)
        if user_data and 'fitness_plan' in user_data:
            await ctx.send(f"Your current fitness plan is: {user_data['fitness_plan']}")
        else:
            await ctx.send("You don't have a fitness plan yet. Type '!fitnessplan' to create a new one.")

    @commands.Cog.listener()
    async def fitnessplan_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("An error occurred while executing the command. Please try again.")
            logging.error(f"Command Error: {ctx.command} - {error}")
