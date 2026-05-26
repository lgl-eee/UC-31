from flask import Flask, render_template

app = Flask(_name_)

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/servicos")
def servicos():
    return render_template("servicos.html")

if __name__ == "__main__":
    app.run(debug=True)