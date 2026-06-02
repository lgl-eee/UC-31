from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    
    mensagem = ""

    if request.method == 'POST':
        nome = request.form.get('nome')
        if not nome:
            mensagem = "Nome é obrigatório."
        else:
            mensagem = f"Usuário {nome} cadastrado com sucesso."

    return render_template('cadastro.html', mensagem=mensagem)

@app.route('/validacao', methods=['POST'])
def cadastro():

    nome = request.form.get('nome', '').strip().title()
    email = request.form.get('email', '').strip().lower()
    cidade = request.form.get('cidade', '').strip().title()

    return f"""
    Nome: {nome}<br>
    Email: {email}<br>
    Cidade: {cidade}
    """

if __name__ == '__main__':
    app.run(debug=True)