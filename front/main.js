let precios;
const urlApi = document.currentScript.getAttribute("url-api");
const tiendaApi = document.currentScript.getAttribute("url-post");

const tabla = document.getElementById("tabla-productos");
let rows = [];
var x = [];
let categorías = {};
const filtro = document.getElementById("casilla-filtro");
const listaSeleccionados = document.getElementById("lista-seleccionados");
const form = document.getElementById("formulario-compras");

fetch(urlApi)
  .then((response) => response.json())
  .then((data) => {
    precios = data;
    armarTabla(precios);
    poblarx();
    autocomplete();
    enviarFormulario();
  })
  .catch((error) => {
    console.error("Error cargando JSON:", error);
    let trError = document.createElement("tr");
    let thError = document.createElement("th");
    let trError2 = document.createElement("tr");
    let tdError2 = document.createElement("td");
    thError.textContent =
      "Hubo un error cargando los datos, intentalo nuevamente más tarde.";
    tdError2.textContent =
      "Si el problema persiste, escribile al administrador.";
    trError.append(thError);
    trError2.append(tdError2);
    tabla.append(trError);
    tabla.append(trError2);
  });

/* Función que puebla la tabla; se llama cada vez que se reinicia el filtro con
 * los elementos que sean visibles (a los cuales aplique el filtro buscado)*/
function poblarx() {
  for (categoría in categorías) {
    rowsCatego = categorías[categoría]["rows"];
    for (const row in rowsCatego) {
      if (rowsCatego[row].style.display === "") {
        x.push(rowsCatego[row]);
      }
    }
  }
}
function autocomplete() {
  var currentFocus = -1;
  filtro.addEventListener("input", function (e) {
    currentFocus = -1;
    for (categoría in categorías) {
      rowsCatego = categorías[categoría]["rows"];
      for (const row in rowsCatego) {
        elemento = rowsCatego[row];
        chequeo = String(elemento.textContent).includes(filtro.value);
        chequeoLower = String(elemento.textContent)
          .toLowerCase()
          .includes(filtro.value);
        if (chequeo || chequeoLower) {
          elemento.style.display = "";
          resaltar(elemento.children[0], filtro.value);
        } else {
          elemento.style.display = "none";
        }
      }
    }
    //for (row in rows) {
    //  elemento = rows[row];
    //  chequeo = String(elemento.textContent).includes(filtro.value);
    //  chequeoLower = String(elemento.textContent)
    //    .toLowerCase()
    //    .includes(filtro.value);
    //  if (chequeo || chequeoLower) {
    //    elemento.style.display = "";
    //    resaltar(elemento.children[0], filtro.value);
    //  } else {
    //    elemento.style.display = "none";
    //  }
    //}
    esconderHeaders();
  });

  filtro.addEventListener("keydown", function (e) {
    x = [];
    //if (x) x = x.getElementsByTagName("tr");
    poblarx();
    if (e.keyCode == 40) {
      e.preventDefault();
      /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
      currentFocus++;
      /*and and make the current item more visible:*/
      addActive(x);
    } else if (e.keyCode == 38) {
      e.preventDefault();
      //up
      /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
      currentFocus--;
      /*and and make the current item more visible:*/
      addActive(x);
    } else if (e.keyCode == 13) {
      /*If the ENTER key is pressed, prevent the form from being submitted,*/
      e.preventDefault();
      if (currentFocus > -1) {
        /*and simulate a click on the "active" item:*/
        if (x) x[currentFocus].click();
      }
    }
  });

  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = x.length - 1;
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
    x[currentFocus].scrollIntoView({
      behavior: "smooth",
      block: "end",
      inline: "nearest",
    });
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function resaltar(elem, texto) {
    let HTML = elem.innerHTML;
    if (texto !== "") {
      let regExpBorrar = new RegExp("</?mark>", "gi");
      textContent = elem.innerHTML;
      elem.innerHTML = textContent.replace(regExpBorrar, "");
      let regExp = new RegExp(texto, "gi");
      textContent = elem.innerHTML;
      elem.innerHTML = textContent.replace(regExp, "<mark>$&</mark>");
    } else {
      let regExp = new RegExp("</?mark>", "gi");
      textContent = elem.innerHTML;
      elem.innerHTML = textContent.replace(regExp, "");
    }
  }
  function esconderHeaders() {
    for (const categoría in categorías) {
      let visible = false;
      rowsCatego = categorías[categoría]["rows"];
      for (const row in rowsCatego) {
        if (rowsCatego[row].style.display === "") {
          visible = true;
        }
      }
      let estilo;
      if (visible) {
        estilo = "";
      } else {
        estilo = "none";
      }
      rowsHeaders = categorías[categoría]["headerRows"];
      for (let row in rowsHeaders) {
        rowsHeaders[row].style.display = estilo;
      }
    }
  }
}
/*Parece que acá falta una llave
 * =============================
 */
