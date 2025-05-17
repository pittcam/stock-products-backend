from flask import Flask, request, jsonify, json
from flask_cors import CORS
from redis_client import guardar_en_cache, obtener_de_cache, r
from productos_data import productos
import json

app = Flask(__name__)
CORS(app)


@app.route('/productos', methods=['GET'])
def get_productos():
    cache = obtener_de_cache('productos')
    if cache:
        return jsonify(cache)

    guardar_en_cache('productos', productos)
    return jsonify(productos)


@app.route('/registrar-venta', methods=['POST'])
def registrar_venta():
    data = request.get_json()
    cliente = data.get('cliente')
    items = data.get('items')

    if not cliente or not items:
        return jsonify({"error": "Falta cliente o items"}), 400

    productos_actuales = obtener_de_cache('productos')
    if not productos_actuales:
        return jsonify({"error": "No hay productos en caché"}), 500

    productos_dict = {p['id']: p for p in productos_actuales}

    for item in items:
        producto = productos_dict.get(item['id_producto'])
        if not producto:
            return jsonify({"error": f"Producto ID {item['id_producto']} no existe"}), 400
        if producto['stock'] < item['cantidad']:
            return jsonify({"error": f"Stock insuficiente para {producto['nombre']}"}), 400
        producto['stock'] -= item['cantidad']

    guardar_en_cache('productos', list(productos_dict.values()))

    venta = {
        "cliente": cliente,
        "items": items,
    }

    # Guarda en lista de historial
    r.lpush("ventas", json.dumps(venta))

    return jsonify({"comprobante": f"Venta registrada para {cliente}."})

@app.route('/historial-ventas', methods=['GET'])
def historial_ventas():
    ventas = r.lrange("ventas", 0, -1)
    return jsonify([json.loads(v) for v in ventas])


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
