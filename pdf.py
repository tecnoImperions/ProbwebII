from flask import Flask, send_file
from fpdf import FPDF
import os
from io import BytesIO

app = Flask(__name__)

@app.route("/ver-factura-prueba")
def ver_factura_prueba():
    # Datos simulados
    pedido = {
        'id': 123,
        'tienda_nombre': "MI TIENDA PRUEBA",
        'tienda_direccion': "Av. Siempre Viva 123",
        'cliente_nombre': "Juan Pérez",
        'cliente_correo': "juan@example.com",
        'fecha_creacion': "2026-01-14 12:30",
    }
    productos = [
        {'producto_nombre': "Producto A", 'cantidad': 2, 'precio_unitario': 10.5},
        {'producto_nombre': "Producto B", 'cantidad': 1, 'precio_unitario': 25.0},
    ]

    # Crear PDF en memoria
    pdf = FPDF('P', 'mm', (80, 250))
    pdf.add_page()
    pdf.set_margins(5, 5, 5)
    pdf.set_auto_page_break(auto=True, margin=10)

    # Encabezado
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 6, pedido['tienda_nombre'], 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    pdf.cell(0, 4, pedido['tienda_direccion'], 0, 1, 'C')
    pdf.cell(0, 4, "Bolivia", 0, 1, 'C')
    pdf.ln(2)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(2)

    # Cliente
    pdf.cell(0, 4, f"Cliente: {pedido['cliente_nombre']}", 0, 1)
    pdf.cell(0, 4, f"Correo: {pedido['cliente_correo']}", 0, 1)
    pdf.cell(0, 4, f"Fecha: {pedido['fecha_creacion']}", 0, 1)
    pdf.ln(2)

    # Productos
    for p in productos:
        total_item = p['cantidad'] * p['precio_unitario']
        pdf.cell(45, 4, p['producto_nombre'], 0, 0)
        pdf.cell(10, 4, str(p['cantidad']), 0, 0, 'C')
        pdf.cell(20, 4, f"{total_item:.2f} Bs", 0, 1, 'R')

    pdf.ln(2)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(2)

    # Totales
    subtotal = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
    iva = subtotal * 0.13
    total = subtotal + iva
    pdf.cell(50, 4, "Subtotal:", 0, 0)
    pdf.cell(25, 4, f"{subtotal:.2f} Bs", 0, 1, 'R')
    pdf.cell(50, 4, "IVA 13%:", 0, 0)
    pdf.cell(25, 4, f"{iva:.2f} Bs", 0, 1, 'R')
    pdf.cell(50, 4, "TOTAL:", 0, 0)
    pdf.cell(25, 4, f"{total:.2f} Bs", 0, 1, 'R')

    pdf.ln(5)
    pdf.cell(0, 4, "¡Gracias por su compra!", 0, 1, 'C')

    # Guardar PDF en memoria y enviarlo al navegador
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)

    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        download_name=f"factura_prueba_{pedido['id']}.pdf",
        as_attachment=False  # False para abrir en navegador
    )

if __name__ == "__main__":
    app.run(debug=True)
