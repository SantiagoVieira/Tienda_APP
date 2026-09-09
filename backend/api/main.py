"""API REST de la tienda.

Esta capa es deliberadamente delgada: recibe la petición HTTP, resuelve el
usuario y el producto, llama al método correspondiente de `Tienda` y serializa
el resultado. Ninguna regla de negocio vive aquí.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from datos import catalogo_inicial
from dominio import ErrorDominio, Item, ProductoNoEncontrado, Tienda, Usuario

from .esquemas import (
    AgregarItemIn,
    CarritoOut,
    CompraOut,
    ItemOut,
    ProductoOut,
    TiendaOut,
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="Tienda - Caso de estudio de principios de diseño",
    description=(
        "Implementación web del diseño orientado a objetos del OVA: "
        "Tienda, Usuario, Carrito, Item, Producto y las reglas de precio."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Única instancia de la tienda: el estado vive en memoria mientras el proceso
# esté arriba. El caso de estudio no pide persistencia.
tienda = Tienda(productos=catalogo_inicial())


# ---------------------------------------------------------------------------
# Dependencias y utilidades
# ---------------------------------------------------------------------------


def usuario_actual(x_usuario: str = Header(default="invitado")) -> Usuario:
    """Resuelve el usuario a partir del encabezado `X-Usuario`.

    El diagrama contempla varios usuarios, cada uno con su carrito. Se usa un
    encabezado en lugar de un sistema de autenticación porque el caso de
    estudio no plantea requisitos de seguridad.
    """
    return tienda.obtener_usuario(x_usuario)


@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(_request, exc: ErrorDominio):
    """Traduce los errores de negocio a respuestas HTTP."""
    from fastapi.responses import JSONResponse

    codigo = 404 if isinstance(exc, ProductoNoEncontrado) else 400
    return JSONResponse(status_code=codigo, content={"detail": str(exc)})


def _producto_out(producto) -> ProductoOut:
    regla = tienda.manejador_reglas.obtener_regla(producto.sku)
    return ProductoOut(
        sku=producto.sku,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        unidades_disponibles=producto.unidades_disponibles,
        precio_unitario=producto.precio_unitario,
        tipo=regla.nombre,
        unidad=regla.unidad,
    )


def _item_out(item: Item) -> ItemOut:
    return ItemOut(
        id=item.id,
        sku=item.producto.sku,
        nombre=item.producto.nombre,
        cantidad=item.cantidad,
        precio_unitario=item.producto.precio_unitario,
        regla=item.regla_precio.nombre,
        total=round(item.calcular_total(), 2),
    )


def _carrito_out(usuario: Usuario) -> CarritoOut:
    return CarritoOut(
        items=[_item_out(i) for i in usuario.carrito.items],
        total=round(usuario.carrito.calcular_total(), 2),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/productos", response_model=list[ProductoOut], tags=["Catálogo"])
def listar_productos():
    """Catálogo de la tienda con el tipo de producto según su SKU."""
    return [_producto_out(p) for p in tienda.productos]


@app.get("/api/tienda", response_model=TiendaOut, tags=["Tienda"])
def estado_tienda():
    """Total acumulado de ventas de la tienda."""
    return TiendaOut(total_ventas=round(tienda.total_ventas, 2))


@app.get("/api/carrito", response_model=CarritoOut, tags=["Carrito"])
def ver_carrito(usuario: Usuario = Depends(usuario_actual)):
    """Contenido del carrito con el total de cada ítem y el total general."""
    return _carrito_out(usuario)


@app.post("/api/carrito/items", response_model=CarritoOut, tags=["Carrito"])
def agregar_item(datos: AgregarItemIn, usuario: Usuario = Depends(usuario_actual)):
    """Agrega un producto al carrito verificando la disponibilidad."""
    producto = tienda.buscar_producto(datos.sku)
    tienda.agregar_producto_a_carrito(usuario, producto, datos.cantidad)
    return _carrito_out(usuario)


@app.delete("/api/carrito/items/{item_id}", response_model=CarritoOut, tags=["Carrito"])
def eliminar_item(item_id: int, usuario: Usuario = Depends(usuario_actual)):
    """Elimina un ítem del carrito."""
    item = usuario.carrito.buscar_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="El ítem no está en el carrito")
    tienda.eliminar_item_de_carrito(usuario, item)
    return _carrito_out(usuario)


@app.post("/api/compras", response_model=CompraOut, tags=["Compra"])
def finalizar_compra(usuario: Usuario = Depends(usuario_actual)):
    """Concreta la compra: acumula la venta y descuenta el inventario."""
    total = tienda.finalizar_compra(usuario)
    return CompraOut(
        total=round(total, 2), total_ventas=round(tienda.total_ventas, 2)
    )


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

if FRONTEND_DIR.is_dir():
    app.mount(
        "/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static"
    )

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
