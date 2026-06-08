from flask import(
    Flask,
    render_template,
    request,
    make_response,
    redirect,
    url_for
)

app = Flask(__name__)

@app.route('/')
def inicio():
    
    #lê o cookie
    tema = request.cookies.get('tema', 'claro')

    return render_template(
        inicio.html,
        tema=tema
    )

@app.route('/tema/<escolha>')
def trocar_tema(escolha):

    if escolha not in ['claro', 'escuro']:
        escolha = 'claro'

    resposta = make_response(
        redirect(url_for('inicio'))
    )

    resposta.set_cookie(
        'tema',
        escolha,
        max_age=60*60*24*30    
    )

    return resposta
if __name__ == '__main__':
    app.run(debug=True)