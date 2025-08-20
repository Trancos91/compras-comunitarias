from typing import IO
from collections.abc import Sequence
from os import path
import re
import json
import sqlite3
import pdfplumber
import gspread
from fpdf import FPDF, FontFace
from unidecode import unidecode

class ExtractorJuanito:
    def __init__(self, pdf=None, palabras_excluídas=None, 
                 productos_buscados=None, categorías_excluídas=None, 
                 crop_todas=None, crop_primera=None, table_settings={},
                 chequear_sinstock=True, agregar_id=False, columna_categoría=1,
                 precio_minoritario=False):
        self.pdf = self.procesar_pdf(pdf, table_settings=table_settings, agregar_id=agregar_id,
                                     crop_todas=crop_todas, crop_primera=crop_primera,
                                     chequear_sinstock=chequear_sinstock, precio_minoritario=precio_minoritario,
                                     columna_categoría=columna_categoría) if pdf else None
        if palabras_excluídas: self.palabras_excluídas = self.path_o_lista(palabras_excluídas)
        if productos_buscados: self.productos_buscados = self.path_o_lista(productos_buscados)
        if categorías_excluídas:
            self.categorías_excluídas = self.path_o_lista(categorías_excluídas)
        else:
            self.categorías_excluídas = []

        self.tiendas = ["juanito", "burbuja"]


    def path_o_lista(self, ingreso):
        print("Ejecutando path_o_lista")
        if path.exists(path.normpath(ingreso)):
            print("Encontré el path")
            with open(ingreso) as file:
                listado = [x.strip() for x in file.read().split(",")]
            return listado
        else:
            if "," in ingreso:
                print("Detectada una lista de elementos")
                listado = [x.strip() for x in ingreso.split(",")]
                return listado
            else:
                raise FileNotFoundError("Parece que el valor ingresado no es ni una lista de elementos"
                                        " ni un archivo que la contenga.")

    def armar_listado_productos_buscados(self, archivo: None|IO=None):
        """
        Recibe un archivo y lo procesa, convirtiéndolo en una lista (delimitadores ","),
        transformándolo en lower case y eliminando plurales (eliminando la "s" en palabras que terminan con "s").
        Si no recibe un archivo específico, revisa si ya existe el listado como variable del objeto.
        """

        if not archivo:
            if self.productos_buscados:
                productos = self.productos_buscados
            else:
                raise Exception("No indicaste un listado de productos buscados")
        else:
            productos = archivo.read().split(",")

        def eliminar_plural(término):
            palabras = término.split(" ")
            singulares = [palabra[:-1] if palabra.endswith("s") else palabra for palabra in palabras]
            modificada = " ".join(singulares)
            return modificada

        for index, producto in enumerate(productos.copy()):
            productos[index] = unidecode(producto.lower())

        productos = [eliminar_plural(producto) for producto in productos.copy()]
        return productos


    def procesar_pdf(self, archivo, table_settings: dict | None=None,
                     crop_primera: tuple[float, float, float, float] | None=None,
                    crop_todas: tuple[float, float, float, float] | None=None,
                     chequear_sinstock=True, agregar_id=False, columna_categoría=1,
                     precio_minoritario=False):
        """
        Obtiene un archivo PDF y lo convierte con pdfplumber. Agrega las categorías de cada producto
        como una última columna a la tabla e ignora los "headers" seccionales.
        Los defaults son para el formato de Juanito.
        Precio Minoritario: Si es True, formatea la anteúltima row andemás de la última
        """

        if agregar_id: id = 1
        # Abre el archivo con pdfplumber
        pdf = pdfplumber.open(archivo)
        # Obtiene todas las páginas
        páginas = pdf.pages
        if crop_primera:
            páginas[0] = páginas[0].crop(crop_primera, relative=True)
        if crop_todas:
            for página in páginas:
                página = página.crop(crop_todas, relative=True)

        tabla_completa = []

        # Arma una tabla completa concatenando todas las páginas
        for página in páginas:
            tabla_completa += página.extract_table(table_settings=table_settings)


        tabla_parseada = []

        row_minoritaria = None
        header_precio = None
        header_precio_minoritario = None
        # Elimina los headers seccionales, y los agrega como valor de la última columna de cada fila.
        for row in tabla_completa:
            if row[1] == None: continue
            precio_parseado = row[-1].replace(" ", "")
            precio_parseado = precio_parseado.replace("$", "")
            precio_parseado = precio_parseado.replace(".", "")
            precio_parseado = precio_parseado.replace(",", "")
            precio_parseado = precio_parseado.replace("-", "")
            if precio_minoritario:
                row[-2] = row[-2].replace(" ", "")
                row[-2] = row[-2].replace("$", "")
                row[-2] = row[-2].replace(".", "")
                row[-2] = row[-2].replace(",", "")
                row[-2] = row[-2].replace("-", "")
                #print(row[-2])


            if chequear_sinstock:
                #if row[len(row) - 1] == 'SINSTOCK' or row[len(row) - 1] == '': 
                if precio_parseado == 'SINSTOCK' or precio_parseado == '': 
                    print("Dio SinStock")
                    continue

            if precio_parseado or (not row[-1] and not row[-2]):
                try:
                    int(precio_parseado)
                except ValueError:
                    categoría = row[columna_categoría].lower()
                    if row[-1].lower() != categoría:
                        header_precio = row[-1].lower()
                        header_precio = header_precio.replace("precio", "")
                        header_precio = header_precio.replace("unidad", "").strip()
                        header_precio = " " + header_precio
                    else:
                        header_precio = None
                    if precio_minoritario:
                        header_precio_minoritario = row[-2].lower()
                        header_precio_minoritario = header_precio_minoritario.replace("precio", "")
                        header_precio_minoritario = header_precio_minoritario.replace("unidad", "").strip()
                        header_precio_minoritario = " " + header_precio_minoritario
                    else:
                        header_precio_minoritario = None
                    print(categoría)
                    print(header_precio)
                    print(header_precio_minoritario)
                    continue

            row[-1] = precio_parseado

            if not agregar_id:
                try:
                    prueba = int(row[0])
                except ValueError:
                    continue
                except TypeError:
                    print("Casilla 0 fue none, se va a igorar este ítem.")
                    continue
            if row:
                row_parseada = []
                row_minoritaria = []
                if precio_minoritario:
                    if row[-1]:
                        row_parseada.append(row[0])
                        if not agregar_id:
                            row_parseada.append(row[1])
                        row_parseada.append(row[-1])
                        row_parseada.append(categoría)
                        row_parseada[-3] = row_parseada[-3] + header_precio if header_precio else row_parseada[-3]
                    if row[-2]:
                        row_minoritaria.append(row[0])
                        if not agregar_id:
                            row_minoritaria.append(row[1])
                            row_minoritaria[0] = row_minoritaria[0] + "m"
                        row_minoritaria.append(row[-2])
                        row_minoritaria.append(categoría)
                        row_minoritaria[-3] = row_minoritaria[-3] + header_precio_minoritario if header_precio_minoritario else row_minoritaria[-3]
                else:
                    if row[-1]:
                        row_parseada.append(row[0])
                        if not agregar_id:
                            row_parseada.append(row[1])
                        row_parseada.append(row[-1])
                        row_parseada.append(categoría)
                        row_parseada[-3] = row_parseada[-3] + header_precio if header_precio else row_parseada[-3]
                if agregar_id: 
                    if row_parseada:
                        row_parseada.insert(0, str(id))
                        id += 1
                    if row_minoritaria:
                        row_minoritaria.insert(0, str(id))
                        id += 1
                if row_parseada:
                    tabla_parseada.append(row_parseada)
                if row_minoritaria:
                    tabla_parseada.append(row_minoritaria)

        try:
            tabla_parseada.sort(key=lambda x: int(x))
        except:
            pass
        return tabla_parseada

    def filtrar_tabla(self, archivo, tabla=None):
        """
        Devuelve una lista de listas(como el pdf procesado) únicamente con los productos indicados
        """
        with open(archivo, "r") as file:
            productos = self.armar_listado_productos_buscados(file)

        if not tabla: tabla = self.pdf
        if not tabla: raise Exception("El método filtrar_tabla no recibió ninguna tabla de argumento,"
                                      " y no hay variable pdf en la clase.")
        # Crea una tabla sin tildes ni mayúsculas del pdf
        tabla_unidecode = [unidecode(x[1].lower()) for x in tabla]
        print(tabla_unidecode)

        # Tabla con únicamente los resultados seleccionados
        tabla_filtrada = []

        for index, producto in enumerate(tabla):
            if any((x in tabla_unidecode[index] for x in productos)) and not any((x in tabla_unidecode[index] for x in self.palabras_excluídas)):
                tabla_filtrada.append(producto)
        return tabla_filtrada

    def crear_pdf(self, tabla, nombre):
        """
        Genera un PDF utilizando el formato de Juanito a partir de la tabla procesada y actualizada.
        El último ítem de cada lista(row) que recibe debería ser una categoría del producto para agruparlo.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        categorías = {}
        for row in tabla:
            if row[-1] not in categorías.keys():
                categorías[row[-1]] = []
            categoría = row.pop(-1)
            categorías[categoría].append(row)

        with pdf.table(text_align="left") as table:
            row = table.row()
            estilo_refes = (224, 224, 224)
            for categoría in categorías.keys():
                row = table.row()
                row.cell(categoría.capitalize(),
                         style=FontFace(emphasis="BOLD", size_pt=16, fill_color=(192, 192, 192)), 
                         colspan=len(categorías[categoría][0]), align="center")
                row = table.row()
                row.cell("ID", style=FontFace(fill_color=estilo_refes), align="center")
                row.cell("Producto", style=FontFace(fill_color=estilo_refes), align="center")
                if len(categorías[categoría][0]) == 4:
                    row.cell("Precio x 100g", style=FontFace(fill_color=estilo_refes), align="center")
                    row.cell("Precio x kg", style=FontFace(fill_color=estilo_refes), align="center")
                else:
                    row.cell("Precio", style=FontFace(fill_color=estilo_refes), align="center")
                for data_row in categorías[categoría]:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)

        pdf.output(nombre)

    def escribir_sql(self, contenido, tabla_sql):
        """
        Recibe una tabla(una lista de listas) y la escribe a la base de datos de sql
        """
        try:
            conexion = sqlite3.connect("compras_comunitarias.db")
            cur = conexion.cursor()
            print("Conectado a la base de datos")
            print(f"Acá una columna random: {contenido[2]}")
            print(f"Row 0: {contenido[0]}")
            if len(contenido[0]) == 5:
                cur.execute(f"CREATE TABLE IF NOT EXISTS {tabla_sql} (id, nombre, precio_minoritario, precio, categoria);")
            elif len(contenido[0]) == 4:
                cur.execute(f"CREATE TABLE IF NOT EXISTS {tabla_sql} (id, nombre, precio, categoria);")
            else:
                raise Exception("La tabla que ingresaron no tenía ni 4 ni 5 columnas; no cuadra con el formato de juanito")
            cur.execute(f"DELETE FROM {tabla_sql}")
            print(f"Tabla {tabla_sql} truncada")
            #if len(contenido[0]) == 5:
            #    insert_con_parametros = f"""INSERT INTO {tabla_sql} (id, nombre, precio_minoritario, precio, categoria) VALUES (?, ?, ?, ?, ?);"""
            #elif len(contenido[0]) == 4:
            #    insert_con_parametros = f"""INSERT INTO {tabla_sql} (id, nombre, precio, categoria) VALUES (?, ?, ?, ?);"""
            #else:
            #    raise Exception("La tabla que ingresaron no tenía ni 4 ni 5 columnas; no cuadra con el formato de juanito")
            insert_con_parametros = f"""INSERT INTO {tabla_sql} (id, nombre, precio, categoria) VALUES (?, ?, ?, ?);"""
            for row in contenido:
                if len(row) == 4:
                    cur.execute(insert_con_parametros, row)
                else:
                    print("Row sin 4 columnas:")
                    print(row)
            conexion.commit()
            print("Escrita la nueva data a la tabla")
            cur.close()
        except sqlite3.Error as error:
            print("Hubo un error al intentar escribir la data a la base de datos", error)
        finally:
            if conexion:
                conexion.close()
                print("Cerrada la conexión a la base de datos")

    def obtener_datos_sql(self, tabla, precio_minoritario=False):
        """
        Obtiene los datos de la base de datos indicada como lista de listas(tabla)
        """
        datos = []
        try:
            conexion = sqlite3.connect("compras_comunitarias.db")
            cur = conexion.cursor()
            print("Conectado a la base de datos")
            if not precio_minoritario:
                for row in cur.execute(f"SELECT id, nombre, precio, categoria FROM {tabla}"):
                    datos.append([row[0], row[1], row[2], row[3]])
                print("Obtenidos los datos")
            else:
                for row in cur.execute(f"SELECT id, nombre, precio_minoritario, precio, categoria FROM {tabla}"):
                    datos.append([row[0], row[1], row[2], row[3], row[4]])
                print("Obtenidos los datos")
            cur.close()
        except sqlite3.Error as error:
            print("Hubo un error al intentar escribir la data a la base de datos", error)
        finally:
            if conexion:
                conexion.close()
                print("Cerrada la conexión a la base de datos")
        return datos

    def generar_pedido(self, pedido: dict, tablas: list[str]):
        """
        A partir de un diccionario con IDs de productos y cantidades, genera
        un pedido para la persona cuyo nombre viene incluída en dicho diccionario.
        Si el producto ya figura en el sheet, lo agrega en una nueva columna de dicha persona.
        Si no existía el producto, además de generar la columna con el pedido de dicha persona,
        genera un row con el nuevo producto y su valor.
        """
        try:
            pedido = dict(pedido)
        except:
            raise ValueError("El pedido ingresado no se puede convertir a diccionario")
        nombre = pedido.pop("nombre")
        print(f"Pedido: {pedido}")
        tienda_actual = None
        for tienda in self.tiendas:
            if any(tienda in x for x in tablas):
                tienda_actual = re.compile(tienda + ".*", re.IGNORECASE)
        if not tienda_actual:
            raise ValueError("Deberíamos recibir una tienda válida a la que agregar")

        def obtener_indice_producto(producto):
            """
            Chequea si existe el producto. Si existe, devuelve el índice.
            Si no, crea una row para dicho producto y devuelve el índice
            """
            celda = sheet.find(producto[1])
            col_precio = sheet.find("Precio", in_row=1).col
            if celda:
                return celda.row
            else:
                row_tienda = sheet.find(tienda_actual, case_sensitive=False).row + 1
                sheet.insert_row([producto[1]], index=row_tienda)
                sheet.update_cell(row_tienda, col_precio, producto[2].replace("$", "").strip())
                sheet.update_cell(row_tienda, 2, f"=sum(indirect('d{row_tienda}:{row_tienda}'))")
                return row_tienda

        def obtener_col_persona(nombre):
            """
            Chequea si la persona que hace el pedido tiene una columna.
            Si la tiene, agrega sus pedidos ahí. Si no, crea una y arma
            su pedido en esa columna.
            """
            celda = sheet.find(nombre, in_row=1, case_sensitive=False)
            totales = sheet.find("Totales", in_column=1).row
            if celda:
                return celda.col
            else:
                sheet.insert_cols([[nombre]], 4)
                sheet.update_cell(totales, 4, f"=sum(arrayformula(d2:d{totales-1}*c2:c{totales-1}))")
                return 4

        def obtener_productos_pedido(pedido):
            """
            Obtiene los productos específicos en el dict del pedido.
            Devuele una tupla con id, producto, precio y cantidad pedida.
            """
            conexion = sqlite3.connect("compras_comunitarias.db")
            cur = conexion.cursor()
            productos = []
            try:
                for key in pedido:
                    mayorista = False
                    for tabla in tablas:
                        #if "burbuja" in tabla and "mayorista" in key:
                        #    key_a_usar = key.replace("mayorista", "")
                        #    mayorista = True
                        #    query_precio = "precio"
                        #elif "burbuja" in tabla:
                        #    key_a_usar = key
                        #    query_precio = "precio_minoritario"
                        #else:
                        #    key_a_usar = key
                        #    query_precio = "precio"
                        resultado = cur.execute(f"SELECT id, nombre, precio FROM {tabla} WHERE id = ?", (key,)).fetchone()
                        print(resultado)
                        if resultado:
                            id, producto, precio = resultado
                            break
                    if mayorista: producto += "ENVASE DE 5 LITROS"
                    cantidad = pedido[key]
                    if id and producto and precio:
                        productos.append((id, producto, precio, cantidad))
            except sqlite3.Error as error:
                print("Hubo un error al intentar escribir la data a la base de datos", error)
            finally:
                if cur:
                    cur.close()
                if conexion:
                    conexion.close()
                    print("Cerrada la conexión a la base de datos")
            return productos
        
        # Genera la lista de productos a agregar
        productos = obtener_productos_pedido(pedido)

        with open("secretos/url_sheet.txt") as file:
            url_sheet = file.read().strip()
        gc = gspread.service_account(filename="secretos/credentials.json")
        # Abriendo el 'workbook'(colección de worksheets) con el que vamos a trabajar
        try:
            workbook = gc.open_by_url(url_sheet)
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(e)
        
        sheet = workbook.worksheet("Sheet1")
        col_pedido = obtener_col_persona(nombre)

        for producto in productos:
            row = obtener_indice_producto(producto)
            # Agrega el producto a la columna del pedido
            sheet.update_cell(row, col_pedido, producto[3])


if __name__ == "__main__":
    #extractor = ExtractorJuanito("precios_envasado.pdf", vlines=vlines)
    #tabla = extractor.pdf
    #extractor.escribir_sql(tabla, "juanito")
    #extractor.crear_pdf(tabla, "tabla_envasado.pdf")
    extractor = ExtractorJuanito()
    pedido = {
        "nombre": "in",
        "310": 2.5,
    }
    tablas = ["juanito_granel", "juanito_envasados"]
    extractor.generar_pedido(pedido, tablas)

