import os
import re
from datetime import datetime, date
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager, migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'doapet.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')

# Inicializar extensões
db.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)

login_manager.login_view = 'login'

# Importar modelos após inicializar as extensões
from models import User, Animal, Vacina, FormularioAdotante, Candidatura, Favorito, LogAcao, Mensagem, Notificacao

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def registrar_log(usuario_id, acao):
    try:
        log = LogAcao(usuario_id=usuario_id, acao=acao)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar log: {e}")

def filtrar_profanidades(texto):
    if not texto:
        return texto
    
    # Lista de palavrões comuns em português
    palavroes = [
        r'puta', r'puto', r'porra', r'caralho', r'foder', r'foda', r'fode', r'foderam', r'fodesse',
        r'arrombado', r'arrombada', r'viado', r'veado', r'merda', r'bosta', r'escroto', r'escrota',
        r'filho\s*da\s*puta', r'fdp', r'cu', r'cú', r'corno', r'corna', r'otário', r'otaria', r'otario',
        r'otária', r'cacete', r'imbecil', r'babaca', r'pinto', r'caralinho', r'buceta', r'xereca',
        r'desgraçado', r'desgraçada', r'filho\s*de\s*puta', r'vai\s+se\s+fuder', r'vai\s+se\s+foder',
        r'vai\s+tomar\s+no\s+cu', r'vai\s+tomar\s+no\s+cú'
    ]
    
    # Criar padrão regex com limites de palavras (\b) para evitar falsos positivos
    padrao = re.compile(r'\b(' + '|'.join(palavroes) + r')\b', re.IGNORECASE)
    
    def substituir(match):
        palavra = match.group(0)
        return '*' * len(palavra)
        
    return padrao.sub(substituir, texto)

