from flask import Flask, Response, request
from extractor import ExtractorJuanito
import json

app = Flask(__name__)

# Método viejo que podría sacar pero dejo por las dudas para después :p
@app.route("/precios_juanito")
def precios_juanito():
    extractor = ExtractorJuanito()
    granel = extractor.obtener_datos_sql("juanito_granel")
    envasados = extractor.obtener_datos_sql("juanito_envasados")
    datos = {"granel": granel, "envasados": envasados}
    payload = json.dumps(datos)
    response = Response(payload)
    response.headers["Access-Control-Allow-Origin"] = "*"
    print(response.headers)
    return response

@app.route("/api/productos", methods=["GET", "POST"])
def productos():
    if request.method == "GET":
        extractor = ExtractorJuanito()
        tablas = request.args.getlist("productos")
        precio_minoritario = request.args.get("precio_minoritario", default=False, type=bool)
        print(tablas)
        datos = {}
        for tabla in tablas:
            nombre = tabla
            datos[nombre] = extractor.obtener_datos_sql(tabla, precio_minoritario)
        payload = json.dumps(datos)
        response = Response(payload)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        # En un futuro querría implementar un endpoint donde pueda subir los precios actualizados cada mes.
        # Antes de hacerlo, tendría que ver si van varios meses en los que los parámetros que uso
        # para importar los datos de los PDFs de precios funcionan.
        return Response(status=403)

# Método viejo que podría sacar pero dejo por las dudas para después :P
@app.route("/consumando")
def consumando():
    extractor = ExtractorJuanito(palabras_excluídas="chocolate, mix, praline")
    precios = extractor.obtener_datos_sql("juanito_granel")
    filtrados = extractor.filtrar_tabla("productos.txt", tabla=precios)
    payload = json.dumps(filtrados)
    response = Response(payload)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/api/armar_pedido", methods=["POST"])
def armar_pedido():
    data = request.form
    print(data)
    tienda = request.args.get("tienda", type=str)
    if not tienda:
        return Response("No se especificó una base de datos en el request.", status=400)
    elif "burbuja" in tienda:
        tablas = ["burbuja_latina"]
    elif "juanito" in tienda:
        tablas = ["juanito_granel", "juanito_envasados"]
    else:
        return Response("No se encontró la base de datos a la que se refiere en el request",
                        status=404)

    extractor = ExtractorJuanito()
    extractor.generar_pedido(data, tablas)
    response = Response("Chequeado")
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
