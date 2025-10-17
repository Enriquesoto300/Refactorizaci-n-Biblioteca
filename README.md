# Sistema de Gestión de Biblioteca con Autenticación

Este es un sistema de gestión para una biblioteca desarrollado en **Python**. Permite administrar libros, usuarios y préstamos a través de una interfaz de línea de comandos (CLI).  
La aplicación cuenta con un sistema de autenticación seguro basado en roles y utiliza **hashing** para el almacenamiento de contraseñas.

---

## Características Principales

### Autenticación Segura
Sistema de login con roles (**admin**, **user**).

### Hashing de Contraseñas
Las contraseñas se almacenan de forma segura utilizando el algoritmo **bcrypt**.

### Gestión de Libros
- Registrar nuevos libros (solo admin).
- Listar todos los libros.
- Buscar libros por título o autor.

### Gestión de Usuarios (Lectores)
- Registrar nuevos usuarios lectores (solo admin).
- Listar todos los usuarios.
- Buscar usuarios por nombre.

### Gestión de Préstamos
- Registrar un nuevo préstamo (solo admin).
- Registrar la devolución de un libro (solo admin).
- Listar todos los préstamos activos.

### Configuración Automática
El sistema crea y configura automáticamente la tabla de cuentas en la base de datos la primera vez que se ejecuta.

### Registro de Eventos
Todas las acciones importantes, como inicios de sesión y registros, se guardan en el archivo **biblioteca.log**.

### Interfaz Amigable
La interfaz de usuario en la terminal es limpia, se actualiza en cada paso y hace pausas para mejorar la legibilidad.

---

## Tecnologías Utilizadas

- **Lenguaje:** Python 3  
- **Base de Datos:** MySQL  
- **Librerías de Python:**
  - `mysql-connector-python` → Conexión con la base de datos.  
  - `bcrypt` → Hasheo de contraseñas.  
  - `getpass` → Entrada segura de contraseñas.

---

## Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### 1. Requisitos Previos
- Tener **Python 3** instalado.  
- Tener un servidor de **MySQL** instalado y en ejecución.

### 2. Clonar el Repositorio
```bash
git clone https://github.com/Enriquesoto300/Refactorizaci-n-Biblioteca.git
cd Refactorizaci-n-Biblioteca
```

### 3. Instalar Dependencias
Instala las librerías de Python necesarias usando `pip`:

```bash
pip install mysql-connector-python bcrypt
```

### 4. Configurar la Base de Datos
Ejecuta el script SQL proporcionado (**schema_y_datos.sql**) en tu cliente de MySQL.  
Este script creará la base de datos **biblioteca**, las tablas necesarias (**libros**, **usuarios**, **prestamos**) y las llenará con datos de ejemplo.

### 5. Configurar la Conexión
Abre el archivo **Hash.py** (o como hayas nombrado el script principal) y modifica el diccionario `DB_CONFIG` con tus credenciales de MySQL:

```python
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "toor",
    "database": "biblioteca"
}
```

---

## Uso

1. Abre una terminal en el directorio del proyecto.  
2. Ejecuta el programa con el siguiente comando:

```bash
python Hash.py
```

La primera vez que lo ejecutes, el programa configurará la tabla **cuentas** y creará dos usuarios por defecto para el sistema de login.

### Inicia sesión con una de las siguientes credenciales:

**Administrador**
```
Usuario: admin
Contraseña: admin123
```

**Usuario Estándar**
```
Usuario: user
Contraseña: user123
```

Una vez dentro, navega por los menús para utilizar las diferentes funcionalidades del sistema.

---

Este README fue generado para el proyecto de gestión de biblioteca.
