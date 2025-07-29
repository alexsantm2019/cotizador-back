from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Cotizacion, CotizacionDetalle
from .serializers import CotizacionSerializer
from .serializers import CotizacionDetalleSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import datetime
import json
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import Producto

# Para enviar PDF y whatsapp:
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
import os
from reportlab.pdfgen import canvas

#Tablas:
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import Image
from datetime import datetime

@api_view(['GET'])
def get_cotizaciones(request):
    cotizaciones = Cotizacion.objects.filter(deleted_at__isnull=True).order_by('-id')    
    serializer = CotizacionSerializer(cotizaciones, many=True, context={'request': request})  # Agregar contexto

    # cotizaciones = Cotizacion.objects.filter(deleted_at__isnull=True).select_related('user').order_by('-id')
    # serializer = CotizacionSerializer(cotizaciones, many=True, context={'request': request})  
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_cotizacion_by_id(request, cotizacion_id):
    try:
        cotizacion = Cotizacion.objects.get(id=cotizacion_id, deleted_at__isnull=True)
        serializer = CotizacionSerializer(cotizacion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cotizacion.DoesNotExist:
        return Response(
            {"error": "Cotización no encontrada o está eliminada."},
            status=status.HTTP_404_NOT_FOUND,
        )    

@api_view(['GET'])
def get_cotizaciones_by_fecha(request, year, month=None):
    if not year:
        return Response({"detail": "El año es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Convertir el año y mes a enteros si es necesario
        year = int(year)
        if month:
            month = int(month)
    except ValueError:
        return Response({"detail": "El año y mes deben ser números."}, status=status.HTTP_400_BAD_REQUEST)

    # Definir los límites para el filtro de fecha
    if month:
        # Crear la fecha de inicio y fin para el mes especificado
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)  # Para diciembre, el mes siguiente es enero del siguiente año
        else:
            end_date = datetime(year, month + 1, 1)  # El primer día del siguiente mes
    else:
        # Si no hay mes, solo se filtra por el año
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)  # El primer día del siguiente año

    # Filtrar las cotizaciones dentro del rango de fechas
    cotizaciones = Cotizacion.objects.filter(
        fecha_creacion__gte=start_date, fecha_creacion__lt=end_date, deleted_at__isnull=True
    ).order_by('-id')

    # Verificar si hay cotizaciones
    if not cotizaciones:
        return Response([], status=status.HTTP_200_OK)

    # Serializar las cotizaciones
    serializer = CotizacionSerializer(cotizaciones, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_cotizacion(request):
    if request.method == 'POST':
        with transaction.atomic():  # Usamos transacciones para garantizar consistencia
            # Guardar la cotización
            cotizacion_serializer = CotizacionSerializer(data=request.data, context={'request': request})    # Para agregar user_id
            if cotizacion_serializer.is_valid():
                cotizacion = cotizacion_serializer.save()  # Guardar y obtener la instancia creada

                # Obtener los detalles de la cotización del request
                detalles = request.data.get('detalles', [])  # Asegurarse de que se envían los detalles
                
                if not detalles:
                    return Response(
                        {"error": "Debe incluir al menos un detalle en la cotización."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                # Guardar cada detalle
                for detalle_data in detalles:
                    detalle_data['cotizacion'] = cotizacion.id  # Asociar el detalle a la cotización creada
                    detalle_serializer = CotizacionDetalleSerializer(data=detalle_data)
                    if detalle_serializer.is_valid():
                        detalle_serializer.save()
                    else:
                        return Response(
                            detalle_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                        )

                return Response(cotizacion_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(cotizacion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

@api_view(['PUT'])
def update_cotizacion(request, cotizacion_id):
    try:
        # Obtener la cotización a actualizar
        cotizacion = Cotizacion.objects.get(id=cotizacion_id, deleted_at__isnull=True)

        with transaction.atomic():  # Usamos transacciones para garantizar consistencia
            # Actualizar la cotización
            cotizacion_serializer = CotizacionSerializer(cotizacion, data=request.data, context={'request': request}, partial=(request.method == 'PATCH')) # Para agregar user_id
            if cotizacion_serializer.is_valid():
                cotizacion = cotizacion_serializer.save()

                # Actualizar los detalles
                detalles = request.data.get('detalles', [])

                if not detalles:
                    return Response(
                        {"error": "Debe incluir al menos un detalle en la cotización."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Eliminar los detalles existentes y crear los nuevos
                CotizacionDetalle.objects.filter(cotizacion=cotizacion).delete()
                for detalle_data in detalles:
                    detalle_data['cotizacion'] = cotizacion.id
                    detalle_serializer = CotizacionDetalleSerializer(data=detalle_data)
                    if detalle_serializer.is_valid():
                        detalle_serializer.save()

                        # ----------------------- Actualización de inventario -------------------                        
                        if cotizacion.estado == 3 and detalle_data.get("producto"):
                            producto_id = detalle_data["producto"]
                            cantidad_a_restar = int(detalle_data["cantidad"])

                            respuesta_stock = actualizar_stock(producto_id, cantidad_a_restar)
                            if respuesta_stock:
                                return respuesta_stock  # Retorna error si el stock no es suficiente
                        # ----------------------- Fin Actualización de inventario -------------------

                    else:
                        return Response(
                            detalle_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                        )

                return Response(cotizacion_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(cotizacion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Cotizacion.DoesNotExist:
        return Response(
            {"error": "Cotización no encontrada o está eliminada."},
            status=status.HTTP_404_NOT_FOUND,
        )  

def actualizar_stock(producto_id, cantidad_a_restar):
    """
    Actualiza el stock del producto restando la cantidad especificada.
    Retorna None si la actualización es exitosa, o un Response con el error correspondiente.
    """
    # Si el estado es 3 (confirmado), actualizar stock del producto
    try:
        producto = Producto.objects.get(id=producto_id)
        nueva_cantidad = producto.cantidad - cantidad_a_restar
        if nueva_cantidad < 0:
            return Response(
                {"error": f"Stock insuficiente para el producto {producto_id}. Disponible: {producto.cantidad}, requerido: {cantidad_a_restar}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar la cantidad en la base de datos
        producto.cantidad = nueva_cantidad
        producto.save()
        return None  # Indica que la actualización fue exitosa
    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)                      

@api_view(['DELETE'])
def delete_cotizacion(request, id):
    try:
        # Actualizar deleted_at de la cotización
        cotizacion = Cotizacion.objects.get(id=id, deleted_at__isnull=True)
        now = datetime.datetime.now()
        cotizacion.deleted_at = now
        cotizacion.save()

        # Actualizar deleted_at de los detalles relacionados
        CotizacionDetalle.objects.filter(cotizacion=cotizacion).update(deleted_at=now)

        return Response({"message": "Cotización eliminada correctamente."}, status=status.HTTP_200_OK)
    except Cotizacion.DoesNotExist:
        return Response({"error": "Cotización no encontrada o ya eliminada."}, status=status.HTTP_404_NOT_FOUND) 

# Función para generar el PDF
# pip install reportlab

def generar_pdf(cotizacion_id):
    try:
        cotizacion = Cotizacion.objects.select_related('cliente').prefetch_related('detalles__producto').get(
            id=cotizacion_id, deleted_at__isnull=True
        )              
    except ObjectDoesNotExist:
        return None  # Si la cotización no existe, retorna None

    # Directorio de destino
    media_dir = settings.MEDIA_ROOT
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Nombre del archivo PDF
    filename = f"cotizacion_{cotizacion.id}.pdf"
    filepath = os.path.join(media_dir, filename)

    # Crear el PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []

    # Ruta completa del logo en la subcarpeta LOGOS
    logo_path = os.path.join(settings.MEDIA_ROOT, 'LOGOS', 'logo_mundi.jpg')  # Cambia 'logo.png' por el nombre de tu logo

    # Incluir el logo en el PDF
    logo = Image(logo_path, width=5*cm, height=2*cm)  # Ajusta las dimensiones del logo
    logo.hAlign = 'CENTER'  # Centrar el logo
    elements.append(logo)
    elements.append(Spacer(1, 12))  # Espacio después del logo

    # Datos de la primera tabla (información del cliente)
    cliente = cotizacion.cliente
    data_cliente = [
        ["Fecha de Creación:", str(cotizacion.fecha_creacion.strftime("%d/%m/%Y"))],
        ["Nombre del Cliente:", cliente.nombre],
        ["Dirección:", cliente.direccion if cliente.direccion else "N/A"],
        ["Teléfono:", cliente.telefono if cliente.telefono else "N/A"],
        ["Correo:", cliente.correo if cliente.correo else "N/A"]
    ]

    # Estilos para texto en la tabla
    styles = getSampleStyleSheet()
    estilo_bold = styles["Normal"]
    estilo_bold.fontName = "Helvetica-Bold"  # Texto en negrita

    # Tabla con datos del cliente
    data_cliente_bold = [
        [Paragraph(f"<b>{item[0]}</b>", estilo_bold), item[1]] for item in data_cliente
    ]
    
    tabla_cliente = Table(data_cliente_bold, colWidths=[5 * cm, 11 * cm])  # Ocupar 100% de la página
    tabla_cliente.setStyle(TableStyle([]))  # Sin bordes ni colores
    elements.append(tabla_cliente)
    elements.append(Spacer(1, 20))  # Espacio entre tablas

    # Estilo cursiva para descripción
    estilo_cursiva = styles["Italic"]
    estilo_cursiva.alignment = TA_LEFT  # Alineación a la izquierda para la descripción

    # Datos de la segunda tabla (detalles de la cotización)
    detalles_data = [["CANTIDAD", "SERVICIO", "VALOR UNITARIO", "VALOR TOTAL"]]

    for detalle in cotizacion.detalles.all():
        cantidad = int(detalle.cantidad) if detalle.cantidad else 0
        costo_unitario = float(detalle.producto.costo) if detalle.producto and detalle.producto.costo else 0
        descuento = float(detalle.descuento) if detalle.descuento else 0
        valor_total = (cantidad * costo_unitario) - descuento

        servicio = detalle.producto.producto if detalle.producto else "Paquete"
        descripcion = detalle.producto.descripcion if detalle.producto and detalle.producto.descripcion else ""

        # Separar el nombre del servicio y la descripción
        servicio_con_descripcion = Paragraph(f"<b>{servicio}</b><br/><i>{descripcion}</i>")

        # Añadir a la fila de la tabla
        detalles_data.append([cantidad, servicio_con_descripcion, f"${costo_unitario}", f"${valor_total}"])

    # Agregar Subtotal, IVA y Total debajo de las columnas correspondientes
    subtotal = float(cotizacion.subtotal) if cotizacion.subtotal else 0
    iva = float(cotizacion.iva) if cotizacion.iva else 0
    total = float(cotizacion.total) if cotizacion.total else 0

    detalles_data.append(["", "", "Subtotal:", f"${subtotal:.2f}"])
    detalles_data.append(["", "", "IVA:", f"${iva:.2f}"])
    detalles_data.append(["", "", "Total:", f"${total:.2f}"])

    tabla_detalles = Table(detalles_data, colWidths=[3 * cm, 7 * cm, 4 * cm, 4 * cm])
    tabla_detalles.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # Encabezado en gris
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Centrar todo el contenido
        ("ALIGN", (1, 1), (1, -1), "LEFT"),  # Solo la columna "SERVICIO" alineada a la izquierda
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Centrado vertical de toda la tabla
        ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Bordes en la tabla
        ("FONTNAME", (-2, -3), (-1, -1), "Helvetica-Bold"),  # Subtotal, IVA y Total en negrita
        ("ALIGN", (-2, -3), (-1, -1), "CENTER"),  # Alinear valores a la derecha
        ("BACKGROUND", (-2, -3), (-1, -1), colors.lightgrey),  # Fondo gris para las filas de totales
    ]))

    elements.append(tabla_detalles)
    elements.append(Spacer(1, 20))  # Espacio antes del mensaje final

    # Mensaje final
    usuario = "Ninguno"
    if cotizacion.user:
        first_name = cotizacion.user.first_name if cotizacion.user.first_name else ""
        last_name = cotizacion.user.last_name if cotizacion.user.last_name else ""
        usuario = f"{first_name} {last_name}".strip() if first_name or last_name else cotizacion.user.username

    mensaje_texto = f"""<para align=left>
    <span>Validez de la proforma:</span> 24 horas<br/>
    Cualquier modificación, la podemos realizar sin ningún inconveniente.<br/>
    Si tienes alguna inquietud sobre esta cotización, puedes contactarnos al <b>0984687368</b>.<br/><br/>
    <span>Creado por:</span> <em>{usuario}</em><br/><br/>
    <b>Somos Grupo MundiEventos</b>
    </para>"""

    mensaje_final = Paragraph(mensaje_texto, styles["Normal"])
    elements.append(mensaje_final)

    # Generar PDF
    doc.build(elements)
    return filepath

@csrf_exempt
@require_POST
def enviar_correo(request, cotizacion_id):
    # Obtener la cotización
    cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id, deleted_at__isnull=True)

    # Generar el PDF antes de enviarlo
    pdf_path = generar_pdf(cotizacion_id)

    # Verificar si la generación del PDF fue exitosa
    if not pdf_path or not os.path.exists(pdf_path):
        return JsonResponse({'error': 'No se pudo generar el PDF'}, status=500)

    # Configurar el correo    
    subject = f'Cotización #{cotizacion_id} | Grupo MundiEventos'
    message = f'Hola {cotizacion.cliente.nombre},\n\nAdjunto encontrarás la cotización #{cotizacion_id}. \nSi tienes alguna duda o inquietud no dudes en conctactarte con nosotros.'
    recipient_list = [cotizacion.cliente.correo]  # Asegúrate de que el cliente tiene un campo "email"
    # recipient_list = ["alexsantm@gmail.com"]  # Asegúrate de que el cliente tiene un campo "email"

    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    # Adjuntar el PDF
    email.attach_file(pdf_path)

    # Enviar el correo
    try:
        email.send()
        return JsonResponse({'message': 'Correo enviado con éxito'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def enviar_whatsapp(request, cotizacion_id):
    filepath = generar_pdf(cotizacion_id)
    if not filepath:
        return JsonResponse({"error": "Cotización no encontrada"}, status=404)

    # Aquí deberías integrar WhatsApp API para enviar el PDF
    return JsonResponse({"message": f"Cotización {cotizacion_id} enviada por WhatsApp"})        