# Consumando - Compras comunitarias

Esta es una aplicación armada así nomás para gestionar el armado de pedidos colectivos a la hora de hacer compras comunitarias.

## Uso principal

En lugar de que cada persona le mande a una persona cada cosa que quiere comprar, y ésta tenga que encargarse de armar un
documento de google sheets en el cual desplegar el total de elementos pedidos y el precio que le corresponde a cada quien pagar,
el programa presenta una interfaz web mediante la cual hacer el pedido y un backend que se encarga de armar dicho sheet.

## Funciones administrativas actuales y futuras

### Importación de PDFs de precios

Además, el backend cuenta con un par de métodos para importar las listas de precios actualizadas de cada mes(que los proveedores
envían como PDFs) utilizando pdfplumber. Falta implementar un endpoint en el cual subir los PDFs para que se importen
automáticamente, pero antes de eso tiene que quedar en claro que los parámetros usados para importar los distintos PDFs que
se están usando ahora funcionan también con sus modificaciones mes a mes, así que por ahora la actualización sería manual mediante
la actualización de la base de datos SQLite.

### Generación de listado de precios

Por ahora irrelevantes, ya que se pueden usar los archivos originales, pero el backend cuenta también con maneras de filtrar los
listados de productos, para situaciones en las que los pedidos que se vayan a coordinar no sean de la totalidad del catálogo
sino de una cantidad limitada de artículos. Para dichos casos, hay un método para generar los PDFs de ese "catálogo limitado",
también bastante verde y simple ya que todavía no sería indispensable.
