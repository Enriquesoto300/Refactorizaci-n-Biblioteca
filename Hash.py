import mysql.connector
from datetime import datetime
import getpass
import bcrypt
import sys
import os
import platform

# ============================================================
# FUNCIONES DE UTILIDAD PARA LA INTERFAZ
# ============================================================
def limpiar_pantalla():
    """Limpia la pantalla de la terminal (compatible con Windows, Linux, macOS)."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def pausar_y_continuar():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\nPresiona Enter para continuar...")

# ============================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================================
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "toor",
    "database": "biblioteca"
}

# ============================================================
# CLASE CONEXIÓN A BASE DE DATOS
# ============================================================
class ConexionBD:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as e:
            if e.errno == 1049:
                print(f"AVISO: La base de datos '{DB_CONFIG['database']}' no existe.")
                print("Por favor, créala usando el script SQL proporcionado y luego ejecuta este programa.")
            else:
                print(f"❌ Error de conexión a la base de datos: {e}")
            self.conn = None
            self.cursor = None

    def ejecutar(self, query, params=None):
        if self.cursor:
            self.cursor.execute(query, params or ())

    def obtener_todos(self):
        return self.cursor.fetchall()

    def obtener_uno(self):
        return self.cursor.fetchone()

    def confirmar(self):
        self.conn.commit()

    def cerrar(self):
        if self.conn:
            self.conn.close()

# ============================================================
# FUNCIÓN DE LOGS
# ============================================================
def log_evento(mensaje, usuario="Sistema"):
    try:
        with open("biblioteca.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{usuario}] {mensaje}\n")
    except IOError as e:
        print(f"No se pudo escribir en el archivo de log: {e}")

# ============================================================
# CONFIGURACIÓN INICIAL (INTEGRADA)
# ============================================================
def setup_database_accounts():
    try:
        limpiar_pantalla()
        print("--- Realizando configuración inicial de cuentas ---")
        db = ConexionBD()
        if not db.conn: return

        db.ejecutar("""
            CREATE TABLE IF NOT EXISTS cuentas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin', 'user'))
            )
        """)
        print("✅ Tabla 'cuentas' verificada/creada.")

        usuarios = [('admin', 'admin123', 'admin'), ('user', 'user123', 'user')]
        for nombre, password, rol in usuarios:
            db.ejecutar("SELECT id FROM cuentas WHERE nombre_usuario = %s", (nombre,))
            if db.obtener_uno() is None:
                print(f"Creando usuario por defecto: {nombre}...")
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                db.ejecutar(
                    "INSERT INTO cuentas (nombre_usuario, password_hash, rol) VALUES (%s, %s, %s)",
                    (nombre, hashed_password.decode('utf-8'), rol)
                )
                print(f"✅ Usuario '{nombre}' creado con la contraseña '{password}'.")
            else:
                print(f"ℹ️ El usuario '{nombre}' ya existe.")
        
        db.confirmar()
        db.cerrar()
        print("\n🎉 Configuración de cuentas completada.")
        pausar_y_continuar()
    except mysql.connector.Error as e:
        print(f"❌ Error durante la configuración de cuentas: {e}")

def verificar_y_preparar_db():
    try:
        db = ConexionBD()
        if not db.conn:
             sys.exit(1)
        
        db.ejecutar("SHOW TABLES LIKE 'cuentas'")
        if db.obtener_uno() is None:
            db.cerrar()
            setup_database_accounts()
        else:
            db.cerrar()
    except mysql.connector.Error as e:
        print(f"❌ No se pudo verificar la base de datos. Error: {e}")
        sys.exit(1)

# ============================================================
# CLASE DE AUTENTICACIÓN Y SESIÓN
# ============================================================
class Autenticacion:
    def __init__(self):
        self.usuario_actual = None
        self.rol_actual = None

    def _verificar_password(self, password_plano, password_hash):
        return bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8'))

    def iniciar_sesion(self):
        limpiar_pantalla()
        print("--- INICIO DE SESIÓN ---")
        nombre_usuario = input("Usuario: ").strip()
        password = getpass.getpass("Contraseña: ")

        db = ConexionBD()
        if not db.conn: return False
            
        db.ejecutar("SELECT * FROM cuentas WHERE nombre_usuario = %s", (nombre_usuario,))
        cuenta = db.obtener_uno()
        db.cerrar()

        if cuenta and self._verificar_password(password, cuenta['password_hash']):
            self.usuario_actual = cuenta['nombre_usuario']
            self.rol_actual = cuenta['rol']
            log_evento(f"Inicio de sesión exitoso", self.usuario_actual)
            limpiar_pantalla()
            print(f"✅ Bienvenido, {self.usuario_actual} (Rol: {self.rol_actual}).")
            pausar_y_continuar()
            return True
        else:
            log_evento(f"Intento de inicio de sesión fallido para '{nombre_usuario}'")
            print("❌ Usuario o contraseña incorrectos.")
            pausar_y_continuar()
            return False

    def cerrar_sesion(self):
        if self.usuario_actual:
            log_evento(f"Cierre de sesión", self.usuario_actual)
            self.usuario_actual = None
            self.rol_actual = None
            print(f"👋 Sesión cerrada.")
            pausar_y_continuar()
        
    def tiene_permiso(self, rol_requerido):
        if rol_requerido == 'admin':
            return self.rol_actual == 'admin'
        if rol_requerido == 'user':
            return self.rol_actual in ('user', 'admin')
        return False

# ============================================================
# CLASES DE DOMINIO (Libro, Usuario, Prestamo)
# ============================================================
class Libro:
    @staticmethod
    def registrar():
        print("--- REGISTRAR NUEVO LIBRO ---")
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        try: anio = int(input("Año: "))
        except ValueError: print("❌ Año inválido."); return
        if not titulo or not autor: print("❌ Todos los campos son obligatorios."); return
        db = ConexionBD()
        db.ejecutar("INSERT INTO libros (titulo, autor, anio, disponible) VALUES (%s, %s, %s, %s)", (titulo, autor, anio, True))
        db.confirmar()
        db.cerrar()
        log_evento(f"Libro registrado: {titulo}")
        print("✅ Libro registrado correctamente.")

    @staticmethod
    def listar():
        db = ConexionBD()
        db.ejecutar("SELECT * FROM libros")
        libros = db.obtener_todos()
        print("--- LISTA DE LIBROS ---")
        for libro in libros:
            estado = "Disponible" if libro["disponible"] else "Prestado"
            print(f"[{libro['id']}] {libro['titulo']} - {libro['autor']} ({libro['anio']}) - {estado}")
        db.cerrar()

    @staticmethod
    def buscar():
        print("--- BUSCAR LIBRO ---")
        palabra = input("Buscar por título o autor: ").strip()
        db = ConexionBD()
        db.ejecutar("SELECT * FROM libros WHERE titulo LIKE %s OR autor LIKE %s", (f"%{palabra}%", f"%{palabra}%"))
        resultados = db.obtener_todos()
        print("\n--- RESULTADOS DE BÚSQUEDA ---")
        if not resultados: print("❌ No se encontraron libros.")
        else:
            for libro in resultados:
                estado = "Disponible" if libro["disponible"] else "Prestado"
                print(f"[{libro['id']}] {libro['titulo']} - {libro['autor']} ({libro['anio']}) - {estado}")
        db.cerrar()

class Usuario:
    @staticmethod
    def registrar():
        print("--- REGISTRAR NUEVO USUARIO (LECTOR) ---")
        nombre = input("Nombre del usuario: ").strip()
        tipo = input("Tipo (Alumno / Profesor / Otro): ").strip()
        if not nombre or not tipo: print("❌ Todos los campos son obligatorios."); return
        db = ConexionBD()
        db.ejecutar("INSERT INTO usuarios (nombre, tipo) VALUES (%s, %s)", (nombre, tipo))
        db.confirmar()
        db.cerrar()
        log_evento(f"Usuario (lector) registrado: {nombre}")
        print("✅ Usuario registrado correctamente.")

    @staticmethod
    def listar():
        db = ConexionBD()
        db.ejecutar("SELECT * FROM usuarios")
        usuarios = db.obtener_todos()
        print("--- LISTA DE USUARIOS (LECTORES) ---")
        for usuario in usuarios: print(f"[{usuario['id']}] {usuario['nombre']} - {usuario['tipo']}")
        db.cerrar()

    @staticmethod
    def buscar():
        print("--- BUSCAR USUARIO (LECTOR) ---")
        nombre = input("Buscar usuario por nombre: ").strip()
        db = ConexionBD()
        db.ejecutar("SELECT * FROM usuarios WHERE nombre LIKE %s", (f"%{nombre}%",))
        resultados = db.obtener_todos()
        print("\n--- RESULTADOS DE BÚSQUEDA ---")
        if not resultados: print("❌ No se encontraron usuarios.")
        else:
            for usuario in resultados: print(f"[{usuario['id']}] {usuario['nombre']} - {usuario['tipo']}")
        db.cerrar()

class Prestamo:
    @staticmethod
    def registrar():
        print("--- REGISTRAR NUEVO PRÉSTAMO ---")
        try:
            id_usuario = int(input("ID del usuario: "))
            id_libro = int(input("ID del libro: "))
        except ValueError: print("❌ IDs inválidos."); return
        db = ConexionBD()
        db.ejecutar("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
        if not db.obtener_uno(): print("❌ Usuario no encontrado."); db.cerrar(); return
        db.ejecutar("SELECT * FROM libros WHERE id = %s", (id_libro,))
        libro = db.obtener_uno()
        if not libro: print("❌ Libro no encontrado."); db.cerrar(); return
        if not libro["disponible"]: print("❌ El libro no está disponible."); db.cerrar(); return
        fecha = datetime.now().date()
        db.ejecutar("INSERT INTO prestamos (id_usuario, id_libro, fecha_prestamo, fecha_devolucion) VALUES (%s, %s, %s, NULL)", (id_usuario, id_libro, fecha))
        db.ejecutar("UPDATE libros SET disponible = %s WHERE id = %s", (False, id_libro))
        db.confirmar()
        db.cerrar()
        log_evento(f"Préstamo registrado: Usuario {id_usuario} - Libro {id_libro}")
        print("✅ Préstamo registrado correctamente.")

    @staticmethod
    def devolver():
        print("--- DEVOLVER LIBRO ---")
        try: id_prestamo = int(input("ID del préstamo a devolver: "))
        except ValueError: print("❌ ID inválido."); return
        db = ConexionBD()
        db.ejecutar("SELECT * FROM prestamos WHERE id = %s", (id_prestamo,))
        prestamo = db.obtener_uno()
        if not prestamo: print("❌ Préstamo no encontrado."); db.cerrar(); return
        if prestamo["fecha_devolucion"]: print("❌ El libro ya fue devuelto."); db.cerrar(); return
        fecha_dev = datetime.now().date()
        db.ejecutar("UPDATE prestamos SET fecha_devolucion = %s WHERE id = %s", (fecha_dev, id_prestamo))
        db.ejecutar("UPDATE libros SET disponible = %s WHERE id = %s", (True, prestamo["id_libro"]))
        db.confirmar()
        db.cerrar()
        log_evento(f"Devolución registrada: Préstamo {id_prestamo}")
        print("✅ Libro devuelto correctamente.")

    @staticmethod
    def listar_activos():
        db = ConexionBD()
        db.ejecutar("SELECT p.id, u.nombre, l.titulo, p.fecha_prestamo FROM prestamos p JOIN usuarios u ON p.id_usuario = u.id JOIN libros l ON p.id_libro = l.id WHERE p.fecha_devolucion IS NULL")
        prestamos = db.obtener_todos()
        print("--- PRÉSTAMOS ACTIVOS ---")
        if not prestamos: print("No hay préstamos activos.")
        else:
            for p in prestamos: print(f"[{p['id']}] {p['nombre']} -> {p['titulo']} (Desde: {p['fecha_prestamo']})")
        db.cerrar()

# ============================================================
# CLASE PRINCIPAL DEL SISTEMA (MENÚS)
# ============================================================
class SistemaBiblioteca:
    def __init__(self):
        self.auth = Autenticacion()

    def _ejecutar_accion(self, funcion, rol_requerido=None):
        limpiar_pantalla()
        if rol_requerido and not self.auth.tiene_permiso(rol_requerido):
            print("❌ Acceso denegado. Permisos de administrador requeridos.")
        else:
            funcion()
        pausar_y_continuar()

    def menu_libros(self):
        while True:
            limpiar_pantalla()
            print("--- MENÚ LIBROS ---")
            print("1. Registrar libro (Admin)")
            print("2. Listar libros")
            print("3. Buscar libro")
            print("4. Volver al menú principal")
            opcion = input("Selecciona una opción: ")
            if opcion == "1": self._ejecutar_accion(Libro.registrar, 'admin')
            elif opcion == "2": self._ejecutar_accion(Libro.listar)
            elif opcion == "3": self._ejecutar_accion(Libro.buscar)
            elif opcion == "4": break
            else: print("❌ Opción inválida."); pausar_y_continuar()

    def menu_usuarios(self):
        while True:
            limpiar_pantalla()
            print("--- MENÚ USUARIOS (LECTORES) ---")
            print("1. Registrar usuario (Admin)")
            print("2. Listar usuarios")
            print("3. Buscar usuario")
            print("4. Volver al menú principal")
            opcion = input("Selecciona una opción: ")
            if opcion == "1": self._ejecutar_accion(Usuario.registrar, 'admin')
            elif opcion == "2": self._ejecutar_accion(Usuario.listar)
            elif opcion == "3": self._ejecutar_accion(Usuario.buscar)
            elif opcion == "4": break
            else: print("❌ Opción inválida."); pausar_y_continuar()

    def menu_prestamos(self):
        while True:
            limpiar_pantalla()
            print("--- MENÚ PRÉSTAMOS ---")
            print("1. Registrar préstamo (Admin)")
            print("2. Devolver libro (Admin)")
            print("3. Ver préstamos activos")
            print("4. Volver al menú principal")
            opcion = input("Selecciona una opción: ")
            if opcion == "1": self._ejecutar_accion(Prestamo.registrar, 'admin')
            elif opcion == "2": self._ejecutar_accion(Prestamo.devolver, 'admin')
            elif opcion == "3": self._ejecutar_accion(Prestamo.listar_activos)
            elif opcion == "4": break
            else: print("❌ Opción inválida."); pausar_y_continuar()

    def menu_principal(self):
        while True:
            limpiar_pantalla()
            print(f"===== SISTEMA DE BIBLIOTECA (Usuario: {self.auth.usuario_actual}) =====")
            print("1. Gestión de Libros")
            print("2. Gestión de Usuarios (Lectores)")
            print("3. Gestión de Préstamos")
            print("4. Cerrar Sesión")
            print("5. Salir del sistema")
            opcion = input("Selecciona una opción: ")
            if opcion == "1": self.menu_libros()
            elif opcion == "2": self.menu_usuarios()
            elif opcion == "3": self.menu_prestamos()
            elif opcion == "4": self.auth.cerrar_sesion(); return "logout"
            elif opcion == "5": return "salir"
            else: print("❌ Opción inválida."); pausar_y_continuar()

    def ejecutar(self):
        limpiar_pantalla()
        print("Iniciando Sistema de Biblioteca...")
        verificar_y_preparar_db()
        while True:
            if not self.auth.usuario_actual:
                if not self.auth.iniciar_sesion():
                    limpiar_pantalla()
                    retry = input("¿Volver a intentar el inicio de sesión? (s/n): ").lower()
                    if retry != 's': break
                else:
                    if self.menu_principal() == "salir": break
            else:
                 if self.menu_principal() == "salir": break
        
        limpiar_pantalla()
        print("👋 Saliendo del sistema... ¡Hasta pronto!")

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    sistema = SistemaBiblioteca()
    sistema.ejecutar()
