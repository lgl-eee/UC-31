from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import os
import json
from datetime import date, timedelta
from statistics import mean
from functools import wraps



DATA_DIR = 'dados'
ESCOLAS_FILE = os.path.join(DATA_DIR, 'escolas.json')
AVAL_FILE = os.path.join(DATA_DIR, 'avaliacoes.json')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'trocar-por-uma-chave-secreta')


app.permanent_session_lifetime = timedelta(hours=2)

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ENV_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')  # opcional, dev only
ENV_ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

if ENV_ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = ENV_ADMIN_PASSWORD_HASH
else:
    ADMIN_PASSWORD_HASH = generate_password_hash(ENV_ADMIN_PASSWORD or 'admin123')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    ensure_data_dir()
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json_atomic(path, data):
    ensure_data_dir()
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def next_id(items):
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1

def annotate_escolas(escolas, avaliacoes):
    for e in escolas:
        notas = [a['estrela'] for a in avaliacoes if a.get('escola_id') == e.get('id')]
        e['num_avaliacoes'] = len(notas)
        e['media'] = round(mean(notas), 1) if notas else 0
    return escolas

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            # passar next para que após login volte para a página pretendida
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USER and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.permanent = True
            session['is_admin'] = True
            flash('Login efetuado com sucesso.', 'success')
            next_url = request.args.get('next') or url_for('admin')
            return redirect(next_url)
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('Logout efetuado.', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    escolas = load_json(ESCOLAS_FILE)
    avaliacoes = load_json(AVAL_FILE)
    annotate_escolas(escolas, avaliacoes)
    top3 = sorted(escolas, key=lambda x: x.get('media', 0), reverse=True)[:3]
    return render_template('index.html', top_escolas=top3)

@app.route('/escolas')
def listar_escolas():
    q = request.args.get('q', '').strip().lower()
    ordenar = request.args.get('ordenar', 'media')  # 'media' ou 'nome'
    escolas = load_json(ESCOLAS_FILE)
    avaliacoes = load_json(AVAL_FILE)
    annotate_escolas(escolas, avaliacoes)

    if q:
        escolas = [e for e in escolas if q in e.get('nome', '').lower() or q in e.get('cidade', '').lower()]

    if ordenar == 'nome':
        escolas = sorted(escolas, key=lambda x: x.get('nome', '').lower())
    else:
        escolas = sorted(escolas, key=lambda x: x.get('media', 0), reverse=True)

    return render_template('escolas.html', escolas=escolas, q=q, ordenar=ordenar)

@app.route('/escolas/<int:id>')
def detalhes(id):
    escolas = load_json(ESCOLAS_FILE)
    avaliacoes = load_json(AVAL_FILE)
    escola = next((e for e in escolas if e.get('id') == id), None)
    if not escola:
        flash('Escola não encontrada.', 'danger')
        return redirect(url_for('listar_escolas'))
    notas = [a for a in avaliacoes if a.get('escola_id') == id]
    escola = escola.copy()
    escola['num_avaliacoes'] = len(notas)
    escola['media'] = round(mean([n['estrela'] for n in notas]), 1) if notas else 0
    return render_template('detalhes.html', escola=escola, avaliacoes=notas)

@app.route('/cadastrar', methods=['GET', 'POST'])
@admin_required
def cadastrar():
    if request.method == 'POST':
        escolas = load_json(ESCOLAS_FILE)
        novo = {
            'id': next_id(escolas),
            'nome': request.form.get('nome', '').strip(),
            'morada': request.form.get('morada', '').strip(),
            'cidade': request.form.get('cidade', '').strip(),
            'descricao': request.form.get('descricao', '').strip(),
            'vagas': int(request.form.get('vagas') or 0),
            'telefone': request.form.get('telefone', '').strip(),
            'site': request.form.get('site', '').strip(),
            'foto': request.form.get('foto', '').strip()
        }
        if not novo['nome']:
            flash('O nome da escola é obrigatório.', 'danger')
            return render_template('cadastrar.html', escola=novo)
        escolas.append(novo)
        save_json_atomic(ESCOLAS_FILE, escolas)
        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('listar_escolas'))
    return render_template('cadastrar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    escolas = load_json(ESCOLAS_FILE)
    escola = next((e for e in escolas if e.get('id') == id), None)
    if not escola:
        flash('Escola não encontrada.', 'danger')
        return redirect(url_for('listar_escolas'))
    if request.method == 'POST':
        escola['nome'] = request.form.get('nome', escola.get('nome')).strip()
        escola['morada'] = request.form.get('morada', escola.get('morada')).strip()
        escola['cidade'] = request.form.get('cidade', escola.get('cidade')).strip()
        escola['descricao'] = request.form.get('descricao', escola.get('descricao')).strip()
        escola['vagas'] = int(request.form.get('vagas') or escola.get('vagas', 0))
        escola['telefone'] = request.form.get('telefone', escola.get('telefone')).strip()
        escola['site'] = request.form.get('site', escola.get('site')).strip()
        escola['foto'] = request.form.get('foto', escola.get('foto')).strip()
        save_json_atomic(ESCOLAS_FILE, escolas)
        flash('Escola atualizada com sucesso!', 'success')
        return redirect(url_for('detalhes', id=id))
    return render_template('editar.html', escola=escola)

@app.route('/deletar/<int:id>', methods=['POST'])
@admin_required
def deletar(id):
    escolas = load_json(ESCOLAS_FILE)
    avaliacoes = load_json(AVAL_FILE)
    escolas_novas = [e for e in escolas if e.get('id') != id]
    avaliacoes_novas = [a for a in avaliacoes if a.get('escola_id') != id]
    if len(escolas_novas) == len(escolas):
        flash('Escola não encontrada.', 'danger')
    else:
        save_json_atomic(ESCOLAS_FILE, escolas_novas)
        save_json_atomic(AVAL_FILE, avaliacoes_novas)
        flash('Escola e avaliações associadas removidas.', 'success')
    return redirect(url_for('listar_escolas'))

@app.route('/avaliar/<int:escola_id>', methods=['POST'])
def avaliar(escola_id):
    avaliacoes = load_json(AVAL_FILE)
    escolas = load_json(ESCOLAS_FILE)
    escola = next((e for e in escolas if e.get('id') == escola_id), None)
    if not escola:
        flash('Escola não encontrada.', 'danger')
        return redirect(url_for('listar_escolas'))
    try:
        estrela = int(request.form.get('estrela', 0))
    except ValueError:
        estrela = 0
    if estrela < 1 or estrela > 5:
        flash('A avaliação deve ter entre 1 e 5 estrelas.', 'danger')
        return redirect(url_for('detalhes', id=escola_id))
    nova = {
        'id': next_id(avaliacoes),
        'escola_id': escola_id,
        'autor': request.form.get('autor', 'Anónimo').strip() or 'Anónimo',
        'estrela': estrela,
        'comentario': request.form.get('comentario', '').strip(),
        'data': date.today().isoformat()
    }
    avaliacoes.append(nova)
    save_json_atomic(AVAL_FILE, avaliacoes)
    flash('Avaliação registada. Obrigado!', 'success')
    return redirect(url_for('detalhes', id=escola_id))

@app.route('/admin')
@admin_required
def admin():
    escolas = load_json(ESCOLAS_FILE)
    avaliacoes = load_json(AVAL_FILE)
    annotate_escolas(escolas, avaliacoes)
    total_escolas = len(escolas)
    total_avaliacoes = len(avaliacoes)
    top5 = sorted(escolas, key=lambda x: x.get('media', 0), reverse=True)[:5]
    return render_template('admin.html', total_escolas=total_escolas,
                           total_avaliacoes=total_avaliacoes, top5=top5)

if __name__ == '__main__':
    # Executar em desenvolvimento local: python app.py
    app.run(debug=True, host='0.0.0.0', port=5000)