# Tareas pendientes

## Backend

- [ ] Escribir un endpoint que reciba un pdf, lo procese, y lo agregue a la base de datos
  - [ ] Escribir un endpoint que devuelva el PDF procesado para ver si extrajo bien los datos
  - [ ] Armar un sistema de autenticación para que no se pueda enviar cualquier cosa
  - [ ] Estructurar el endpoint (o endpoints) de forma que se pueda agregar contenido a una misma base de datos,
        agregar contenido a distintas, o reemplazar una base de datos con otra. Programar de forma que si no existe
        la base de datos elegida, se cree una.
  - [x] Modificar la tabla del sheets para tener varios puntos de compra(juanito, burbuja latina, etc)
  - [x] Modificar el método de generar pedido para que reciba un argumento del lugar al que armaría dicho pedido. Debería
        buscar en el sheets la fila correspondiente a la tienda, sumar uno, y ahí insertar row para armar el pedido.
  - [x] Refactorear el método que recibe IDs? Para que si no las encuentra en una base de datos la busque en otra?
        Esto giraría en torno a armar una gran lista con todas las tiendas: Juanito, burbuja latina y tunas. Si no, páginas
        separadas y listo.

## Frontend

- [x] Pensar el diseño de la lista de ítems: dividimos por peso o unidad a pesar de que estén en la misma lista?
      Cómo podemos integrar múltiples vendedores a un mismo pedido de manera que no se mezclen?
- [ ] Programar cookies que recuerden los pedidos hechos en caso de que se reinicie la página.
- [ ] Cambiar la tipografía de la tabla, por lo menos.
- [ ] Ver de cambiar la tipografía del resto de la página.
- [ ] Modificar URL a la URL del server

## Server

- [ ] Agregar dominio compras.acaballito.lat
- [ ] Configurar Caddy para que sirva la página estática y que redirija al backend en la ruta de api
