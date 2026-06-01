from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():

    mensagem = ""

    if request.method == 'POST':
        nome = request.form.get('nome')
        jogo = request.form.get('jogo')
        email = request.form.get('email')

        if not nome or not jogo or not email:
            mensagem = "Todos os campos são obrigatórios."
        else:
            mensagem = f"Usuário {nome} inscrito com sucesso no jogo {jogo}."

    return render_template('inscricao.html', mensagem=mensagem)

if __name__ == '__main__':
    app.run(debug=True)