from fpdf import FPDF
import os
from datetime import datetime

def generar_factura(order, tienda, cliente, items, path_guardar="facturas/"):
    """
    order: dict con info del pedido (id, fecha, total, estado)
    tienda: dict con info de la tienda (nombre, direccion)
    cliente: dict con info del cliente (nombre, nit, telefono, direccion, ciudad)
    items: lista de dicts con info de productos (nombre, cantidad, precio)
    path_guardar: carpeta donde guardar PDF
    """
    pdf = FPDF('P', 'mm', (80, 250))
    pdf.add_page()
    pdf.set_margins(5, 5, 5)
    pdf.set_auto_page_break(auto=True, margin=10)

    # Encabezado
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 6, "MI TIENDA", 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 4, tienda['nombre'], 0, 1, 'C')
    pdf.cell(0, 4, tienda['direccion'], 0, 1, 'C')
    pdf.cell(0, 4, "Bolivia", 0, 1, 'C')
    pdf.cell(0, 4, "Tel: (591) 6-3488086", 0, 1, 'C')
    pdf.cell(0, 4, "NIT: 123456789", 0, 1, 'C')
    pdf.ln(2)
    pdf.set_line_width(0.5)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(3)

    # Datos factura
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 5, "FACTURA DE COMPRA", 0, 1, 'C')
    pdf.set_font('Arial', '', 9)
    pdf.cell(25, 4, "Factura No:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, str(order['id']).zfill(6), 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(25, 4, "Fecha:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, order['fecha'].strftime('%d/%m/%Y %H:%M'), 0, 1)
    pdf.ln(2)
    pdf.set_line_width(0.3)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(3)

    # Datos cliente
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 4, "DATOS DEL CLIENTE", 0, 1)
    pdf.ln(1)
    pdf.set_font('Arial', '', 9)
    pdf.cell(20, 4, "Cliente:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.multi_cell(0, 4, cliente['nombre'], 0)
    pdf.set_font('Arial', '', 9)
    pdf.cell(20, 4, "NIT/CI:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, cliente.get('nit', 'S/N'), 0, 1)
    pdf.cell(20, 4, "Telefono:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, cliente.get('telefono', ''), 0, 1)
    pdf.cell(20, 4, "Direccion:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.multi_cell(0, 4, cliente.get('direccion', ''))
    pdf.cell(20, 4, "Ciudad:", 0, 0)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, cliente.get('ciudad', ''), 0, 1)
    pdf.ln(2)
    pdf.set_line_width(0.3)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(3)

    # Detalle productos
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(0, 4, "DETALLE DE PRODUCTOS", 0, 1, 'C')
    pdf.ln(1)
    pdf.set_line_width(0.2)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(2)

    subtotal_general = 0
    for item in items:
        nombre_producto = item['nombre']
        precio_unit = item['precio']
        qty = item['cantidad']
        subtotal = precio_unit * qty
        subtotal_general += subtotal

        pdf.set_font('Arial', 'B', 9)
        pdf.multi_cell(0, 4, nombre_producto, 0, 'L')
        pdf.set_font('Arial', '', 8)
        pdf.cell(45, 4, f"  {qty} x Bs {precio_unit:.2f}", 0, 0, 'L')
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(25, 4, f"Bs {subtotal:.2f}", 0, 1, 'R')
        pdf.ln(1)

    # IVA 13%
    iva = subtotal_general * 0.13
    total_con_iva = subtotal_general + iva

    pdf.ln(2)
    pdf.set_line_width(0.3)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(35, 5, "SUBTOTAL:", 0, 0, 'R')
    pdf.set_font('Arial', '', 10)
    pdf.cell(35, 5, f"Bs {subtotal_general:.2f}", 0, 1, 'R')
    pdf.cell(35, 5, "IVA (13%):", 0, 0, 'R')
    pdf.set_font('Arial', '', 10)
    pdf.cell(35, 5, f"Bs {iva:.2f}", 0, 1, 'R')
    pdf.ln(1)
    pdf.set_line_width(0.5)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(35, 6, "TOTAL:", 0, 0, 'R')
    pdf.set_font('Arial', 'B', 13)
    pdf.cell(35, 6, f"Bs {total_con_iva:.2f}", 0, 1, 'R')
    pdf.ln(3)

    # Pie
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 4, "Esta factura es válida como comprobante de compra.", 0, 'C')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "¡Gracias por su compra!", 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 4, "Lo esperamos pronto", 0, 1, 'C')
    pdf.set_font('Arial', 'I', 7)
    pdf.cell(0, 3, "www.misitio.com", 0, 1, 'C')

    # Crear carpeta si no existe
    if not os.path.exists(path_guardar):
        os.makedirs(path_guardar)

    filename = os.path.join(path_guardar, f"factura_{order['id']}.pdf")
    pdf.output(filename)
    return filename
