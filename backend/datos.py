"""Catálogo inicial de la tienda.

El caso de estudio no pide persistencia, así que el inventario vive en memoria
y se carga desde aquí al arrancar el servidor. Reiniciar el proceso restablece
el catálogo a este estado.
"""

from __future__ import annotations

from typing import List

from dominio import Producto


def catalogo_inicial() -> List[Producto]:
    return [
        # --- Productos normales (EA): precio por unidad -------------------
        Producto(
            sku="EA-1001",
            nombre="Cuaderno cuadriculado",
            descripcion="Cuaderno de 100 hojas, tamaño carta.",
            unidades_disponibles=40,
            precio_unitario=8500,
        ),
        Producto(
            sku="EA-1002",
            nombre="Audífonos inalámbricos",
            descripcion="Audífonos Bluetooth con estuche de carga.",
            unidades_disponibles=12,
            precio_unitario=129900,
        ),
        Producto(
            sku="EA-1003",
            nombre="Termo de acero 750 ml",
            descripcion="Termo con aislamiento térmico de doble pared.",
            unidades_disponibles=25,
            precio_unitario=54000,
        ),
        # --- Productos de peso (WE): precio POR GRAMO, cantidad en kg -----
        Producto(
            sku="WE-2001",
            nombre="Café molido de origen",
            descripcion="Café tostado y molido. Se vende por kilogramo.",
            unidades_disponibles=30,
            precio_unitario=38.5,
        ),
        Producto(
            sku="WE-2002",
            nombre="Almendras naturales",
            descripcion="Almendras sin sal. Se venden por kilogramo.",
            unidades_disponibles=18,
            precio_unitario=52.0,
        ),
        # --- Productos de descuento especial (SP) -------------------------
        Producto(
            sku="SP-3001",
            nombre="Jabón artesanal",
            descripcion="Jabón de glicerina. 20% de descuento por cada 3 unidades.",
            unidades_disponibles=60,
            precio_unitario=12000,
        ),
        Producto(
            sku="SP-3002",
            nombre="Medias deportivas",
            descripcion="Par de medias de algodón. Descuento por volumen.",
            unidades_disponibles=45,
            precio_unitario=15900,
        ),
    ]
