from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
import hashlib
from itsdangerous import URLSafeSerializer

# Crea un serializer con una clave secreta
serializer = URLSafeSerializer('chantoromacadamianuez')  # Reemplaza 'clave_secreta' con tu propia clave secreta


app = Flask(__name__)

def update_product_stock(product_id, new_stock):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE Productos SET Stock = %s WHERE ProductoID = %s", (new_stock, product_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating product stock in database: {e}")
        return False

def get_connection():
    return mysql.connector.connect(
        host='sql.freedb.tech',
        user='freedb_admin2134',
        password='mKXWrKQ7DK*E8D?',
        database='freedb_Chantoro'
    )

def get_products_from_database():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Productos")
        products = cursor.fetchall()
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        print(f"Error getting products from database: {e}")
        return []

def delete_product_from_database(product_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Productos WHERE ProductoID = %s", (product_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting product from database: {e}")
        return False

def add_product_to_database(product_data):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Productos (NombreProducto, Descripcion, Precio, Stock) VALUES (%s, %s, %s, %s)", (product_data['NombreProducto'], product_data['Descripcion'], product_data['Precio'], product_data['Stock']))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error adding product to database: {e}")
        return False

def update_product_in_database(product_id, product_data):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE Productos SET NombreProducto = %s, Descripcion = %s, Precio = %s, Stock = %s WHERE ProductoID = %s", (product_data['NombreProducto'], product_data['Descripcion'], product_data['Precio'], product_data['Stock'], product_id))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating product in database: {e}")
        return False

@app.route('/products', methods=['GET', 'POST', 'DELETE', 'PUT'])
def products():
    if request.method == 'GET':
        products = get_products_from_database()
        return jsonify(products)
    elif request.method == 'DELETE':
        product_id = request.args.get('productId')
        if product_id is None:
            return jsonify({'error': 'Product ID is required'}), 400
        success = delete_product_from_database(product_id)
        if success:
            return jsonify({'message': 'Product deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete product'}), 500
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        success = add_product_to_database(data)
        if success:
            return jsonify({'message': 'Product added successfully'})
        else:
            return jsonify({'error': 'Failed to add product'}), 500
    elif request.method == 'PUT':
        data = request.json
        product_id = data.get('ProductoID')
        if product_id is None:
            return jsonify({'error': 'Product ID is required'}), 400
        success = update_product_in_database(product_id, data)
        if success:
            return jsonify({'message': 'Product updated successfully'})
        else:
            return jsonify({'error': 'Failed to update product'}), 500
        
