from flask import Flask, render_template, request
from utills.gpt import generate_chat_completion
from utills.score import get_game_prompt
from datetime import date
import json

app = Flask(__name__, static_folder='static')

all_narratives = []
all_dates = []
all_teams = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        today = date.today()
        messages = [
            {"role": "system", "content": f"""
        You are an AI designed to input user text input and return a dictionary of two pairs.
        Today's date is {today}.
        The first pair's key is date and the value is a date in the format of YYY-MMM-DD 
        with the YYYY as a four digit integer representation of the year, the MMM as the three digit 
        capitalized character representation of the month and DD as the two digit integer 
        representation of the date. The second pair's key is team and the value is in the format of 
        XXX with XXX as the three digit capitalized character representation of a Major League Baseball team
        abbreviation. If a date or a team cannot be found in the user text input, use the default
        values of 2023-MAY-13 for the team and the default values LAD for the team. A sample
        output returned should look like date: 2023-MAY-13, team: LAD in a dictionary.
        """},
            {"role": "user", "content": user_input}
        ]
        response = generate_chat_completion(messages)
        response_data = json.loads(response)
        response_date = response_data["date"]
        response_team = response_data["team"]
        score = get_game_prompt(response_date, response_team)

        if score:
            narrative = generate_chat_completion(score["data"])
            all_narratives.append(narrative)
        else:
            narrative = "The game you requested does not exist. Please try again."
            all_narratives.append(narrative)

        all_dates.append(response_date)
        all_teams.append(response_team)
        return render_template('index.html', dates=all_dates, teams=all_teams, narratives=all_narratives)
    return render_template('index.html', dates=all_dates, teams=all_teams, narratives=all_narratives)


# Run the Flask app
if __name__ == '__main__':
    app.run()
