# FeedIA: Feedback y Predicción Inteligente para tu Negocio

## 🚀 Demo
Credenciales de prueba:
- **Usuario Común**
  - Usuario: usuariocomun
  - Contraseña: 123456
- **Usuario Negocio**
  - Usuario: usuarionegocio
  - Contraseña: 123456

## 📝 Descripción
FeedIA es una plataforma web que transforma la interacción cliente-negocio en valor estratégico. Los clientes pueden compartir opiniones escaneando un código QR, recibiendo puntos canjeables como recompensa.

### Características Principales
- 📱 Feedback rápido y anónimo vía QR
- 🤖 Análisis de sentimientos en tiempo real con IA
- 💰 Sistema de puntos canjeables
- 📊 Dashboard interactivo para negocios
- 🔮 Predicción de ventas y tendencias

## 🛠️ Tecnologías
- Django 5.1.4
- MySQL/PostgreSQL
- Transformers (BERT)
- Redis (para caché y Celery)
- Celery (procesamiento asíncrono)
- Docker (opcional)
- Whitenoise (archivos estáticos)

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.10+
- MySQL
- Redis (opcional, para producción)
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/feedia.git
cd feedia
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# Configuración local
ENVIRONMENT=local
DEBUG=True
SECRET_KEY=your-secret-key-here

# Base de datos MySQL
DB_NAME=feedia
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306

# Redis y Celery (opcional, para producción)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
```

### 5. Configurar Base de Datos
```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE feedia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Ejecutar migraciones
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

## 🐳 Configuración con Docker (Opcional)

### 1. Construir y Ejecutar Contenedores
```bash
docker-compose up -d
```

### 2. Ejecutar Migraciones en Docker
```bash
docker-compose exec web python manage.py migrate
```

### 3. Crear Superusuario en Docker
```bash
docker-compose exec web python manage.py createsuperuser
```

## 🧠 Modelo de IA
FeedIA utiliza el modelo BERT para análisis de sentimientos en español. La primera vez que se ejecute, descargará automáticamente el modelo (aproximadamente 500MB).

## 📝 Notas Importantes
- En desarrollo local, se usa el caché en memoria
- En producción, se recomienda usar Redis para caché
- Los archivos estáticos se sirven con Whitenoise
- Las tareas asíncronas requieren Celery+Redis en producción

## 🔧 Solución de Problemas Comunes
1. **Error de MySQL**: Asegúrate de tener instalado `mysql-connector-python`
2. **Error de memoria con BERT**: Necesitas al menos 2GB de RAM libre
3. **Errores de archivos estáticos**: Ejecuta `collectstatic`

## 📚 Documentación Adicional
- [Django](https://docs.djangoproject.com/)
- [Transformers](https://huggingface.co/docs/transformers/index)
- [Redis](https://redis.io/docs/)
- [Celery](https://docs.celeryq.dev/en/stable/)

## ✨ Autor
Mauricio Arce - [LinkedIn](https://www.linkedin.com/in/mauricioarcez/)

