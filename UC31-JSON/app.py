from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route("/")
def produtos():
    
    with open("produtos.json", "r", encoding="utf-8") as arquivo:
        lista_produtos = json.load(arquivo)

    retur render_template("produtos.html", produtos=lista_produtos)

if __name__ == "__main__"
    app.run(debug=True)
