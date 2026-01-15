# models/cliente/generar_factura.py
from fpdf import FPDF
import os
from datetime import datetime

def generar_factura_cliente(pedido_id):
    """
    Genera una factura PDF para un pedido específico
    Retorna la ruta del archivo generado o None si hay error
    """
    from models.db import get_connection
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener datos del pedido
        cursor.execute("""
            SELECT 
                p.id,
                p.fecha_creacion,
                p.total,
                p.estado,
                c.nombre as cliente_nombre,
                c.correo as cliente_correo,
                c.telefono as cliente_telefono,
                c.direccion as cliente_direccion,
                t.nombre as tienda_nombre,
                t.direccion as tienda_direccion
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            LEFT JOIN tiendas t ON p.tienda_id = t.id
            WHERE p.id = %s
        """, (pedido_id,))
        
        pedido = cursor.fetchone()
        
        if not pedido:
            return None
        
        # Obtener productos del pedido
        cursor.execute("""
            SELECT 
                pp.cantidad,
                pp.precio_unitario,
                pr.nombre as producto_nombre
            FROM pedido_productos pp
            JOIN productos pr ON pp.producto_id = pr.id
            WHERE pp.pedido_id = %s
        """, (pedido_id,))
        
        productos = cursor.fetchall()
        
        # Crear el PDF
        pdf = FPDF('P', 'mm', (80, 250))
        pdf.add_page()
        pdf.set_margins(5, 5, 5)
        pdf.set_auto_page_break(auto=True, margin=10)
        
        # ========== ENCABEZADO ==========
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 6, pedido['tienda_nombre'] or "MI TIENDA", 0, 1, 'C')
        
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 4, pedido['tienda_direccion'] or "Dirección no especificada", 0, 1, 'C')
        pdf.cell(0, 4, "Bolivia", 0, 1, 'C')
        pdf.cell(0, 4, "Tel: (591) 6-3488086", 0, 1, 'C')
        pdf.cell(0, 4, "NIT: 123456789", 0, 1, 'C')
        
        pdf.ln(2)
        pdf.set_line_width(0.5)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(3)
        
        # ========== DATOS DE FACTURA ==========
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 5, "FACTURA DE COMPRA", 0, 1, 'C')
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(25, 4, "Factura No:", 0, 0)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 4, str(pedido['id']).zfill(6), 0, 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(25, 4, "Fecha:", 0, 0)
        pdf.set_font('Arial', 'B', 9)
        fecha_str = pedido['fecha_creacion'].strftime('%d/%m/%Y %H:%M') if pedido['fecha_creacion'] else 'N/A'
        pdf.cell(0, 4, fecha_str, 0, 1)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(25, 4, "Estado:", 0, 0)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 4, pedido['estado'].upper(), 0, 1)
        
        pdf.ln(2)
        pdf.set_line_width(0.3)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(3)
        
        # ========== DATOS DEL CLIENTE ==========
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 4, "DATOS DEL CLIENTE", 0, 1)
        pdf.ln(1)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(20, 4, "Cliente:", 0, 0)
        pdf.set_font('Arial', 'B', 9)
        pdf.multi_cell(0, 4, pedido['cliente_nombre'] or 'N/A', 0)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(20, 4, "Correo:", 0, 0)
        pdf.set_font('Arial', 'B', 9)
        pdf.multi_cell(0, 4, pedido['cliente_correo'] or 'N/A', 0)
        
        if pedido['cliente_telefono']:
            pdf.set_font('Arial', '', 9)
            pdf.cell(20, 4, "Telefono:", 0, 0)
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(0, 4, pedido['cliente_telefono'], 0, 1)
        
        if pedido['cliente_direccion']:
            pdf.set_font('Arial', '', 9)
            pdf.cell(20, 4, "Direccion:", 0, 0)
            pdf.set_font('Arial', 'B', 9)
            pdf.multi_cell(0, 4, pedido['cliente_direccion'])
        
        pdf.ln(2)
        pdf.set_line_width(0.3)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(3)
        
        # ========== DETALLE DE PRODUCTOS ==========
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 4, "DETALLE DE PRODUCTOS", 0, 1, 'C')
        pdf.ln(1)
        pdf.set_line_width(0.2)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(2)
        
        subtotal_general = 0
        for producto in productos:
            nombre = producto['producto_nombre']
            precio_unit = float(producto['precio_unitario'])
            cantidad = producto['cantidad']
            subtotal = precio_unit * cantidad
            subtotal_general += subtotal
            
            pdf.set_font('Arial', 'B', 9)
            pdf.multi_cell(0, 4, nombre, 0, 'L')
            
            pdf.set_font('Arial', '', 8)
            pdf.cell(45, 4, f"  {cantidad} x Bs {precio_unit:.2f}", 0, 0, 'L')
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(25, 4, f"Bs {subtotal:.2f}", 0, 1, 'R')
            pdf.ln(1)
        
        # ========== CÁLCULOS IVA ==========
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
        
        pdf.set_font('Arial', 'B', 10)
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
        
        # ========== PIE DE PÁGINA ==========
        pdf.set_font('Arial', 'I', 8)
        pdf.multi_cell(0, 4, "Esta factura es valida como comprobante de compra.", 0, 'C')
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "Gracias por su compra!", 0, 1, 'C')
        
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 4, "Lo esperamos pronto", 0, 1, 'C')
        
        pdf.set_font('Arial', 'I', 7)
        pdf.cell(0, 3, "www.mitienda.com", 0, 1, 'C')
        
        # ========== GUARDAR PDF ==========
        facturas_dir = "facturas"
        if not os.path.exists(facturas_dir):
            os.makedirs(facturas_dir)
        
        filename = os.path.join(facturas_dir, f"factura_{pedido['id']}.pdf")
        pdf.output(filename)
        
        return filename
        
    except Exception as e:
        print(f"Error al generar factura: {e}")
        return None
    finally:
        cursor.close()
        conn.close()