function armarTabla(precios) {
  let categoría;
  // Construye la tabla por cada categoría, indicando su presentación
  console.log(Object.keys(precios).length);
  if (Object.keys(precios).length > 1) {
    for (const presentacion in precios) {
      iterarLista(precios[presentacion], presentacion);
      appendearRows();
    }
  } else {
    presentacion = Object.keys(precios)[0];
    iterarLista(precios[presentacion], null);
    appendearRows();
  }
  function appendearRows() {
    for (y in categorías) {
      headers = categorías[y]["headerRows"];
      for (header in headers) {
        tabla.append(headers[header]);
      }
      filas = categorías[y]["rows"];
      for (row in filas) {
        tabla.append(filas[row]);
      }
    }
  }
}
function iterarLista(listaPrecios, presentacion) {
  // Arma el diccionario de elementos que formarán la tabla
  if (listaPrecios[0].length == 4) {
    console.log("largo cuatro");
    precio_minoritario = false;
    colHeader = 3;
  } else if (listaPrecios[0].length == 5) {
    console.log("largo cinco");
    precio_minoritario = true;
    colHeader = 4;
  }
  console.log(listaPrecios[0]);
  for (const datum in listaPrecios) {
    // Chequea si la categoría es la misma que en la última fila
    categoría = listaPrecios[datum][colHeader];
    if (!(categoría in categorías)) {
      categorías[categoría] = {};
      categorías[categoría]["headerRows"] = [];
      categorías[categoría]["rows"] = [];
      let trHeader = document.createElement("tr");
      let categoríaCell = document.createElement("th");
      categoríaCell.innerHTML = capitalizar(categoría);
      categoríaCell.setAttribute("colspan", "3");
      let trHeader2 = document.createElement("tr");
      let productoHeader = document.createElement("th");
      let precioHeader = document.createElement("th");
      productoHeader.innerHTML = "Producto";
      precioHeader.innerHTML = "Precio";
      trHeader.append(categoríaCell);
      trHeader2.append(productoHeader);
      trHeader2.append(precioHeader);
      if (presentacion !== null) {
        let formatoHeader = document.createElement("th");
        formatoHeader.innerHTML = "Presentación";
        trHeader2.append(formatoHeader);
      }
      categorías[categoría]["headerRows"].push(trHeader);
      categorías[categoría]["headerRows"].push(trHeader2);
      //tabla.append(trHeader);
      //tabla.append(trHeader2);
    }
    let tr = document.createElement("tr");
    tr.id = listaPrecios[datum][0];
    let precio = document.createElement("td");
    let producto = document.createElement("td");
    producto.classList.add("producto");
    producto.innerHTML = capitalizar(listaPrecios[datum][1]);
    precio.innerHTML = "$" + listaPrecios[datum][2];
    tr.append(producto);
    tr.append(precio);
    if (precio_minoritario == true && listaPrecios[datum][3] !== "") {
      var trMayorista = document.createElement("tr");
      //Agrega "mayorista" al id del tag, así se puede diferenciar de los minoristas
      trMayorista.id = listaPrecios[datum][0] + "mayorista";
      let productoMayorista = document.createElement("td");
      let precioMayorista = document.createElement("td");
      productoMayorista.classList.add("producto");
      productoMayorista.innerHTML =
        capitalizar(listaPrecios[datum][1]) + " <b>5 LITROS</b>";
      precioMayorista.innerHTML = "$" + listaPrecios[datum][3];
      trMayorista.append(productoMayorista);
      trMayorista.append(precioMayorista);
      trMayorista.style.cursor = "pointer";
      console.log(trMayorista);
      categorías[categoría]["rows"].push(trMayorista);
      rows.push(trMayorista);
    }
    if (presentacion !== null) {
      let colPresentacion = document.createElement("td");
      colPresentacion.innerHTML = capitalizar(presentacion.split("_").pop());
      tr.append(colPresentacion);
    }
    tr.style.cursor = "pointer";
    categorías[categoría]["rows"].push(tr);
    rows.push(tr);
    if (precio_minoritario == true) {
    }
    //tabla.append(tr);
    //
    // Código para el funcionamiento de las filas:
    // Con cada click se agrega un nuevo ítem a la lista de
    // elementos seleccionados, con una cruz para eliminarlos
    tr.addEventListener("click", function (e) {
      /*insert the value for the autocomplete text field:*/
      let chequeoHeaders = document.getElementById(
        "th-productos-seleccionados",
      );
      if (chequeoHeaders == null) {
        let trProductosSeleccionados = document.createElement("tr");
        let thProductosSeleccionados = document.createElement("th");
        let thPrecioDelProducto = document.createElement("th");
        let thUnidadDePedido = document.createElement("th");
        let thCantidadPedida = document.createElement("th");
        trProductosSeleccionados.setAttribute(
          "id",
          "th-productos-seleccionados",
        );
        thProductosSeleccionados.textContent = "Producto";
        thPrecioDelProducto.textContent = "Precio";
        thUnidadDePedido.textContent = "Unidad";
        thCantidadPedida.textContent = "Cantidad";
        thProductosSeleccionados.classList.add("td-producto");
        thUnidadDePedido.classList.add("td-unidad");
        thCantidadPedida.classList.add("td-cantidad");
        thPrecioDelProducto.classList.add("td-precio");
        trProductosSeleccionados.append(thProductosSeleccionados);
        trProductosSeleccionados.append(thPrecioDelProducto);
        trProductosSeleccionados.append(thUnidadDePedido);
        trProductosSeleccionados.append(thCantidadPedida);
        listaSeleccionados.append(trProductosSeleccionados);
      }
      let trProducto = document.createElement("tr");
      let tdProducto = document.createElement("td");
      let tdPrecio = document.createElement("td");
      let tdUnidad = document.createElement("td");
      let tdCantidad = document.createElement("td");
      //let li = document.createElement("li");
      //let label = document.createElement("label");
      let formulario = document.createElement("input");
      //let spanPresentacion = document.createElement("span");
      let btnBorrar = document.createElement("span");
      let step;
      let pattern;
      if (
        presentacion &&
        presentacion.includes("granel") &&
        this.id.includes("m")
      ) {
        tdUnidad.textContent = "100 gr";
        step = 0.25;
      } else if (presentacion && presentacion.includes("granel")) {
        tdUnidad.textContent = "Kg.";
        step = 0.05;
      } else {
        tdUnidad.textContent = "unidad/es";
        step = 1;
        pattern = "[0-9]+";
      }
      btnBorrar.textContent = "❌";
      btnBorrar.style.cursor = "pointer";
      //p.setAttribute("display", "inline-block");
      formulario.setAttribute("type", "number");
      formulario.setAttribute("name", this.id);
      formulario.setAttribute("step", step);
      if (pattern !== null) formulario.setAttribute("pattern", pattern);
      formulario.setAttribute("min", 0);
      formulario.setAttribute("required", true);
      formulario.setAttribute("id", "selec" + this.id);
      formulario.setAttribute("class", "input-cantidad");
      formulario.setAttribute("autocomplete", "off");
      tdProducto.textContent = capitalizar(listaPrecios[datum][1]);
      tdProducto.setAttribute("title", tdProducto.textContent);
      tdProducto.classList.add("td-producto");
      tdPrecio.textContent = "$" + listaPrecios[datum][2];
      tdPrecio.classList.add("td-precio");
      tdUnidad.classList.add("td-unidad");
      tdCantidad.classList.add("td-cantidad");
      tdCantidad.append(formulario);
      trProducto.append(tdProducto);
      trProducto.append(tdPrecio);
      trProducto.append(tdUnidad);
      trProducto.append(tdCantidad);
      trProducto.append(btnBorrar);
      listaSeleccionados.append(trProducto);
      btnBorrar.addEventListener("click", function (e) {
        this.parentElement.remove();
      });
    });
    //if (precio_minoritario == true) {
    //  trMayorista.addEventListener("click", function (e) {
    //    /*insert the value for the autocomplete text field:*/
    //    let li = document.createElement("li");
    //    let label = document.createElement("label");
    //    let formulario = document.createElement("input");
    //    let spanPresentacion = document.createElement("span");
    //    let btnBorrar = document.createElement("span");
    //    if (presentacion === "granel") {
    //      spanPresentacion.textContent = " Kg.";
    //    } else {
    //      spanPresentacion.textContent = " unidad/es";
    //    }
    //    btnBorrar.textContent = "❌";
    //    btnBorrar.style.cursor = "pointer";
    //    //p.setAttribute("display", "inline-block");
    //    formulario.setAttribute("type", "number");
    //    formulario.setAttribute("name", this.id);
    //    formulario.setAttribute("step", 0.05);
    //    formulario.setAttribute("min", 0);
    //    formulario.setAttribute("required", true);
    //    formulario.setAttribute("id", "selec" + this.id);
    //    formulario.setAttribute("class", "input-cantidad");
    //    label.innerHTMj =
    //      capitalizar(listaPrecios[datum][1]) + " <b>5 LITROS</b>" + ": ";
    //    label.setAttribute("for", "selec" + this.id);
    //    label.setAttribute("display", "inline-block");
    //    label.append(formulario);
    //    li.append(label);
    //    li.append(spanPresentacion);
    //    li.append(btnBorrar);
    //    listaSeleccionados.append(li);
    //    btnBorrar.addEventListener("click", function (e) {
    //      this.parentElement.remove();
    //    });
    //    /*Falta código que inserte el ID en la lista que se va a ir
    //    armando */
    //  });
    //}
  }
}

