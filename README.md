# Tienda — Caso de estudio de principios de diseño de software

Implementación web (frontend + backend) del caso de estudio de la aplicación de
comercio discutido en el OVA de principios de diseño de software.

El objetivo del ejercicio es comprobar **si un modelo de diseño orientado a
objetos sirve para implementar una aplicación web moderna**, donde la
comunicación es por HTTP/JSON y la interfaz no es orientada a objetos. Por eso
el diseño del OVA se implementó tal cual, sin "aplanarlo" a funciones sueltas.

---

## Cómo ejecutar

Requisitos: Python 3.10 o superior.

```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Luego abrir <http://127.0.0.1:8000>.

El mismo servidor sirve el frontend, así que no hay un segundo proceso ni un
paso de compilación. La documentación interactiva de la API queda en
<http://127.0.0.1:8000/docs>.

---

## Estructura del proyecto

```text
tienda-app/
├── backend/
│   ├── dominio/                 ← el diseño del OVA, sin dependencias web
│   │   ├── producto.py          ← Producto
│   │   ├── reglas.py            ← ReglaPrecio + las 3 implementaciones
│   │   ├── manejador_reglas.py  ← ManejadorReglas
│   │   ├── item.py              ← Item
│   │   ├── carrito.py           ← Carrito
│   │   ├── usuario.py           ← Usuario
│   │   ├── tienda.py            ← Tienda
│   │   └── errores.py           ← excepciones de negocio
│   ├── api/
│   │   ├── main.py              ← endpoints REST (capa delgada)
│   │   └── esquemas.py          ← modelos Pydantic de entrada/salida
│   ├── datos.py                 ← catálogo inicial en memoria
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── estilos.css
    └── app.js
```

La regla estructural del proyecto es que **`dominio/` no importa nada de
FastAPI**. Se puede ejecutar, probar y razonar sin levantar un servidor; la web
es solo una de sus posibles interfaces.

---

## Mapeo del diagrama al código

| Elemento del diagrama | Dónde quedó |
| --- | --- |
| `Tienda` (`total_ventas`, `agregar_producto_a_carrito`, `eliminar_item_de_carrito`, `finalizar_compra`) | `dominio/tienda.py` |
| `Usuario` (`agregar_item_a_carrito`, `borrar_item_de_carrito`) | `dominio/usuario.py` |
| `Carrito` (`agregar_item`, `calcular_total`, `borrar_item`) | `dominio/carrito.py` |
| `Item` (`cantidad`, `calcular_total`, dependencia con `ManejadorReglas`) | `dominio/item.py` |
| `Producto` (`sku`, `nombre`, `descripcion`, `unidades_disponibles`, `precio_unitario`, `tiene_unidades`, `descontar_unidades`) | `dominio/producto.py` |
| `ManejadorReglas` (`obtener_regla`) | `dominio/manejador_reglas.py` |
| `<<Interface>> ReglaPrecio` (`es_aplicable`, `calcular_total`) | `dominio/reglas.py` (`ABC`) |
| `ReglaPrecioNormal`, `ReglaPrecioPorPeso`, `ReglaPrecioEspecial` | `dominio/reglas.py` |

Todas las clases, atributos y firmas del diagrama existen en el código con el
mismo nombre. Lo único que se agregó fueron detalles técnicos inevitables para
una aplicación web, señalados más abajo.

---

## Reglas de precio

| Prefijo del SKU | Tipo | Cálculo |
| --- | --- | --- |
| `EA` | Normal | `precio_unitario × cantidad` |
| `WE` | De peso | `cantidad_kg × 1000 × precio_por_gramo` |
| `SP` | Descuento especial | 20% de descuento por cada 3 unidades completas, con tope de 50% |

Descuento especial en detalle: 1–2 u. → 0%; 3–5 u. → 20%; 6–8 u. → 40%;
9 u. o más → 50% (tope).

## API REST

| Método | Ruta | Qué hace | Método de dominio que invoca |
| --- | --- | --- | --- |
| `GET` | `/api/productos` | Catálogo con tipo de producto y unidad | — |
| `GET` | `/api/tienda` | Total acumulado de ventas | `Tienda.total_ventas` |
| `GET` | `/api/carrito` | Ítems con su total y el total de la compra | `Carrito.calcular_total` |
| `POST` | `/api/carrito/items` | Agrega un producto validando inventario | `Tienda.agregar_producto_a_carrito` |
| `DELETE` | `/api/carrito/items/{id}` | Elimina un ítem del carrito | `Tienda.eliminar_item_de_carrito` |
| `POST` | `/api/compras` | Concreta la compra | `Tienda.finalizar_compra` |

El usuario se identifica con el encabezado `X-Usuario` (por defecto
`invitado`), de modo que cada usuario tiene su propio carrito como plantea el
diagrama. No hay autenticación porque el caso de estudio no la plantea.

---
