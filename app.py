from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Oct081098#@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("home.html")

# Definição dos modelos do banco de dados
class Cliente(db.Model):
    __tablename__ = 'clientes'
    CNPJ = db.Column(db.String, primary_key=True)
    Primeiro_Nome = db.Column(db.String)
    Segundo_Nome = db.Column(db.String)
    Email = db.Column(db.String)
    Telefone = db.Column(db.String)
    Estado = db.Column(db.String)
    Cidade = db.Column(db.String)
    Bairro = db.Column(db.String)
    Rua = db.Column(db.String)
    Numero = db.Column(db.String)

class Obra(db.Model):
    __tablename__ = 'obras'
    OS = db.Column(db.String, primary_key=True)
    Primeiro_Nome_Contato = db.Column(db.String)
    Segundo_Nome_Contato = db.Column(db.String)
    Valor = db.Column(db.Float)
    Estado_Obra = db.Column(db.String)
    Cidade_Obra = db.Column(db.String)
    Bairro_Obra = db.Column(db.String)
    Rua_Obra = db.Column(db.String)
    Numero_Obra = db.Column(db.String)
    CNPJ_Cliente = db.Column(db.String, db.ForeignKey('clientes.CNPJ'), nullable=False)

class Compra(db.Model):
    __tablename__ = 'compras'
    Ordem_de_Compras = db.Column(db.String, primary_key=True)
    Obra_OS = db.Column(db.String, db.ForeignKey('obras.OS'), nullable=False)
    Materia_prima = db.Column(db.String)
    Consumiveis = db.Column(db.String)
    Miscelanea = db.Column(db.String)

# Função para remover a formatação de moeda do valor antes de salvar no banco
def formatar_valor(valor):
    # Remove "R$", espaços e troca vírgula por ponto
    valor_formatado = re.sub(r'[R$\s]', '', valor)  # Remove "R$", espaços
    valor_formatado = valor_formatado.replace('.', '').replace(',', '.')
    return float(valor_formatado)

# Rota para a página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Dados do Cliente
        cnpj = request.form['cnpj']
        primeiro_nome = request.form['primeiro_nome']
        segundo_nome = request.form['segundo_nome']
        email = request.form['email']
        telefone = request.form['telefone']
        estado = request.form['estado']
        cidade = request.form['cidade']
        bairro = request.form['bairro']
        rua = request.form['rua']
        numero = request.form['numero']

        # Dados da Obra
        os = request.form['os']
        primeiro_nome_contato = request.form['primeiro_nome_contato']
        segundo_nome_contato = request.form['segundo_nome_contato']
        valor = request.form['valor']  # Valor com formatação "R$"
        estado_obra = request.form['estado_obra']
        cidade_obra = request.form['cidade_obra']
        bairro_obra = request.form['bairro_obra']
        rua_obra = request.form['rua_obra']
        numero_obra = request.form['numero_obra']

        # Dados da Compra
        ordem_compra = request.form['ordem_compra']  # Captura da ordem de compra
        materia_prima = request.form['materia_prima']
        consumiveis = request.form['consumiveis']
        miscelanea = request.form['miscelanea']

        # Formata o valor da obra para formato numérico
        valor_formatado = formatar_valor(valor)

        try:
            # Verifica se o cliente já existe
            cliente_existente = Cliente.query.filter_by(CNPJ=cnpj).first()

            # Se o cliente não existir, cria um novo
            if not cliente_existente:
                novo_cliente = Cliente(CNPJ=cnpj, Primeiro_Nome=primeiro_nome, Segundo_Nome=segundo_nome,
                                       Email=email, Telefone=telefone, Estado=estado, Cidade=cidade,
                                       Bairro=bairro, Rua=rua, Numero=numero)
                db.session.add(novo_cliente)
            else:
                # Atualiza os dados do cliente, se necessário
                cliente_existente.Estado = estado
                cliente_existente.Cidade = cidade
                # Pode-se atualizar outros campos aqui se necessário

            db.session.commit()  # Confirma a inserção ou atualização do cliente

            # Cadastra a obra
            nova_obra = Obra(OS=os, Primeiro_Nome_Contato=primeiro_nome_contato,
                             Segundo_Nome_Contato=segundo_nome_contato,
                             Valor=valor_formatado, Estado_Obra=estado_obra, Cidade_Obra=cidade_obra,
                             Bairro_Obra=bairro_obra, Rua_Obra=rua_obra, Numero_Obra=numero_obra, CNPJ_Cliente=cnpj)
            db.session.add(nova_obra)
            db.session.commit()  # Confirma a inserção da obra

            # Cadastra a compra vinculada à obra
            nova_compra = Compra(Obra_OS=os, Ordem_de_Compras=ordem_compra, Materia_prima=materia_prima,
                                 Consumiveis=consumiveis, Miscelanea=miscelanea)
            db.session.add(nova_compra)
            db.session.commit()  # Confirma a inserção da compra

            return redirect(url_for('cadastro'))
        except Exception as e:
            db.session.rollback()  # Desfaz as alterações em caso de erro
            return f"Ocorreu um erro: {str(e)}"

    return render_template('cadastro.html')