/*function filtrar(texto) {
  for (let i; i < rows.length; i++) {
    if (rows[i].childNodes[0].innerHTML.contains(texto)) {
      esconderRow(rows[i].id);
    } else {
      mostrarRow(rows[i].id);
    }
  }
}*/

function esconderRow(id) {
  let elemento = document.getElementById(id);
  if (elemento) {
    elemento.style.display = "";
  }
}

function mostrarRow(id) {
  let elemento = document.getElementById(id);
  if (elemento) {
    elemento.style.display = "none";
  }
}

function capitalizar(val) {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function enviarFormulario() {
  form.addEventListener("submit", async (e) => {
    event.preventDefault();

    const formData = new FormData(form);
    const botonPedido = document.getElementById("boton-armar-pedido");

    botonPedido.value = "Por favor espere...";
    for (elemento in form.elements) {
      form.elements[elemento].disabled = true;
    }
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/armar_pedido?tienda=" + tiendaApi,
        {
          method: "POST",
          body: formData,
        },
      );

      if (response.ok) {
        window.location.href = "exito.html";
      } else {
        console.error("Error HTTP! Status: ", response.status);
        alert(
          "Hubo un error al intentar armar tu pedido! Por favor intentalo de nuevo más tarde :(",
        );
        botonPedido.value = "Armar pedido";
        for (elemento in form.elements) {
          form.elements[elemento].disabled = false;
        }
      }
    } catch (error) {
      console.error("Error con el fetch: ", error);
      botonPedido.value = "Armar pedido";
      for (elemento in form.elements) {
        form.elements[elemento].disabled = false;
      }
    }
  });
}
