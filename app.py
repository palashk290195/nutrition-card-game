from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import pandas as pd
import random

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
app.secret_key = 'your_secret_key'  # Replace with a unique secret key

# Load card data
cards_df = pd.read_csv('data.csv')
cards = cards_df.to_dict(orient='records')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_players = int(request.form.get('num_players'))
        session['num_players'] = num_players
        shuffled_cards = random.sample(cards, len(cards))
        session['players'], session['extra_deck'] = distribute_cards(shuffled_cards, num_players)
        session['current_cards'] = {f'Player {i+1}': None for i in range(num_players)}
        session['scores'] = {f'Player {i+1}': 0 for i in range(num_players)}  # Initialize scores
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        if 'reveal' in request.form:
            player = request.form['reveal']
            if session['players'][player]:
                revealed_card = session['players'][player].pop(0)
                session['current_cards'][player] = revealed_card  # Store revealed card
        elif 'winner' in request.form:
            winner = request.form.get('winner')
            if winner:
                session['scores'][winner] += 1  # Increment score for the winner
                session['current_cards'] = {player: None for player in session['players']}  # Reset for next round
    return render_template('game.html', players=session.get('players', {}), current_cards=session.get('current_cards', {}), scores=session.get('scores', {}))

def distribute_cards(deck, num_players):
    cards_per_player = len(deck) // num_players
    distributed = {f'Player {i+1}': deck[i * cards_per_player: (i + 1) * cards_per_player] for i in range(num_players)}
    extra_deck = deck[num_players * cards_per_player:]  # Extra cards
    return distributed, extra_deck

if __name__ == '__main__':
    app.run(debug=True)
