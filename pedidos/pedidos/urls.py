from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('pedidos/', views.PedidosList),
    path('pedidos/<str:codigo>/', csrf_exempt(views.pedido_detalle), name='pedidoDetalle'),
    path('pedidocreate/', csrf_exempt(views.PedidoCreate), name='pedidoCreate'),
    path('createpedidos/', csrf_exempt(views.PedidosCreate), name='createPedidos'),
]