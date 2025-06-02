from flask import Flask, request, jsonify, json, send_from_directory
from flask_cors import CORS
from redis_client import guardar_en_cache, obtener_de_cache, r
from productos_data import productos
import json
import time
from datetime import datetime

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

    # Extraer todos los campos necesarios
    cliente = data.get('cliente')
    cedula = data.get('cedula', '')
    tipoPago = data.get('tipoPago', 'efectivo')
    items = data.get('items', [])
    id_venta = data.get('id_venta', f"VNT-{int(time.time())}")
    fecha = data.get('fecha', datetime.now().isoformat())
    total = data.get('total', 0)

    if not cliente or not items:
        return jsonify({"error": "Falta cliente o items"}), 400

    productos_actuales = obtener_de_cache('productos')
    if not productos_actuales:
        return jsonify({"error": "No hay productos en caché"}), 500

    productos_dict = {p['id']: p for p in productos_actuales}

    # Verificar stock y actualizar
    for item in items:
        producto_id = item.get('id_producto')
        cantidad = item.get('cantidad', 0)

        producto = productos_dict.get(producto_id)
        if not producto:
            return jsonify({"error": f"Producto ID {producto_id} no existe"}), 400
        if producto['stock'] < cantidad:
            return jsonify({"error": f"Stock insuficiente para {producto['nombre']}"}), 400
        producto['stock'] -= cantidad

    guardar_en_cache('productos', list(productos_dict.values()))

    # Guardar venta completa
    venta = {
        "id_venta": id_venta,
        "fecha": fecha,
        "cliente": cliente,
        "cedula": cedula,
        "tipoPago": tipoPago,
        "items": items,
        "total": total
    }

    # Guarda en lista de historial
    r.lpush("ventas", json.dumps(venta))

    return jsonify({"comprobante": f"Venta registrada para {cliente}."})


@app.route('/historial-ventas', methods=['GET'])
def historial_ventas():
    try:
        # Obtener todas las ventas de Redis
        ventas_raw = r.lrange("ventas", 0, -1)

        if not ventas_raw:
            return jsonify([])

        # Convertir cada venta de JSON string a objeto Python
        ventas = [json.loads(v) for v in ventas_raw]

        # Ordenar por fecha (más reciente primero)
        ventas.sort(key=lambda x: x.get('fecha', ''), reverse=True)

        return jsonify(ventas)
    except Exception as e:
        print(f"Error al obtener historial de ventas: {str(e)}")
        return jsonify({"error": "Error al procesar datos de ventas"}), 500


# Configurar la ruta para servir imágenes
@app.route('/imagenes/<path:filename>')
def serve_image(filename):
    return send_from_directory('imagenes', filename)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
