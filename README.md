# 🥬 Backend Rapidín Vegano

## 🧾 Descripción del Proyecto

En este laboratorio se abordó el desarrollo de una aplicación web para la gestión de ventas e inventario, actuando como una **caja registradora** para supermercados especializados. La solución se construyó aplicando principios de **programación funcional** y empleando un stack tecnológico moderno:

- **Frontend:** React con componentes reutilizables.
- **Backend:** Flask, como framework web liviano y flexible.
- **Almacenamiento en memoria:** Redis, para operaciones de alta velocidad y baja latencia.

### 🧠 Características destacadas:

- **Interfaz en React**: Modular, reutilizable y funcional, siguiendo principios como inmutabilidad y funciones puras.
- **API RESTful en Flask**: Con separación clara entre rutas, lógica de negocio y persistencia.
- **Alto rendimiento con Redis**: Cache para stock y ventas recientes, disminuyendo significativamente la latencia.

---

## 🚀 Tecnologías

- Python 3.10
- Flask
- Redis
- Docker / Docker Compose

---

## 🔌 Puerto del Backend

Este backend corre en el puerto **`5000`**, y expone endpoints RESTful para registrar ventas, consultar productos, y actualizar inventarios.

---

## 📁 Estructura del Proyecto

Para que el entorno funcione correctamente con Docker Compose, asegúrate de que las carpetas del frontend y backend estén organizadas como se muestra a continuación:

proyecto-raiz:
- docker-compose.yml
- Stock-frontend            
- stock-products-backend   


---

## 🐳 Ejecución con Docker Compose

Utiliza el siguiente archivo `docker-compose.yml` en la raíz del proyecto:

```yaml
version: '3.8'

services:
  frontend: 
    build: ./Stock-frontend/rapidin
    ports:
      - "3000:3000"
    networks:
      - g2net
    environment:
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - ./Stock-frontend/rapidin:/app
      - frontend_node_modules:/app/node_modules
    depends_on:
      - backend

  backend:
    build: ./stock-products-backend
    ports:
      - "5000:5000"
    networks:
      - g2net
    environment:
      - REDIS_HOST=redis
      - FLASK_ENV=development
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    networks:
      - g2net

volumes:
  pgdata:
  frontend_node_modules:

networks:
  g2net: {}