# Rota para inicializar o banco de dados (útil localmente e em produção de forma simples)
@app.route('/init-db')
def init_db():
    try:
        db.drop_all()
        db.create_all()
        
        # Criar um administrador padrão
        admin = User(
            email='admin@doapet.com',
            nome='Administrador PetMatch',
            tipo='ONG',
            cpf='000.000.000-00',
            is_admin=True
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()
        registrar_log(admin.id, "Banco de dados inicializado e re-semeado")

        # Criar pets de demonstração com foto_url
        pet1 = Animal(
            nome='Pipoca',
            especie='Cão',
            porte='Pequeno',
            sexo='Fêmea',
            status='Disponivel',
            foto_url='pipoca.png',
            ong_id=admin.id,
            tags_string='Dócil, Brincalhão, Castrado, ONG/Protetor'
        )
        pet2 = Animal(
            nome='Mingau',
            especie='Gato',
            porte='Pequeno',
            sexo='Macho',
            status='Disponivel',
            foto_url='mingau.png',
            ong_id=admin.id,
            tags_string='Independente, Calmo, ONG/Protetor'
        )
        pet3 = Animal(
            nome='Thor',
            especie='Cão',
            porte='Grande',
            sexo='Macho',
            status='Negociacao',
            foto_url='thor.png',
            ong_id=admin.id,
            tags_string='Protetor, Ativo, Precisa de espaço, ONG/Protetor'
        )
        pet4 = Animal(
            nome='Luna',
            especie='Gato',
            porte='Pequeno',
            sexo='Fêmea',
            status='Disponivel',
            foto_url='luna.png',
            ong_id=admin.id,
            tags_string='Brincalhona, Amigável, Curiosa, ONG/Protetor'
        )
        pet5 = Animal(
            nome='Bob',
            especie='Cão',
            porte='Médio',
            sexo='Macho',
            status='Disponivel',
            foto_url='bob.png',
            ong_id=admin.id,
            tags_string='Ativo, Carinhoso, Inteligente, ONG/Protetor'
        )
        pet6 = Animal(
            nome='Mel',
            especie='Cão',
            porte='Pequeno',
            sexo='Fêmea',
            status='Disponivel',
            foto_url='mel.png',
            ong_id=admin.id,
            tags_string='Dócil, Calma, Castrada, ONG/Protetor'
        )
        pet7 = Animal(
            nome='Fred',
            especie='Ave',
            porte='Pequeno',
            sexo='Macho',
            status='Disponivel',
            foto_url='fred.png',
            ong_id=admin.id,
            tags_string='Tagarela, Manso, Ativo, ONG/Protetor'
        )
        pet8 = Animal(
            nome='Alvin',
            especie='Roedor',
            porte='Pequeno',
            sexo='Macho',
            status='Disponivel',
            foto_url='alvin.png',
            ong_id=admin.id,
            tags_string='Curioso, Brincalhão, Rápido, ONG/Protetor'
        )
        db.session.add_all([pet1, pet2, pet3, pet4, pet5, pet6, pet7, pet8])
        db.session.commit()
        
        # Adicionar vacinas com datas estratégicas (considerando data atual = 30/05/2026)
        # Verde (em dia, vence em 2027)
        v1_1 = Vacina(animal_id=pet1.id, nome_vacina='Antirrábica', data_aplicacao=date(2026, 1, 10), data_proxima_dose=date(2027, 1, 10))
        # Vermelho (atrasada, venceu em 20/04/2026)
        v1_2 = Vacina(animal_id=pet1.id, nome_vacina='V10', data_aplicacao=date(2025, 4, 20), data_proxima_dose=date(2026, 4, 20))
        
        # Verde (em dia)
        v2_1 = Vacina(animal_id=pet2.id, nome_vacina='Quádrupla Felina', data_aplicacao=date(2026, 3, 15), data_proxima_dose=date(2027, 3, 15))
        
        # Amarelo (vence em breve, em 15/06/2026 - menos de 30 dias)
        v3_1 = Vacina(animal_id=pet3.id, nome_vacina='Antirrábica', data_aplicacao=date(2025, 6, 15), data_proxima_dose=date(2026, 6, 15))
        
        # Adicionar vacinas para os novos animais
        v4_1 = Vacina(animal_id=pet4.id, nome_vacina='Tríplice Felina', data_aplicacao=date(2026, 2, 20), data_proxima_dose=date(2027, 2, 20))
        v5_1 = Vacina(animal_id=pet5.id, nome_vacina='Múltipla V8', data_aplicacao=date(2026, 1, 15), data_proxima_dose=date(2027, 1, 15))
        v6_1 = Vacina(animal_id=pet6.id, nome_vacina='Antirrábica', data_aplicacao=date(2026, 4, 10), data_proxima_dose=date(2027, 4, 10))
        
        # Aves e roedores (checkups e prevenções)
        v7_1 = Vacina(animal_id=pet7.id, nome_vacina='Check-up Geral', data_aplicacao=date(2026, 5, 1), data_proxima_dose=date(2027, 5, 1))
        v8_1 = Vacina(animal_id=pet8.id, nome_vacina='Vermífugo e Vitaminas', data_aplicacao=date(2026, 3, 10), data_proxima_dose=date(2027, 3, 10))
        
        db.session.add_all([v1_1, v1_2, v2_1, v3_1, v4_1, v5_1, v6_1, v7_1, v8_1])
        db.session.commit()
        
        registrar_log(admin.id, "Animais de teste semeados com fotos e prontuários de vacinas")
        return "Banco de dados inicializado e semeado com sucesso com 8 animais (incluindo aves e roedores)!"
    except Exception as e:
        db.session.rollback()
        return f"Erro ao inicializar banco de dados: {e}"

@app.route('/')
def index():
    # Buscar animais ativos (disponíveis ou em negociação) para o carrossel da home
    animais = Animal.query.filter(Animal.status != 'Doado').order_by(Animal.data_cadastro.desc()).all()
    
    # Buscar animais adotados (status = Doado)
    adotados = Animal.query.filter_by(status='Doado').order_by(Animal.data_cadastro.desc()).all()
    
    # Estatísticas reais com base nos dados do banco
    total_adotados = Animal.query.filter_by(status='Doado').count()
    total_candidaturas = Candidatura.query.count()
    total_cadastrados = Animal.query.count()
    
    return render_template('index.html', 
                           animais=animais, 
                           adotados=adotados,
                           total_adotados=total_adotados, 
                           total_candidaturas=total_candidaturas, 
                           total_cadastrados=total_cadastrados)

@app.route('/catalogo')
def catalogo():
    especie = request.args.get('especie', '')
    porte = request.args.get('porte', '')
    sexo = request.args.get('sexo', '')
    tag = request.args.get('tag', '')
    
    query = Animal.query.filter(Animal.status != 'Doado')
    
    if especie:
        query = query.filter_by(especie=especie)
    if porte:
        query = query.filter_by(porte=porte)
    if sexo:
        query = query.filter_by(sexo=sexo)
    if tag:
        query = query.filter(Animal.tags_string.contains(tag))
        
    animais = query.order_by(Animal.data_cadastro.desc()).all()
    
    # Extrai todas as tags únicas
    todas_tags = set()
    for pet in Animal.query.all():
        todas_tags.update(pet.tags)
        
    return render_template('catalogo.html', animais=animais, todas_tags=sorted(list(todas_tags)), especie_sel=especie, porte_sel=porte, sexo_sel=sexo, tag_sel=tag)

@app.route('/animal/<int:id>')
def detalhes_animal(id):
    pet = Animal.query.get_or_404(id)
    
    # Verificar se o usuário atual favoritou ou se candidatou para este pet
    ja_favorito = False
    ja_candidatado = False
    if current_user.is_authenticated:
        ja_favorito = Favorito.query.filter_by(user_id=current_user.id, animal_id=pet.id).first() is not None
        ja_candidatado = Candidatura.query.filter_by(adotante_id=current_user.id, animal_id=pet.id).first() is not None
        
    usuario_id = current_user.id if current_user.is_authenticated else None
    registrar_log(usuario_id, f"Visualizou detalhes do pet: {pet.nome} (ID: {pet.id})")
    
    return render_template('detalhes.html', pet=pet, ja_favorito=ja_favorito, ja_candidatado=ja_candidatado)

@app.route('/animal/<int:id>/candidatar', methods=['POST'])
@login_required
def candidatar_animal(id):
    pet = Animal.query.get_or_404(id)
    
    # Impedir que ONG/Protetor se candidate
    if current_user.tipo in ['ONG', 'PROTETOR']:
        flash("Apenas usuários do tipo Adotante podem se candidatar para adoção.", "danger")
        return redirect(url_for('detalhes_animal', id=id))
        
    # Verificar candidatura existente
    candidatura_existente = Candidatura.query.filter_by(adotante_id=current_user.id, animal_id=pet.id).first()
    if candidatura_existente:
        flash("Você já se candidatou para adotar este animal!", "info")
        return redirect(url_for('detalhes_animal', id=id))
        
    # Criar candidatura
    nova_candidatura = Candidatura(
        animal_id=pet.id,
        adotante_id=current_user.id,
        status='Pendente'
    )
    db.session.add(nova_candidatura)
    
    # Criar notificação para o dono do pet
    if pet.ong_id != current_user.id:
        nova_notif = Notificacao(
            user_id=pet.ong_id,
            mensagem=f"<strong>{current_user.nome}</strong> se candidatou para adotar seu pet <strong>{pet.nome}</strong>!"
        )
        db.session.add(nova_notif)
        
    db.session.commit()
    
    registrar_log(current_user.id, f"Se candidatou para adotar o pet: {pet.nome} (ID: {pet.id})")
    flash(f"Sua candidatura para adotar {pet.nome} foi enviada com sucesso! A ONG responsável analisará sua solicitação.", "success")
    return redirect(url_for('detalhes_animal', id=id))

@app.route('/animal/<int:id>/favoritar', methods=['POST'])
@login_required
def favoritar_animal(id):
    pet = Animal.query.get_or_404(id)
    
    favorito = Favorito.query.filter_by(user_id=current_user.id, animal_id=pet.id).first()
    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        registrar_log(current_user.id, f"Removeu pet dos favoritos: {pet.nome} (ID: {pet.id})")
        flash(f"{pet.nome} foi removido dos seus favoritos.", "info")
    else:
        novo_favorito = Favorito(user_id=current_user.id, animal_id=pet.id)
        db.session.add(novo_favorito)
        
        # Criar notificação para o dono do pet
        if pet.ong_id != current_user.id:
            nova_notif = Notificacao(
                user_id=pet.ong_id,
                mensagem=f"<strong>{current_user.nome}</strong> favoritou seu pet <strong>{pet.nome}</strong>!"
            )
            db.session.add(nova_notif)
            
        db.session.commit()
        registrar_log(current_user.id, f"Adicionou pet aos favoritos: {pet.nome} (ID: {pet.id})")
        flash(f"{pet.nome} foi adicionado aos seus favoritos!", "success")
        
    return redirect(url_for('detalhes_animal', id=id))

@app.route('/cadastrar-pet', methods=['GET', 'POST'])
@login_required
def cadastrar_pet():
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        especie = request.form.get('especie')
        porte = request.form.get('porte')
        sexo = request.form.get('sexo')
        tags = request.form.get('tags', '')
        
        # Upload de foto com limite de 5MB
        foto = request.files.get('foto')
        foto_nome = None
        if foto and foto.filename:
            # Verificar tamanho do arquivo
            foto.seek(0, os.SEEK_END)
            tamanho_arquivo = foto.tell()
            foto.seek(0) # resetar ponteiro de leitura do arquivo
            
            if tamanho_arquivo > 5 * 1024 * 1024:
                flash("A imagem selecionada é maior que 5MB. Escolha uma foto menor.", "danger")
                return render_template('cadastrar_pet.html')

            # Gerar nome único para evitar colisões
            ext = os.path.splitext(foto.filename)[1]
            foto_nome = f"pet_{int(datetime.now().timestamp())}{ext}"
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_nome))
            
        # Adicionar tag "ONG/Protetor" se for cadastrado por uma ONG ou Protetor
        if current_user.tipo in ['ONG', 'PROTETOR']:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if "ONG/Protetor" not in tag_list:
                tag_list.append("ONG/Protetor")
            tags = ', '.join(tag_list)
            
        novo_pet = Animal(
            nome=nome,
            especie=especie,
            porte=porte,
            sexo=sexo,
            status='Disponivel',
            foto_url=foto_nome,
            tags_string=tags,
            ong_id=current_user.id
        )
        db.session.add(novo_pet)
        db.session.commit()
        
        registrar_log(current_user.id, f"Cadastrou um novo pet: {nome} (ID: {novo_pet.id})")
        flash(f"O pet {nome} foi cadastrado com sucesso!", "success")
        return redirect(url_for('detalhes_animal', id=novo_pet.id))
        
    return render_template('cadastrar_pet.html')

