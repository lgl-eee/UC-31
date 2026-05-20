from flask import Flask, render_template, request
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/resultados', methods=['GET'])
def resultados():
    nome = request.args.get('nome')
    curso = request.args.get('curso')
    cidade = request.args.get('cidade')
    return "{}, {} e {}".format(nome, curso, cidade)


if __name__ == '__main__':
    app.run(debug=True)
