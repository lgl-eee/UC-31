from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

TIMES = ['Brasil', 'Argentina', 'Alemanha', 'França']

def iniciar_placar():
    session['placar'] = {time: 0 for time in TIMES}

@app.route('/')
def mostrar_placar():
    iniciar_placar()
    return session['placar']

@app.route('/ponto/<time>')
def adicionar_ponto(time):
    if time not in TIMES:
        return "Time inválido", 400

    session['placar'][time] += 1
    return session['placar']

@app.route('/zerar')
def zerar_placar():
    session['placar'] = {time: 0 for time in TIMES}
    return session['placar']

if __name__ == '__main__':
    app.run(debug=True)