@app.route('/animal/<int:id>/vacina', methods=['POST'])
@login_required
def adicionar_vacina(id):
    pet = Animal.query.get_or_404(id)
    
    # Apenas a ONG dona do pet pode gerenciar
    if current_user.id != pet.ong_id:
        flash("Você não tem permissão para adicionar vacinas a este animal.", "danger")
        return redirect(url_for('detalhes_animal', id=id))
        
    nome_vacina = request.form.get('nome_vacina')
    data_aplicacao_str = request.form.get('data_aplicacao')
    data_proxima_str = request.form.get('data_proxima_dose')
    
    if not nome_vacina or not data_aplicacao_str:
        flash("Nome da vacina e data de aplicação são obrigatórios.", "danger")
        return redirect(url_for('detalhes_animal', id=id))
        
    try:
        data_aplicacao = datetime.strptime(data_aplicacao_str, '%Y-%m-%d').date()
        data_proxima = None
        if data_proxima_str:
            data_proxima = datetime.strptime(data_proxima_str, '%Y-%m-%d').date()
            
        nova_vacina = Vacina(
            animal_id=pet.id,
            nome_vacina=nome_vacina,
            data_aplicacao=data_aplicacao,
            data_proxima_dose=data_proxima
        )
        db.session.add(nova_vacina)
        db.session.commit()
        
        registrar_log(current_user.id, f"Adicionou vacina {nome_vacina} ao pet: {pet.nome} (ID: {pet.id})")
        flash("Vacina adicionada ao prontuário com sucesso!", "success")
    except ValueError:
        flash("Formato de data inválido.", "danger")
        
    return redirect(url_for('detalhes_animal', id=id))

