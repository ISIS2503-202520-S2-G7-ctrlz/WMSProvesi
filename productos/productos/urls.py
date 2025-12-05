from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('productos/', views.listar_productos, name='listar_productos'),
    path("productos/<int:producto_id>/", views.detalle_producto, name="detalle_producto"),
    path("productos/crear/", csrf_exempt(views.crear_producto), name="crear_producto"),
]