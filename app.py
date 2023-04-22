from flask import Flask, request, jsonify
from typing import Optional
from itertools import count
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

server = Flask(__name__)

spec = FlaskPydanticSpec('Flask', title='Rest Api com flask')
spec.register(server)
database = TinyDB(storage=MemoryStorage)
c = count()

class QueryPessoa(BaseModel):
    id: Optional[int] 
    idade: Optional[int] 
    nome: Optional[str] 

class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    idade: int
    nome: str

class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    cont: int

@server.get('/pessoas/')
@spec.validate(query=QueryPessoa,resp=Response(HTTP_200=Pessoas))
def pegar_pessoas():
    query = request.context.query.dict(exclude_none=True)
    pessoas_query = database.search(Query().fragment(query))
    """Busca pessoas no banco de dados"""
    return jsonify(
        Pessoas(
            pessoas=pessoas_query,
            cont=len(pessoas_query)
        ).dict()
    )        

@server.get('/pessoas/<int:id>/')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def pegar_pessoa(id):
    """Busca uma pessoa no banco de dados"""
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa não encontrada!'}    

    return jsonify(pessoa)
    

@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def inserir_pessoa():
    """Insere pessoa no banco de dados."""
    body = request.context.body.dict()
    database.insert(body)
    return body

@server.put('/pessoas/<int:id>/')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))

def altera_pessoa(id):
    """Atualiza uma pessoa no banco de dados"""
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)

@server.delete('/pessoas/<int:id>/')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """Deleta uma pessoa no banco de dados"""
    Pessoa = Query()
    
    database.remove(Pessoa.id == id)
    return jsonify({})
server.run()