@app.route('/animal/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_animal(id):
    pet = Animal.query.get_or_404(id)
    
    # Permitir exclusão apenas se for admin ou o criador (ONG) do pet
    if not current_user.is_admin and current_user.id != pet.ong_id:
        flash("Você não tem permissão para remover esta publicação.", "danger")
        return redirect(url_for('detalhes_animal', id=id))
        
    nome_pet = pet.nome
    db.session.delete(pet)
    db.session.commit()
    
    registrar_log(current_user.id, f"Removeu a publicação do pet: {nome_pet} (ID: {id})")
    flash(f"Publicação de {nome_pet} removida com sucesso!", "success")
    
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('catalogo'))

@app.route('/animal/<int:id>/adotado', methods=['POST'])
@login_required
def marcar_adotado(id):
    pet = Animal.query.get_or_404(id)
    
    # Apenas o criador (ONG/dono) do pet ou admin pode marcar como adotado
    if current_user.id != pet.ong_id and not current_user.is_admin:
        flash("Você não tem permissão para alterar o status deste animal.", "danger")
        return redirect(url_for('ver_perfil'))
        
    pet.status = 'Doado'
    
    # Recusar candidaturas pendentes deste animal
    candidaturas_pendentes = Candidatura.query.filter_by(animal_id=pet.id, status='Pendente').all()
    for cand in candidaturas_pendentes:
        cand.status = 'Recusado'
        
    db.session.commit()
    
    registrar_log(current_user.id, f"Marcou o pet {pet.nome} como adotado (ID: {pet.id})")
    flash(f"Que ótima notícia! {pet.nome} agora está marcado como adotado. 🎉", "success")
    return redirect(url_for('ver_perfil'))

