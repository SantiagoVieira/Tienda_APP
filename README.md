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

```
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
|---|---|
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
|---|---|---|
| `EA` | Normal | `precio_unitario × cantidad` |
| `WE` | De peso | `cantidad_kg × 1000 × precio_por_gramo` |
| `SP` | Descuento especial | 20% de descuento por cada 3 unidades completas, con tope de 50% |

Descuento especial en detalle: 1–2 u. → 0%; 3–5 u. → 20%; 6–8 u. → 40%;
9 u. o más → 50% (tope).

### Cómo agregar una regla nueva

Basta con escribir una clase y decorarla. No se modifica ningún archivo
existente:

```python
@registrar_regla
class ReglaPrecioCombo(ReglaPrecio):
    nombre = "Combo 2x1"

    def es_aplicable(self, sku: str) -> bool:
        return sku.upper().startswith("CB")

    def calcular_total(self, cantidad: int, precio: float) -> float:
        return precio * (cantidad - cantidad // 2)
```

`Item`, `Carrito`, `Tienda`, `ManejadorReglas`, la API y el frontend quedan
intactos. Esto es exactamente lo que pedía el enunciado: *"estos cambios y
adiciones de nuevas reglas se deben poder hacer de forma desacoplada, generando
la menor cantidad de cambios posibles en los componentes ya implementados"*.

---

## API REST

| Método | Ruta | Qué hace | Método de dominio que invoca |
|---|---|---|---|
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

## Decisiones de implementación

1. **El dominio se implementó tal cual y aislado.** `dominio/` no conoce
   FastAPI, HTTP ni JSON. La API es una capa delgada de traducción.

2. **La API es delgada a propósito.** Cada endpoint resuelve el usuario y el
   producto, llama a un método de `Tienda` y serializa el resultado. No hay
   ninguna regla de negocio en `api/`.

3. **Esquemas Pydantic separados de las clases de dominio.** Las clases del
   dominio tienen comportamiento; los esquemas son estructuras de transporte.
   Unificarlos habría atado el modelo de objetos al formato de la respuesta
   HTTP.

4. **`Item` resuelve su regla una sola vez, en el constructor**, a través de
   `ManejadorReglas`. A partir de ahí solo conoce la interfaz `ReglaPrecio`, así
   que `calcular_total` no cambia cuando aparecen reglas nuevas.

5. **Cada regla decide si le aplica un SKU (`es_aplicable`).** No hay ningún
   `if/elif` sobre el prefijo del SKU en el sistema. `ManejadorReglas` solo
   recorre la lista y devuelve la primera coincidencia.

6. **Registro de reglas por decorador.** `@registrar_regla` inscribe la clase en
   un catálogo que `ManejadorReglas` lee al construirse. Sin esto habría que
   editar la lista de reglas de `ManejadorReglas` cada vez, que es justo el
   acoplamiento que el enunciado pide evitar.

7. **La regla también expone su unidad (`unidad`).** El frontend etiqueta las
   cantidades como "u." o "kg" con ese dato, sin conocer los prefijos de SKU.

8. **El inventario se valida al agregar y se descuenta solo al comprar.** Al
   agregar se descuenta lo que el usuario ya tiene reservado en su carrito, para
   que no pueda agregar dos veces el inventario completo. `finalizar_compra`
   valida todo antes de modificar nada, para no dejar el inventario a medio
   actualizar.

9. **Errores de dominio propios.** `dominio/errores.py` define excepciones de
   negocio que la capa web traduce a códigos HTTP. El dominio nunca lanza
   `HTTPException`.

10. **El frontend no replica el modelo de objetos.** No hay clases `Carrito` ni
    `ReglaPrecio` en JavaScript, ni cálculos de precio duplicados. Todos los
    totales que se ven en pantalla los calculó el dominio en el servidor. Si se
    cambia una regla, el frontend refleja el cambio sin tocar una línea.

11. **Estado en memoria.** El caso de estudio no plantea persistencia, así que
    el catálogo se carga desde `datos.py` al arrancar. Reiniciar el proceso
    restablece la tienda.

### Elementos agregados que no están en el diagrama

Se documentan explícitamente por transparencia:

- **`Item.id`**: identificador técnico para poder eliminar un ítem por HTTP. El
  diagrama pasa el objeto `Item` directamente, lo cual no es posible a través de
  una petición REST.
- **`Carrito.buscar_item(id)`** y **`Carrito.vaciar()`**: auxiliares derivados de
  lo anterior y del vaciado del carrito tras la compra.
- **`Tienda.buscar_producto(sku)`** y **`Tienda.obtener_usuario(nombre)`**: el
  diagrama muestra las asociaciones `productos` y `usuarios`, pero no los
  métodos de consulta que hacen falta para resolverlas desde una petición.
- **`dominio/errores.py`**: manejo de errores, que el diagrama no aborda.
- **`ReglaPrecioPorDefecto`**: regla de respaldo para SKUs con prefijo
  desconocido, para que `obtener_regla` nunca retorne `None`.

---

## Supuestos

- Para los productos de peso (`WE`), la cantidad se expresa en **kilogramos** y
  el precio unitario en **pesos por gramo**, siguiendo el enunciado ("se calcula
  el valor por kilogramo... el precio unitario del producto está dado por
  gramo"). Las `unidades_disponibles` de esos productos también están en
  kilogramos.
- El descuento especial se calcula sobre **bloques completos** de 3 unidades
  (división entera).
- Agregar dos veces el mismo producto crea dos ítems separados en el carrito, tal
  como se desprende del diagrama (`Carrito` tiene una colección de `Item`, sin
  restricción de unicidad por producto).
