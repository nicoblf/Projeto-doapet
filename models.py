from datetime import datetime, timezone, timedelta
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class BaseModel(db.Model):
    __abstract__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='ADOTANTE') # 'ONG', 'PROTETOR', 'ADOTANTE'
    data_nascimento = db.Column(db.Date, nullable=True) # Obrigatório para adotantes para validar +18
    whatsapp = db.Column(db.String(20), nullable=True)
    chave_pix = db.Column(db.String(100), nullable=True) # Apenas para ONGs/Protetores receberem apoio
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    pets = db.relationship('Animal', backref='ong', lazy=True)
    formulario = db.relationship('FormularioAdotante', backref='user', uselist=False, lazy=True)
    candidaturas = db.relationship('Candidatura', backref='adotante', lazy=True)
    favoritos = db.relationship('Favorito', backref='user', lazy=True)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
        
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class FormularioAdotante(BaseModel):
    __tablename__ = 'formularios_adotantes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_residencia = db.Column(db.String(50), nullable=False) # 'Casa', 'Apartamento', etc.
    tempo_livre = db.Column(db.Integer, nullable=False) # Horas diárias dedicadas ao pet
    outros_pets = db.Column(db.String(3), nullable=False) # 'Sim' ou 'Não'
    orcamento_medio = db.Column(db.String(50), nullable=False) # 'Baixo', 'Médio', 'Alto'

class Animal(BaseModel):
    __tablename__ = 'animais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    especie = db.Column(db.String(20), nullable=False) # 'Cão', 'Gato'
    porte = db.Column(db.String(20), nullable=False) # 'Pequeno', 'Médio', 'Grande'
    sexo = db.Column(db.String(10), nullable=False) # 'Macho', 'Fêmea'
    status = db.Column(db.String(20), nullable=False, default='Disponivel') # 'Disponivel', 'Negociacao', 'Doado'
    foto_url = db.Column(db.String(256), nullable=True)
    ong_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags_string = db.Column(db.String(256), nullable=True, default='') # Salva tags separadas por vírgula (ex: "Dócil,Castrado,Ativo")
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None))
    
    # Relacionamentos
    vacinas = db.relationship('Vacina', backref='animal', cascade='all, delete-orphan', lazy=True)
    candidaturas = db.relationship('Candidatura', backref='animal', cascade='all, delete-orphan', lazy=True)
    favoritado_por = db.relationship('Favorito', backref='animal', cascade='all, delete-orphan', lazy=True)
    
    @property
    def tags(self):
        if not self.tags_string:
            return []
        return [tag.strip() for tag in self.tags_string.split(',') if tag.strip()]

    @tags.setter
    def tags(self, tag_list):
        self.tags_string = ','.join([tag.strip() for tag in tag_list if tag.strip()])

class Vacina(BaseModel):
    __tablename__ = 'vacinas'
    
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animais.id'), nullable=False)
    nome_vacina = db.Column(db.String(100), nullable=False)
    data_aplicacao = db.Column(db.Date, nullable=False)
    data_proxima_dose = db.Column(db.Date, nullable=True)
    
    @property
    def status_vacina(self):
        # Retorna o status de semáforo dinamicamente: 'verde', 'amarelo' ou 'vermelho'
        hoje = datetime.now().date()
        if not self.data_proxima_dose:
            return 'verde'
        
        dias_restantes = (self.data_proxima_dose - hoje).days
        
        if dias_restantes < 0:
            return 'vermelho' # Vencida / Atrasada
        elif dias_restantes <= 30:
            return 'amarelo' # Próxima do vencimento (menos de 30 dias)
        else:
            return 'verde' # Em dia

class Favorito(BaseModel):
    __tablename__ = 'favoritos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animais.id'), nullable=False)

class Candidatura(BaseModel):
    __tablename__ = 'candidaturas'
    
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animais.id'), nullable=False)
    adotante_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_solicitacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None))
    status = db.Column(db.String(20), nullable=False, default='Pendente') # 'Pendente', 'Aprovado', 'Recusado'

class LogAcao(BaseModel):
    __tablename__ = 'logs_acoes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    acao = db.Column(db.String(255), nullable=False)
    data_hora = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None))
    
    usuario = db.relationship('User', backref='logs', lazy=True)

class Mensagem(BaseModel):
    __tablename__ = 'mensagens'
    
    id = db.Column(db.Integer, primary_key=True)
    candidatura_id = db.Column(db.Integer, db.ForeignKey('candidaturas.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None))
    lida = db.Column(db.Boolean, default=False)
    
    remetente = db.relationship('User', backref='mensagens_enviadas', lazy=True)
    candidatura = db.relationship('Candidatura', backref='mensagens', lazy=True)

class Notificacao(BaseModel):
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # User receiving the notification
    mensagem = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None))
    lida = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('notificacoes', cascade='all, delete-orphan', lazy=True))
