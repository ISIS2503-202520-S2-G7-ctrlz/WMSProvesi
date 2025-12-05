from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Producto
from django.shortcuts import get_object_or_404

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal


@require_GET
def listar_productos(request):
    productos = Producto.objects.all().values("nombre", "sku", "precio", "stock", "ubicacion") #recordar, quitamos id
    # opcional: convertir Decimal a float si hiciera falta
    productos_list = []
    for p in productos:
        p["precio"] = float(p["precio"])
        productos_list.append(p)
    return JsonResponse(productos_list, safe=False)


@require_GET
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    data = {
        #"id": producto.id,
        "nombre": producto.nombre,
        "sku": producto.sku,
        "precio": float(producto.precio),
        "stock": producto.stock,
        "ubicacion": producto.ubicacion or "No disponible"
    }
    return JsonResponse(data)

@require_POST
def crear_producto(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # validar campos requeridos
    required_fields = ["nombre", "sku", "precio", "stock"]
    for field in required_fields:
        if field not in data:
            return JsonResponse({"error": f"Falta el campo '{field}'"}, status=400)

    # crear producto
    try:
        producto = Producto.objects.create(
            nombre=data["nombre"],
            sku=data["sku"],
            precio=Decimal(str(data["precio"])),
            stock=data["stock"],
            ubicacion=data.get("ubicacion", "")
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({
        "mensaje": "Producto creado correctamente",
        "producto": {
            "nombre": producto.nombre,
            "sku": producto.sku,
            "precio": float(producto.precio),
            "stock": producto.stock,
            "ubicacion": producto.ubicacion
        }
    })