@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.json
        customer_id = data['customer_id']
        products = data['products']

        connection = get_connection()
        cursor = connection.cursor()
        
        # Insertar un nuevo pedido
        cursor.execute("INSERT INTO Pedidos (FechaPedido, ClienteID, Surtido) VALUES (%s, %s, %s)", (datetime.now(), customer_id, 0))
        order_id = cursor.lastrowid
        
        # Insertar detalles del pedido
        for product in products:
            cursor.execute("INSERT INTO DetallesPedidos (PedidoID, ProductoID, Cantidad, PrecioUnitario, Total) VALUES (%s, %s, %s, %s, %s)", (order_id, product['id'], product['cantidad'], product['precio'], product['total']))
        
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'success': True, 'order_id': order_id}), 200
    except Exception as e:
        print(f"Error creating order in database: {e}")
        return jsonify({'error': 'Failed to create order'}), 500
    
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT Pedidos.*, Clientes.Nombre, Clientes.Apellido 
            FROM Pedidos 
            JOIN Clientes ON Pedidos.ClienteID = Clientes.ClienteID
        """)
        orders = cursor.fetchall()

        for order in orders:
            with connection.cursor(dictionary=True) as product_cursor:
                product_cursor.execute("""
                    SELECT Productos.NombreProducto, DetallesPedidos.Cantidad, DetallesPedidos.PrecioUnitario, DetallesPedidos.Total 
                    FROM DetallesPedidos 
                    JOIN Productos ON DetallesPedidos.ProductoID = Productos.ProductoID 
                    WHERE DetallesPedidos.PedidoID = %s
                """, (order['PedidoID'],))
                order['productos'] = product_cursor.fetchall()

        return jsonify(orders)
    except Exception as e:
        print(f"Error getting orders from database: {e}")
        return jsonify({'error': 'Failed to get orders'}), 500
    finally:
        if connection:
            connection.close()  # Asegurarse de cerrar la conexión al finalizar


# Función para obtener una conexión a la base de datos MySQL
def get_connection():
    try:
        connection = mysql.connector.connect(
            host='sql.freedb.tech',
        user='freedb_admin2134',
        password='mKXWrKQ7DK*E8D?',
        database='freedb_Chantoro'
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Función para obtener todos los clientes de la base de datos
def get_clients_from_database():
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Clientes")
            clients = cursor.fetchall()
            cursor.close()
            connection.close()
            return clients
        else:
            return []
    except Exception as e:
        print(f"Error getting clients from database: {e}")
        return []

# Función para agregar un cliente a la base de datos con token generado automáticamente
def add_client_to_database(client_data):
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            # Genera un token único para el cliente basado en su correo electrónico
            token = serializer.dumps(client_data['CorreoElectronico'])
            cursor.execute("INSERT INTO Clientes (Nombre, Apellido, CorreoElectronico, Telefono, Contrasena, Token, Direccion) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (client_data['Nombre'], client_data['Apellido'], client_data['CorreoElectronico'], client_data['Telefono'], client_data['Contrasena'], token, client_data['Direccion']))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error adding client to database: {e}")
        return False
    
@app.route('/register', methods=['POST'])
def register():
    client_data = request.json
    success = add_client_to_database(client_data)
    if success:
        return jsonify({"message": "Cliente registrado exitosamente"}), 200
    else:
        return jsonify({"message": "Error al registrar cliente"}), 500

# Función para actualizar un cliente en la base de datos
def update_client_in_database(client_id, client_data):
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE Clientes SET Nombre=%s, Apellido=%s, CorreoElectronico=%s, Telefono=%s, Contrasena=%s, Token=%s, Direccion=%s WHERE ClienteID=%s",
                           (client_data['Nombre'], client_data['Apellido'], client_data['CorreoElectronico'], client_data['Telefono'], client_data['Contrasena'], client_data['Token'], client_data['Direccion'], client_id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error updating client in database: {e}")
        return False

# Función para eliminar un cliente de la base de datos
def delete_client_from_database(client_id):
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Clientes WHERE ClienteID=%s", (client_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error deleting client from database: {e}")
        return False

@app.route('/clients', methods=['GET'])
def clients():
    if request.method == 'GET':
        clients = get_clients_from_database()
        return jsonify(clients)

@app.route('/clients', methods=['POST'])
def add_client():
    data = request.json
    success = add_client_to_database(data)
    if success:
        return jsonify({'message': 'Client added successfully'})
    else:
        return jsonify({'error': 'Failed to add client'}), 500

@app.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.json
    success = update_client_in_database(client_id, data)
    if success:
        return jsonify({'message': 'Client updated successfully'})
    else:
        return jsonify({'error': 'Failed to update client'}), 500

@app.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    success = delete_client_from_database(client_id)
    if success:
        return jsonify({'message': 'Client deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete client'}), 500
    
#Funciones para la agenda


def get_events_from_database():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Agenda")
        events = cursor.fetchall()
        cursor.close()
        connection.close()
        return events
    except Exception as e:
        print(f"Error getting events from database: {e}")
        return []

def add_event_to_database(event_data):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Agenda (FechaInicio, FechaFin, Descripcion) VALUES (%s, %s, %s)", (event_data['FechaInicio'], event_data['FechaFin'], event_data['Descripcion']))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error adding event to database: {e}")
        return False

def delete_event_from_database(event_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Agenda WHERE EventoID = %s", (event_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting event from database: {e}")
        return False

@app.route('/agenda', methods=['GET', 'POST'])
def agenda():
    if request.method == 'GET':
        events = get_events_from_database()
        return jsonify(events)
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        success = add_event_to_database(data)
        if success:
            return jsonify({'message': 'Event added successfully'})
        else:
            return jsonify({'error': 'Failed to add event'}), 500

@app.route('/agenda/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    success = delete_event_from_database(event_id)
    if success:
        return jsonify({'message': 'Event deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete event'}), 500
    
#Carrito
# Configuración de la base de datos
db_config = {
    'host': 'sql.freedb.tech',
    'user': 'freedb_admin2134',
    'password': 'mKXWrKQ7DK*E8D?',
    'database': 'freedb_Chantoro'
}
# Ruta para actualizar el stock de un producto
def update_product_stock(product_id, new_stock):
    try:
        # Conectar a la base de datos
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor()

            # Verificar si el producto existe
            cursor.execute("SELECT ProductoID FROM Productos WHERE ProductoID = %s", (product_id,))
            if not cursor.fetchone():
                return False  # Producto no encontrado

            # Actualizar el stock del producto en la base de datos
            update_query = "UPDATE Productos SET Stock = %s WHERE ProductoID = %s"
            cursor.execute(update_query, (new_stock, product_id))
            conn.commit()

            return True  # Actualización exitosa
    except mysql.connector.Error as e:
        print("Error al actualizar el stock:", str(e))
        return False

@app.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        new_stock = data.get('stock')
        if new_stock is None:
            return jsonify({"error": "No se proporcionó el nuevo stock"}), 400

        if update_product_stock(product_id, new_stock):
            return jsonify({"message": f"Stock actualizado para el producto con ID {product_id}"}), 200
        else:
            return jsonify({"error": "Producto no encontrado o error al actualizar el stock"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Función para obtener las transacciones de contabilidad desde la base de datos
def get_contabilidad_from_database():
    try:
        # Conectar a la base de datos
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            # Ejecutar la consulta SQL para obtener las transacciones de contabilidad
            cursor.execute("SELECT * FROM Contabilidad")
            # Obtener todas las filas como un diccionario
            contabilidad = cursor.fetchall()
            return contabilidad
    except mysql.connector.Error as e:
        print("Error al obtener la contabilidad desde la base de datos:", str(e))
        return []

# Ruta para obtener las transacciones de contabilidad
@app.route('/contabilidad', methods=['GET'])
def obtener_contabilidad():
    # Obtener las transacciones de contabilidad desde la base de datos
    contabilidad = get_contabilidad_from_database()
    # Devolver las transacciones de contabilidad como respuesta en formato JSON
    return jsonify(contabilidad)
# Ruta para agregar una nueva transacción a la base de datos
@app.route('/contabilidad', methods=['POST'])
def agregar_transaccion():
    try:
        # Obtener los datos de la nueva transacción desde la solicitud JSON
        data = request.json
        fecha_transaccion = data.get('FechaTransaccion')
        tipo = data.get('Tipo')
        monto = data.get('Monto')
        descripcion = data.get('Descripcion')

        # Validar que se proporcionen todos los campos necesarios
        if not (fecha_transaccion and tipo and monto and descripcion):
            return jsonify({'error': 'Se requieren todos los campos: FechaTransaccion, Tipo, Monto, Descripcion'}), 400

        # Insertar la nueva transacción en la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Contabilidad (FechaTransaccion, Tipo, Monto, Descripcion) VALUES (%s, %s, %s, %s)",
                       (fecha_transaccion, tipo, monto, descripcion))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Transacción agregada correctamente'}), 200
    except Exception as e:
        print(f"Error al agregar la transacción: {e}")
        return jsonify({'error': 'Error al agregar la transacción'}), 500
    
    
@app.route('/contabilidad/<int:transaccion_id>', methods=['DELETE'])
def eliminar_transaccion(transaccion_id):
    try:
        # Conectar a la base de datos
        with mysql.connector.connect(**db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            # Ejecutar la consulta SQL para eliminar la transacción
            cursor.execute("DELETE FROM Contabilidad WHERE TransaccionID = %s", (transaccion_id,))
            conn.commit()
            return jsonify({'message': 'Transacción eliminada correctamente'}), 200
    except mysql.connector.Error as e:
        print("Error al eliminar la transacción:", str(e))
        return jsonify({'error': 'Error al eliminar la transacción'}), 500

# Función para autenticar usuarios y clientes
def autenticar(identificacion, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Buscar en la tabla Usuarios
        cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = %s AND Contraseña = %s", (identificacion, password))
        usuario = cursor.fetchone()
        if usuario:
            return usuario['UsuarioID'], 'usuario'  # Retornar el ID del usuario y el tipo de usuario

        # Si no es un usuario, buscar en la tabla Clientes
        cursor.execute("SELECT * FROM Clientes WHERE CorreoElectronico = %s AND Contrasena = %s", (identificacion, password))
        cliente = cursor.fetchone()
        if cliente:
            return cliente['ClienteID'], 'cliente'
        else:
            return None, None
    except Exception as e:
        print("Error al autenticar:", e)
        return None, None

# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    identificacion = data.get('identificacion')
    password = data.get('password')
    cliente_id, tipo_usuario = autenticar(identificacion, password)
    if cliente_id:
        usuario_id, tipo_usuario = autenticar(identificacion, password)  # Obtener el ID del usuario
        return jsonify({'message': 'Inicio de sesión exitoso', 'ClienteID': cliente_id, 'UsuarioID': usuario_id, 'token': 'TOKEN_AQUI', 'tipo_usuario': tipo_usuario})
    else:
        return jsonify({'error': 'Identificación o contraseña incorrectas'}), 401

# Ruta para crear un nuevo pedido
@app.route('/hacer_pedido', methods=['POST'])
def crear_pedido():
    try:
        data = request.json
        cliente_id = 1  # ClienteID establecido como 1
        productos = data.get('productos')

        # Conexión a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insertar un nuevo pedido en la tabla Pedidos
        cursor.execute("INSERT INTO Pedidos (FechaPedido, ClienteID, Surtido) VALUES (NOW(), %s, %s)", (cliente_id, False))
        pedido_id = cursor.lastrowid

        # Insertar los detalles del pedido en la tabla DetallesPedidos
        for producto in productos:
            cursor.execute("INSERT INTO DetallesPedidos (PedidoID, ProductoID, Cantidad, PrecioUnitario, Total) VALUES (%s, %s, %s, %s, %s)",
                           (pedido_id, producto['ProductoID'], producto['Cantidad'], producto['PrecioUnitario'], producto['Total']))

        # Confirmar la transacción
        conn.commit()

        # Cerrar conexión y cursor
        cursor.close()
        conn.close()

        return jsonify({'message': 'Pedido creado exitosamente', 'pedido_id': pedido_id}), 201

    except Exception as e:
        print("Error al crear pedido:", e)
        # Revertir la transacción en caso de error
        conn.rollback()
        return jsonify({'error': 'Error al crear pedido'}), 500



#Notificaciones

@app.route('/notifications', methods=['GET'])
def get_notifications():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Notificaciones")
        notifications = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(notifications)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notifications/<int:notification_id>', methods=['PUT'])
def mark_notification_as_read(notification_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE Notificaciones SET Leido = 1 WHERE NotificacionID = %s", (notification_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Notification marked as read successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