# Rota para a página de consulta
@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if request.method == 'POST':
        cnpj = request.form['cnpj']  # O CNPJ é recebido com pontuação
        os = request.form['os']  # A OS informada pelo usuário

        print(f"CNPJ recebido: {cnpj}")  # Verifica o CNPJ recebido no backend

        # Busca o cliente pelo CNPJ
        cliente = Cliente.query.filter_by(CNPJ=cnpj).first()
        print(f"Resultado da consulta (cliente): {cliente}")  # Verifica o resultado da busca no banco

        # Se o cliente for encontrado, busca as obras associadas ao CNPJ
        obras = []
        compras = {}
        if cliente:
            if os:
                # Se a OS for informada, filtra obras pela OS
                obras = Obra.query.filter_by(OS=os, CNPJ_Cliente=cnpj).all()
                print(f"Resultado da consulta (obras para a OS): {obras}")  # Verifica as obras relacionadas à OS
                # Busca compras relacionadas apenas às obras filtradas
                for obra in obras:
                    obra_compras = Compra.query.filter_by(Obra_OS=obra.OS).all()
                    if obra_compras:
                        compras[obra.OS] = obra_compras  # Agrupa compras por OS
            else:
                # Se não houver OS, busca todas as obras do cliente
                obras = Obra.query.filter_by(CNPJ_Cliente=cnpj).all()
                print(f"Resultado da consulta (todas as obras): {obras}")  # Verifica todas as obras

                # Busca compras relacionadas a todas as obras do CNPJ
                for obra in obras:
                    obra_compras = Compra.query.filter_by(Obra_OS=obra.OS).all()
                    if obra_compras:
                        compras[obra.OS] = obra_compras  # Agrupa compras por OS

            return render_template('consulta.html', cliente=cliente, obras=obras, compras=compras)
        else:
            return render_template('consulta.html', mensagem='Cliente não encontrado')

    return render_template('consulta.html')

# Função para limpar todas as tabelas do banco de dados
def limpar_banco():
    db.session.query(Compra).delete()
    db.session.query(Obra).delete()
    db.session.query(Cliente).delete()
    db.session.commit()

# Rota para limpar o banco de dados
@app.route('/limpar_banco')
def limpar():
    limpar_banco()
    return 'Banco de dados limpo com sucesso.'

# Rota para verificar se o CNPJ já está cadastrado
@app.route('/verificar_cnpj')
def verificar_cnpj():
    cnpj = request.args.get('cnpj').strip()  # CNPJ com máscara
    cliente = Cliente.query.filter_by(CNPJ=cnpj).first()  # Busca pelo CNPJ com máscara

    if cliente:
        return jsonify({
            'cadastrado': True,
            'primeiro_nome': cliente.Primeiro_Nome,
            'segundo_nome': cliente.Segundo_Nome,
            'email': cliente.Email,
            'telefone': cliente.Telefone,
            'estado': cliente.Estado,
            'cidade': cliente.Cidade,
            'bairro': cliente.Bairro,
            'rua': cliente.Rua,
            'numero': cliente.Numero
        })
    else:
        return jsonify({'cadastrado': False})




    # API's
    @app.route('/api/consulta-obra/<cnpj>', methods=['GET'])
    def consulta_obra(cnpj):
        # Remover caracteres especiais do CNPJ (como pontos, barras e traços)
        cnpj = re.sub(r'\D', '', cnpj)

        # Procurar o cliente pelo CNPJ
        cliente = Cliente.query.filter_by(CNPJ=cnpj).first()

        if not cliente:
            return jsonify({"error": "CNPJ não encontrado"}), 404

        # Procurar as obras associadas ao cliente
        obras = Obra.query.filter_by(CNPJ_Cliente=cnpj).all()

        if not obras:
            return jsonify({"error": "Nenhuma obra encontrada para este cliente"}), 404

        # Estrutura para armazenar a resposta
        resultado = {
            "cliente": {
                "CNPJ": cliente.CNPJ,
                "nome": f"{cliente.Primeiro_Nome} {cliente.Segundo_Nome}",
                "email": cliente.Email,
                "telefone": cliente.Telefone
            },
            "obras": []
        }

        # Adicionar os dados das obras e itens utilizados
        for obra in obras:
            # Buscar compras relacionadas à obra
            compras = Compra.query.filter_by(Obra_OS=obra.OS).first()

            obra_info = {
                "os": obra.OS,
                "valor": obra.Valor,
                "endereco": {
                    "rua": obra.Rua_Obra,
                    "bairro": obra.Bairro_Obra,
                    "numero": obra.Numero_Obra,
                    "cidade": obra.Cidade_Obra,
                    "estado": obra.Estado_Obra
                },
                "itens_utilizados": {
                    "materia_prima": compras.Materia_prima if compras else "",
                    "consumiveis": compras.Consumiveis if compras else "",
                    "miscelanea": compras.Miscelanea if compras else ""
                }
            }

            resultado["obras"].append(obra_info)

        return jsonify(resultado)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no PostgreSQL
    app.run(debug=True)






