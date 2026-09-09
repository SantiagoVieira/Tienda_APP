/**
 * Frontend de la tienda.
 *
 * Decisión de diseño: el frontend NO replica el modelo de objetos ni conoce
 * ninguna regla de precio. Es una vista sobre el estado que expone el backend:
 * pide datos, los pinta y envía las acciones del usuario. Todos los totales
 * que se muestran aquí los calculó el dominio en el servidor.
 */

const API = "/api";
const USUARIO = "invitado";

const moneda = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const $productos = document.getElementById("productos");
const $itemsCarrito = document.getElementById("items-carrito");
const $totalCarrito = document.getElementById("total-carrito");
const $totalVentas = document.getElementById("total-ventas");
const $btnComprar = document.getElementById("btn-comprar");
const $aviso = document.getElementById("aviso");

let temporizadorAviso = null;

/** Muestra un mensaje breve en la parte inferior de la pantalla. */
function avisar(mensaje, tipo = "info") {
  $aviso.textContent = mensaje;
  $aviso.className = "aviso" + (tipo === "info" ? "" : ` aviso--${tipo}`);
  $aviso.hidden = false;
  clearTimeout(temporizadorAviso);
  temporizadorAviso = setTimeout(() => {
    $aviso.hidden = true;
  }, 3800);
}

/** Envoltura de fetch que propaga el mensaje de error del backend. */
async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(API + ruta, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      "X-Usuario": USUARIO,
      ...(opciones.headers || {}),
    },
  });
  const cuerpo = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || "Ocurrió un error inesperado");
  }
  return cuerpo;
}

/** Clase CSS de la insignia según el tipo de producto. */
function claseInsignia(sku) {
  if (sku.toUpperCase().startsWith("WE")) return "insignia insignia--peso";
  if (sku.toUpperCase().startsWith("SP")) return "insignia insignia--especial";
  return "insignia";
}

// --- Renderizado -----------------------------------------------------------

function pintarProductos(productos) {
  $productos.innerHTML = "";

  for (const p of productos) {
    const agotado = p.unidades_disponibles <= 0;
    const porGramo = p.unidad === "kg";

    const tarjeta = document.createElement("article");
    tarjeta.className = "tarjeta";
    tarjeta.innerHTML = `
      <span class="tarjeta__sku">${p.sku}</span>
      <span class="${claseInsignia(p.sku)}">${p.tipo}</span>
      <div class="tarjeta__nombre">${p.nombre}</div>
      <p class="tarjeta__desc">${p.descripcion}</p>
      <div class="tarjeta__precio">
        ${moneda.format(p.precio_unitario)}
        <small>${porGramo ? "por gramo" : "por unidad"}</small>
      </div>
      <div class="tarjeta__stock ${agotado ? "agotado" : ""}">
        ${agotado
          ? "Agotado"
          : `Disponibles: ${p.unidades_disponibles} ${porGramo ? "kg" : "u."}`}
      </div>
    `;

    const acciones = document.createElement("div");
    acciones.className = "tarjeta__acciones";

    const cantidad = document.createElement("input");
    cantidad.type = "number";
    cantidad.min = "1";
    cantidad.value = "1";
    cantidad.disabled = agotado;
    cantidad.setAttribute("aria-label", `Cantidad de ${p.nombre}`);

    const boton = document.createElement("button");
    boton.className = "boton";
    boton.textContent = "Agregar";
    boton.disabled = agotado;
    boton.addEventListener("click", () =>
      agregarAlCarrito(p.sku, Number(cantidad.value))
    );

    acciones.append(cantidad, boton);
    tarjeta.append(acciones);
    $productos.append(tarjeta);
  }
}

function pintarCarrito(carrito) {
  $itemsCarrito.innerHTML = "";

  if (carrito.items.length === 0) {
    $itemsCarrito.innerHTML = '<p class="vacio">Aún no has agregado productos.</p>';
  }

  for (const item of carrito.items) {
    const unidad = item.sku.toUpperCase().startsWith("WE") ? "kg" : "u.";

    const linea = document.createElement("div");
    linea.className = "linea";
    linea.innerHTML = `
      <div class="linea__nombre">${item.nombre}</div>
      <div class="linea__total">${moneda.format(item.total)}</div>
      <div class="linea__detalle">
        ${item.cantidad} ${unidad} · ${item.regla}
      </div>
    `;

    const acciones = document.createElement("div");
    acciones.className = "linea__acciones";

    const quitar = document.createElement("button");
    quitar.className = "boton--texto";
    quitar.textContent = "Eliminar";
    quitar.addEventListener("click", () => eliminarItem(item.id));

    acciones.append(quitar);
    linea.append(acciones);
    $itemsCarrito.append(linea);
  }

  $totalCarrito.textContent = moneda.format(carrito.total);
  $btnComprar.disabled = carrito.items.length === 0;
}

// --- Acciones --------------------------------------------------------------

async function cargarProductos() {
  pintarProductos(await pedir("/productos"));
}

async function cargarCarrito() {
  pintarCarrito(await pedir("/carrito"));
}

async function cargarTienda() {
  const tienda = await pedir("/tienda");
  $totalVentas.textContent = moneda.format(tienda.total_ventas);
}

async function agregarAlCarrito(sku, cantidad) {
  if (!Number.isInteger(cantidad) || cantidad <= 0) {
    avisar("La cantidad debe ser un número entero mayor que cero", "error");
    return;
  }
  try {
    const carrito = await pedir("/carrito/items", {
      method: "POST",
      body: JSON.stringify({ sku, cantidad }),
    });
    pintarCarrito(carrito);
    const agregado = carrito.items[carrito.items.length - 1];
    avisar(
      `${agregado.nombre} agregado · ítem: ${moneda.format(agregado.total)} · ` +
        `compra: ${moneda.format(carrito.total)}`,
      "exito"
    );
  } catch (error) {
    avisar(error.message, "error");
  }
}

async function eliminarItem(itemId) {
  try {
    pintarCarrito(await pedir(`/carrito/items/${itemId}`, { method: "DELETE" }));
  } catch (error) {
    avisar(error.message, "error");
  }
}

async function comprar() {
  try {
    const compra = await pedir("/compras", { method: "POST" });
    avisar(`Compra realizada por ${moneda.format(compra.total)}`, "exito");
    await Promise.all([cargarProductos(), cargarCarrito(), cargarTienda()]);
  } catch (error) {
    avisar(error.message, "error");
  }
}

// --- Arranque --------------------------------------------------------------

$btnComprar.addEventListener("click", comprar);

Promise.all([cargarProductos(), cargarCarrito(), cargarTienda()]).catch((error) =>
  avisar(`No se pudo conectar con el servidor: ${error.message}`, "error")
);
