from .models import Pedido
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
import requests
import json


#===============================================
#Lógica de validación
#===============================================

def check_productos(data):
    r = requests.get(settings.PATH_PRODUCTO, headers={"Accept":"application/json"})
    productos = r.json()

    ids_disponibles = {p["sku"] for p in productos}

    ids_solicitados = {item["sku"] for item in data["productos"]}

    return ids_solicitados.issubset(ids_disponibles)

#TODO
def get_bodega_id(data):
    r = requests.get(settings.PATH_BODEGAS, headers={"Accept":"application/json"})
    places = r.json()
    for place in places:
        if data["place"] == place["name"]:
            return place["id"]
    return -1

#===============================================
#Lógica de Consulta
#===============================================

def PedidosList(request):
    if request.method == "GET":
        queryset = Pedido.objects.all()
        context = list(queryset.values('codigo', 'cliente', 'estado', 'fecha_creacion', 'fecha_actualizacion'))
    return JsonResponse(context, safe=False)


def pedido_detalle(request, codigo):
    if request.method =="GET":
        pedido = get_object_or_404(Pedido, codigo=codigo)

        #Consumir microservicio de productos para obtener detalles
        r = requests.get(settings.PATH_PRODUCTO, headers={"Accept":"application/json"})
        productos = r.json()

        #Indexar productos por SKU
        productos_dict = {str(p["sku"]): p for p in productos}


        productos_completos = []
        for item in pedido.productos:
            sku = str(item.get("sku"))
            if sku in productos_dict:
                producto_detallado = productos_dict[sku]
                producto_detallado["cantidad"] = item.get("cantidad", 1)
                productos_completos.append(producto_detallado)

        # 4. Respuesta completa del pedido
        data = {
            "codigo": pedido.codigo,
            "cliente": pedido.cliente,
            "estado": pedido.estado,
            "fecha_creacion": pedido.fecha_creacion,
            "fecha_actualziacion": pedido.fecha_actualizacion,
            "detalles": pedido.detalles,
            "productos": productos_completos,
        }

    return JsonResponse(data)


#===============================================
#Lógica de Creación
#===============================================

def PedidoCreate(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data_json = json.loads(data)
        if check_productos(data_json):
            pedido = Pedido()
            pedido.codigo = data_json['codigo']
            pedido.cliente = data_json['cliente']
            pedido.estado = data_json['estado']
            pedido.detalles = data_json['detalles']
            pedido.productos = data_json['productos']
            pedido.save()
            return HttpResponse("Pedido creado exitosamente successfully created")
        else:
            return HttpResponse("Error creando el pedido. Algun producto no existe", status=400)

def PedidosCreate(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data_json = json.loads(data)
        pedidos_list = []
        for pedido in data_json:
                    if check_productos(pedido):
                        db_pedido = Pedido()
                        db_pedido.codigo = pedido['codigo']
                        db_pedido.cliente = pedido['cliente']
                        db_pedido.estado = pedido['estado']
                        db_pedido.fecha_creacion = pedido['fecha_creacion']
                        db_pedido.fecha_actualizacion = data_json['fecha_actualizacion']
                        db_pedido.detalles = data_json['detalles']
                        db_pedido.productos = data_json['productos']
                        pedidos_list.append(db_pedido)
                    else:
                        return HttpResponse("Error creando el pedido. Algun producto no existe", status=400)
        
        Pedido.objects.bulk_create(pedidos_list)
        return HttpResponse("Pedidos creados exitosamente")


