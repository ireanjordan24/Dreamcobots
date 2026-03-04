# Feature 3: Occupational bot for interview preparation.
# Functionality: Provides commonly asked interview questions and tips.
# Use Cases: Candidates preparing for upcoming interviews.

class InterviewPreparationBot:
    def __init__(self):
        pass

    def start(self):
        print("Interview Preparation Bot is starting...")

    def provide_questions(self):
        print("Providing commonly asked interview questions...")

    def offer_tips(self):
        print("Offering tips and strategies for successful interviews...")

    def run(self):
        self.start()
        self.provide_questions()
        self.offer_tips()

# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = InterviewPreparationBot()
    bot.run()