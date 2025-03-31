from flask import Flask, render_template, session
from flask_cors import CORS

from routes.user import user
from routes.assistant import assistant

app = Flask(__name__)
app.secret_key = 'secret_key'
CORS(app)

app.register_blueprint(user)
app.register_blueprint(assistant)

@app.route('/')
def index():
    return render_template('auth.html')

@app.route('/chat')
def main():
    if "loggedin" in session and session["loggedin"]:
        return render_template("chat.html", user_id=session["user_id"])
    return render_template('auth.html')

if __name__ == '__main__':
    app.run(debug=True)
