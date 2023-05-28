#reminders.py

import pytz
import commands

class Reminders(commands.Cog):
    def __init__(self, bot, user_data_manager, scheduler):
        self.bot = bot
        self.user_data_manager = user_data_manager
        self.scheduler = scheduler

    async def register(self, guild):
        # Register the reminder commands
        await guild.add_command(self.reminder)
        await guild.add_command(self.removereminder)

    async def send_reminder(self, user_id, methods):
        user_data = self.user_data_manager.get_user_data(user_id)
        if 'reminder' in user_data:
            for method in methods:
                if method == 'dm':
                    user = self.bot.get_user(user_id)
                    if user:
                        await user.send('This is your scheduled reminder!')
                elif method == 'email':
                    send_email(user_data['email'], 'This is your scheduled reminder!')
                elif method == 'sms':
                    send_sms(user_data['phone'], 'This is your scheduled reminder!')

    @commands.command()
    async def reminder(self, ctx, days: str, time: str, method: str, tz: str = "UTC"):
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
        user_data = self.user_data_manager.get_user_data(ctx.author.id)
        if user_data and 'reminder_job' in user_data:
            self.scheduler.remove_job(user_data['reminder_job'])
            del user_data['reminder_job']
            self.user_data_manager.set_user_data(ctx.author.id, user_data)
            await ctx.send("Your reminder has been removed.")
        else:
            await ctx.send("You don't have any active reminder.")


