import redis
import json
import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

def guardar_en_cache(clave, datos):
    r.set(clave, json.dumps(datos))

def obtener_de_cache(clave):
    valor = r.get(clave)
    return json.loads(valor) if valor else None
