from flask import Flask, render_template, request, session 

app = Flask(__name__)
app.secret_key = 'chave_secreta'

@app.route('/contador', methods=['GET', 'POST'])
def contador():
    if 'contador_visitas' not in session:
        session['contador_visitas'] = 0
    if request.method == 'POST':
        session['contador_visitas'] += 1
    return render_template('contador.html', contador_visitas=session['contador_visitas'])

if __name__ == '__main__':
    app.run(debug=True)    