@app.route('/admin/usuario/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_usuario(id):
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem executar esta ação.", "danger")
        return redirect(url_for('index'))
        
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash("Você não pode remover uma conta administradora.", "danger")
        return redirect(url_for('admin_dashboard'))
        
    nome_usuario = user.nome
    db.session.delete(user)
    db.session.commit()
    
    registrar_log(current_user.id, f"Removeu o usuário: {nome_usuario} (ID: {id})")
    flash(f"Usuário {nome_usuario} removido com sucesso!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/contato', methods=['GET', 'POST'])
def contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')
        
        # Registra log
        usuario_id = current_user.id if current_user.is_authenticated else None
        registrar_log(usuario_id, f"Mensagem de contato enviada por {nome} ({email}) - Assunto: {assunto}")
        
        flash("Mensagem enviada com sucesso! Entraremos em contato em breve.", "success")
        return redirect(url_for('contato'))
    return render_template('contato.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        cpf = request.form.get('cpf')
        whatsapp = request.form.get('whatsapp')
        data_nascimento_str = request.form.get('data_nascimento')
        tipo = request.form.get('tipo')
        senha = request.form.get('senha')
        
        # Validar e-mail único
        if User.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "danger")
            return redirect(url_for('registrar'))
            
        # Validar CPF único
        if User.query.filter_by(cpf=cpf).first():
            flash("Este CPF já está cadastrado.", "danger")
            return redirect(url_for('registrar'))
            
        # Converter data de nascimento
        if not data_nascimento_str:
            flash("Data de nascimento é obrigatória.", "danger")
            return redirect(url_for('registrar'))
            
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Data de nascimento inválida.", "danger")
            return redirect(url_for('registrar'))
            
        # Validar idade mínima (18 anos) para adotantes
        hoje = date.today()
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        if tipo == 'ADOTANTE' and idade < 18:
            flash("Você precisa ter pelo menos 18 anos para se cadastrar como Adotante.", "danger")
            return redirect(url_for('registrar'))
            
        # Criar usuário
        novo_usuario = User(
            nome=nome,
            email=email,
            cpf=cpf,
            whatsapp=whatsapp,
            data_nascimento=data_nascimento,
            tipo=tipo
        )
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Logar ação
        registrar_log(novo_usuario.id, f"Novo usuário cadastrado: {nome} como {tipo}")
        
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for('login'))
        
    return render_template('registrar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = User.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            registrar_log(usuario.id, "Usuário realizou login com sucesso")
            
            if usuario.is_admin:
                return redirect(url_for('admin_dashboard'))
                
            return redirect(url_for('index'))
        else:
            flash("Credenciais inválidas. Verifique seu e-mail e senha.", "danger")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    registrar_log(current_user.id, "Usuário realizou logout")
    logout_user()
    flash("Sessão encerrada com sucesso.", "success")
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem acessar esta área.", "danger")
        return redirect(url_for('index'))
        
    usuarios = User.query.all()
    pets = Animal.query.all()
    candidaturas = Candidatura.query.all()
    logs = LogAcao.query.order_by(LogAcao.data_hora.desc()).limit(100).all()
    
    return render_template('admin.html', usuarios=usuarios, pets=pets, candidaturas=candidaturas, logs=logs)

@app.route('/minhas-candidaturas')
@login_required
def minhas_candidaturas():
    if current_user.tipo in ['ONG', 'PROTETOR']:
        return redirect(url_for('gerenciar_candidaturas'))
    candidaturas = Candidatura.query.filter_by(adotante_id=current_user.id).order_by(Candidatura.data_solicitacao.desc()).all()
    return render_template('minhas_candidaturas.html', candidaturas=candidaturas)

@app.route('/gerenciar-candidaturas')
@login_required
def gerenciar_candidaturas():
    if current_user.tipo not in ['ONG', 'PROTETOR']:
        return redirect(url_for('minhas_candidaturas'))
    
    candidaturas = Candidatura.query.join(Animal).filter(Animal.ong_id == current_user.id).order_by(Candidatura.data_solicitacao.desc()).all()
    return render_template('gerenciar_candidaturas.html', candidaturas=candidaturas)

@app.route('/candidatura/<int:id>/status/<string:acao>', methods=['POST'])
@login_required
def atualizar_status_candidatura(id, acao):
    candidatura = Candidatura.query.get_or_404(id)
    pet = candidatura.animal
    
    if pet.ong_id != current_user.id:
        flash("Você não tem permissão para alterar o status desta candidatura.", "danger")
        return redirect(url_for('gerenciar_candidaturas'))
        
    if acao == 'aprovar':
        candidatura.status = 'Aprovado'
        pet.status = 'Negociacao'
        registrar_log(current_user.id, f"Aprovou a candidatura de {candidatura.adotante.nome} para o pet: {pet.nome} (ID: {pet.id})")
        flash(f"Candidatura de {candidatura.adotante.nome} aprovada! O pet {pet.nome} agora está marcado 'Em Negociação'.", "success")
    elif acao == 'recusar':
        candidatura.status = 'Recusado'
        registrar_log(current_user.id, f"Recusou a candidatura de {candidatura.adotante.nome} para o pet: {pet.nome} (ID: {pet.id})")
        flash(f"Candidatura de {candidatura.adotante.nome} recusada.", "info")
        
    db.session.commit()
    return redirect(url_for('gerenciar_candidaturas'))

@app.route('/favoritos')
@login_required
def ver_favoritos():
    favoritos = Favorito.query.filter_by(user_id=current_user.id).all()
    return render_template('favoritos.html', favoritos=favoritos)

@app.route('/perfil')
@login_required
def ver_perfil():
    meus_pets = Animal.query.filter_by(ong_id=current_user.id).order_by(Animal.data_cadastro.desc()).all()
    meus_favoritos = []
    minhas_candidaturas_pets = []
    if current_user.tipo in ['ONG', 'PROTETOR']:
        total_pets = len(meus_pets)
        total_solicitacoes = Candidatura.query.join(Animal).filter(Animal.ong_id == current_user.id).count()
        stats = {'total_pets': total_pets, 'total_solicitacoes': total_solicitacoes}
    else:
        total_solicitacoes = Candidatura.query.filter_by(adotante_id=current_user.id).count()
        total_favs = Favorito.query.filter_by(user_id=current_user.id).count()
        stats = {'total_pets': len(meus_pets), 'total_solicitacoes': total_solicitacoes, 'total_favs': total_favs}
        # Buscar animais favoritados
        favoritos = Favorito.query.filter_by(user_id=current_user.id).all()
        meus_favoritos = [f.animal for f in favoritos]
        # Buscar animais que se candidatou
        candidaturas = Candidatura.query.filter_by(adotante_id=current_user.id).all()
        minhas_candidaturas_pets = [{'animal': c.animal, 'status': c.status} for c in candidaturas]
        
    return render_template('perfil.html', stats=stats, meus_pets=meus_pets, meus_favoritos=meus_favoritos, minhas_candidaturas_pets=minhas_candidaturas_pets)

# ==================== SISTEMA DE CHAT ====================

@app.route('/minhas-conversas')
@login_required
def minhas_conversas():
    """Lista todas as conversas ativas (candidaturas pendentes ou aprovadas) do usuário."""
    # Buscar candidaturas onde o usuário é o adotante OU é dono do pet (quem cadastrou)
    # Apenas candidaturas com status 'Pendente' ou 'Aprovado'
    candidaturas_adotante = Candidatura.query.filter(
        Candidatura.status.in_(['Pendente', 'Aprovado']),
        Candidatura.adotante_id == current_user.id
    ).all()
    
    candidaturas_dono = Candidatura.query.filter(
        Candidatura.status.in_(['Pendente', 'Aprovado'])
    ).join(Animal).filter(
        Animal.ong_id == current_user.id
    ).all()
    
    # Unificar e ordenar por data de solicitação decrescente
    candidaturas_set = set(candidaturas_adotante + candidaturas_dono)
    candidaturas = sorted(list(candidaturas_set), key=lambda x: x.data_solicitacao, reverse=True)
    
    # Para cada candidatura, buscar a última mensagem e contar as não lidas
    conversas = []
    for cand in candidaturas:
        ultima_msg = Mensagem.query.filter_by(candidatura_id=cand.id).order_by(Mensagem.data_envio.desc()).first()
        nao_lidas = Mensagem.query.filter_by(candidatura_id=cand.id, lida=False).filter(Mensagem.remetente_id != current_user.id).count()
        conversas.append({
            'candidatura': cand,
            'ultima_mensagem': ultima_msg,
            'nao_lidas': nao_lidas
        })
    
    return render_template('conversas.html', conversas=conversas)

@app.route('/chat/<int:candidatura_id>')
@login_required
def chat(candidatura_id):
    """Página do chat para uma candidatura aprovada."""
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    pet = candidatura.animal
    
    # Verificar se o usuário tem permissão (é o adotante ou o dono do pet)
    if current_user.id != candidatura.adotante_id and current_user.id != pet.ong_id:
        flash("Você não tem permissão para acessar esta conversa.", "danger")
        return redirect(url_for('index'))
    
    # Verificar se a candidatura foi aprovada ou está pendente
    if candidatura.status not in ['Pendente', 'Aprovado']:
        flash("O chat está disponível apenas para candidaturas ativas.", "info")
        return redirect(url_for('minhas_candidaturas'))
    
    # Marcar mensagens do outro como lidas
    Mensagem.query.filter_by(candidatura_id=candidatura_id, lida=False).filter(Mensagem.remetente_id != current_user.id).update({'lida': True})
    db.session.commit()
    
    # Buscar todas as mensagens
    mensagens = Mensagem.query.filter_by(candidatura_id=candidatura_id).order_by(Mensagem.data_envio.asc()).all()
    
    # Determinar o interlocutor
    if current_user.id == candidatura.adotante_id:
        interlocutor = pet.ong
    else:
        interlocutor = candidatura.adotante
    
    return render_template('chat.html', candidatura=candidatura, pet=pet, mensagens=mensagens, interlocutor=interlocutor)

@app.route('/chat/<int:candidatura_id>/enviar', methods=['POST'])
@login_required
def enviar_mensagem(candidatura_id):
    """Endpoint AJAX para enviar uma mensagem."""
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    pet = candidatura.animal
    
    # Verificar permissão
    if current_user.id != candidatura.adotante_id and current_user.id != pet.ong_id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    if candidatura.status not in ['Pendente', 'Aprovado']:
        return jsonify({'error': 'Chat indisponível'}), 403
    
    conteudo = request.json.get('conteudo', '').strip()
    if not conteudo:
        return jsonify({'error': 'Mensagem vazia'}), 400
    
    conteudo = filtrar_profanidades(conteudo)
    
    nova_msg = Mensagem(
        candidatura_id=candidatura_id,
        remetente_id=current_user.id,
        conteudo=conteudo
    )
    db.session.add(nova_msg)
    db.session.commit()
    
    return jsonify({
        'id': nova_msg.id,
        'remetente_id': nova_msg.remetente_id,
        'remetente_nome': nova_msg.remetente.nome,
        'conteudo': nova_msg.conteudo,
        'data_envio': nova_msg.data_envio.strftime('%H:%M'),
        'data_completa': nova_msg.data_envio.strftime('%d/%m/%Y %H:%M'),
        'eh_minha': True
    })

@app.route('/chat/<int:candidatura_id>/mensagens')
@login_required
def buscar_mensagens(candidatura_id):
    """Endpoint AJAX para polling de novas mensagens."""
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    pet = candidatura.animal
    
    # Verificar permissão
    if current_user.id != candidatura.adotante_id and current_user.id != pet.ong_id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    # Buscar mensagens após o último ID conhecido
    after_id = request.args.get('after', 0, type=int)
    novas_mensagens = Mensagem.query.filter_by(candidatura_id=candidatura_id).filter(Mensagem.id > after_id).order_by(Mensagem.data_envio.asc()).all()
    
    # Marcar como lidas as mensagens do outro
    for msg in novas_mensagens:
        if msg.remetente_id != current_user.id and not msg.lida:
            msg.lida = True
    db.session.commit()
    
    return jsonify([{
        'id': msg.id,
        'remetente_id': msg.remetente_id,
        'remetente_nome': msg.remetente.nome,
        'conteudo': msg.conteudo,
        'data_envio': msg.data_envio.strftime('%H:%M'),
        'data_completa': msg.data_envio.strftime('%d/%m/%Y %H:%M'),
        'eh_minha': msg.remetente_id == current_user.id
    } for msg in novas_mensagens])

@app.route('/perfil/<int:user_id>')
@login_required
def ver_perfil_publico(user_id):
    """Ver perfil público de outro usuário (acessível via chat)."""
    usuario = User.query.get_or_404(user_id)
    
    # Buscar estatísticas públicas
    if usuario.tipo in ['ONG', 'PROTETOR']:
        total_pets = Animal.query.filter_by(ong_id=usuario.id).count()
        pets_usuario = Animal.query.filter_by(ong_id=usuario.id).order_by(Animal.data_cadastro.desc()).all()
        stats = {'total_pets': total_pets}
    else:
        total_solicitacoes = Candidatura.query.filter_by(adotante_id=usuario.id).count()
        pets_usuario = []
        stats = {'total_solicitacoes': total_solicitacoes}
    
    return render_template('perfil_publico.html', usuario=usuario, stats=stats, pets_usuario=pets_usuario)

@app.route('/notificacoes')
@login_required
def ver_notificacoes():
    notificacoes = Notificacao.query.filter_by(user_id=current_user.id).order_by(Notificacao.data_criacao.desc()).all()
    # Marcar todas como lidas quando o usuário entra na página
    Notificacao.query.filter_by(user_id=current_user.id, lida=False).update({'lida': True})
    db.session.commit()
    return render_template('notificacoes.html', notificacoes=notificacoes)

@app.route('/notificacoes/limpar', methods=['POST'])
@login_required
def limpar_notificacoes():
    Notificacao.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Notificações limpas com sucesso.", "success")
    return redirect(url_for('ver_notificacoes'))

@app.context_processor
def inject_unread_counts():
    if current_user.is_authenticated:
        from sqlalchemy import or_
        msg_count = Mensagem.query.join(Candidatura).join(Animal).filter(
            Candidatura.status.in_(['Pendente', 'Aprovado']),
            Mensagem.lida == False,
            Mensagem.remetente_id != current_user.id
        ).filter(
            or_(
                Candidatura.adotante_id == current_user.id,
                Animal.ong_id == current_user.id
            )
        ).count()
        
        notif_count = Notificacao.query.filter_by(user_id=current_user.id, lida=False).count()
        return dict(unread_messages_count=msg_count, unread_notifications_count=notif_count)
    return dict(unread_messages_count=0, unread_notifications_count=0)

if __name__ == '__main__':
    app.run(debug=True)
