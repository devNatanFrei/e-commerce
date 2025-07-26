⚙️ Guia de Instalação e Execução
Siga os passos abaixo para colocar o projeto em funcionamento.

1. Clone o Repositório
Primeiro, clone este repositório para a sua máquina local e navegue até a pasta do projeto.

git clone <URL_DO_SEU_REPOSITORIO>
cd e-commerce


2. Crie e Ative o Ambiente Virtual
O uso de um ambiente virtual (venv) é crucial para isolar as dependências do projeto.

# Cria a pasta 'venv' com o ambiente virtual
python -m venv venv


Agora, ative o ambiente. O comando varia conforme seu sistema operacional:

No Windows (PowerShell):
Pode ser necessário ajustar a política de execução para permitir a ativação de scripts. Execute este comando uma vez como administrador: 
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
Powershell
No macOS/Linux:
# Ativa o ambiente
source venv/bin/activate


💡 Seu terminal deve agora exibir (venv) no início da linha, indicando que o ambiente está ativo.
3. Instale as Dependências
Com o venv ativado, instale todas as bibliotecas necessárias.

Opção A: Instalação Direta (como no log)
pip install django pillow django-crispy-forms crispy-bootstrap4 django-debug-toolbar

Opção B: Usando um Arquivo requirements.txt (Recomendado)
Para facilitar, crie um arquivo requirements.txt:

pip freeze > requirements.txt

Da próxima vez, qualquer pessoa poderá instalar tudo com um único comando:

pip install -r requirements.txt

4. Aplique as Migrações do Banco de Dados
Este comando cria as tabelas no banco de dados (db.sqlite3) que o Django e suas aplicações precisam para funcionar.

python manage.py migrate

5. Execute o Servidor de Desenvolvimento
Tudo pronto! Inicie o servidor local.

python manage.py runserver

O projeto estará acessível em seu navegador no endereço: http://127.0.0.1:8000/
