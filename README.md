# 🐾 PetMatch - Portal de Adoção Responsável de Animais

O **PetMatch** é uma plataforma moderna desenvolvida para conectar ONGs, protetores independentes e adotantes de forma segura, eficiente e interativa. O portal simplifica o fluxo de adoção de animais, oferecendo recursos premium de gerenciamento, acessibilidade e interatividade em tempo real.

---

## 🌟 Funcionalidades Principais

*   **👥 Perfis de Usuário Adaptados**:
    *   **ONGs e Protetores**: Podem cadastrar animais, anexar prontuários de vacinação, marcar pets como adotados (movendo-os para o histórico) e gerenciar contatos de interessados.
    *   **Adotantes**: Podem favoritar pets, se candidatar para adoções, ver notificações e interagir diretamente com os responsáveis.
*   **📊 Estatísticas Dinâmicas e Contadores Reais**: A página inicial conta com estatísticas integradas diretamente com o banco de dados SQLite, atualizando o número de pets protegidos, candidaturas e animais adotados.
*   **🎠 Carrossel Infinito de Animais**:
    *   Exposição animada de pets disponíveis para adoção.
    *   Carrossel exclusivo para "**Últimos Adotados**", mostrando os pets que já encontraram um lar amoroso.
*   **💬 Chat em Tempo Real**: Sistema de mensagens para conectar adotantes e protetores diretamente na plataforma com **filtro automático de profanidades/palavrões**.
*   **🔔 Central de Notificações**: Painel integrado que notifica os usuários quando um pet é favoritado, quando uma candidatura de adoção é enviada, ou quando novas mensagens são recebidas.
*   **🩺 Prontuário de Vacinação Digital**: Controle semafórico do status das vacinas do animal:
    *   🟢 **Em dia**: Vacinas atualizadas.
    *   🟡 **Vence em breve**: Faltam menos de 30 dias para a próxima dose.
    *   🔴 **Atrasada**: Dose pendente expirada.
*   **🛡️ Upload Seguro de Imagens**: Validação dupla (cliente com JavaScript e servidor com Python) limitando o tamanho das fotos de cadastro a **5MB**.
*   **♿ Acessibilidade Completa**:
    *   Controles de tamanho de fonte (A+ e A-).
    *   Alternância entre Tema Escuro e Tema Claro.
    *   **Modo de Alto Contraste** para pessoas com baixa visão.
    *   Foco de teclado (`Tab`) destacado visualmente em vermelho.
    *   Integração com o widget do **VLibras**.
*   **🖥️ Design 100% Responsivo**: Layout otimizado para celulares, tablets e computadores, garantindo usabilidade máxima sem cortes de imagens ou vazamentos horizontais.

---

## 🛠️ Tecnologias Utilizadas

*   **Back-End**: Python 3.x, Flask, Flask-SQLAlchemy (ORM), Flask-Login, Flask-Migrate
*   **Banco de Dados**: SQLite (Rápido e sem dependências externas para desenvolvimento local)
*   **Front-End**: HTML5, CSS3 (Custom Styling, Glassmorphism, HSL tailors), Vanilla JavaScript
*   **Iconografia**: FontAwesome v6
*   **Tipografia**: Outfit (Google Fonts)

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o Python 3 instalado em seu computador.

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/sistema-doacao-animais.git
cd sistema-doacao-animais
```

### 2. Criar e Ativar o Ambiente Virtual
No Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
No macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Inicializar e Semear o Banco de Dados
Para criar a estrutura de tabelas SQLite e injetar os dados de teste (como os pets Mingau, Pipoca, Luna, Thor e vacinas de demonstração), execute o script de inicialização do banco:
1. Abra o navegador em `http://127.0.0.1:5000/init-db` (após iniciar o servidor).
2. O banco será limpo e recriado com dados premium de demonstração prontos para testes.

### 5. Iniciar o Servidor Flask
```bash
python app.py
```
O portal estará disponível no endereço: `http://127.0.0.1:5000`

---

## 🔒 Credenciais de Teste (Administrador/ONG Padrão)
Após rodar `/init-db`, você pode utilizar as seguintes credenciais para testar as permissões de ONG:
*   **E-mail**: `admin@doapet.com`
*   **Senha**: `admin123`

---

## 📂 Estrutura do Banco de Dados (Models)

*   `User`: Armazena dados cadastrais de Adotantes, ONGs e Protetores (Nome, E-mail, CPF, Whatsapp, Tipo de conta e Senha criptografada).
*   `Animal`: Cadastro dos pets contendo nome, espécie, porte, sexo, tags de personalidade, foto, status (`Disponivel`, `Negociacao` ou `Doado`) e referência ao criador.
*   `Vacina`: Registro de vacinas vinculadas aos animais, contendo a data de aplicação e da próxima dose para o controle semafórico.
*   `Candidatura`: Acompanhamento de propostas de adoção (`Pendente`, `Aprovado`, `Recusado`).
*   `Favorito`: Associações de pets favoritados por usuários adotantes.
*   `Mensagem`: Histórico de mensagens trocadas via chat privado.
*   `Notificacao`: Alertas gerados ao usuário sobre interações (favoritos, candidaturas e conversas).
*   `LogAcao`: Registro e auditoria de ações importantes no sistema (criações, deleções, logins, etc.).

https://nicolasblf.pythonanywhere.com/
