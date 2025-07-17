# 🚀 Docker Compose Commands for FastAPI + Celery + Manim Stack

This guide covers all essential Docker Compose commands and helper scripts for managing your development and production services.

---

## 🔧 Basic Service Commands

| Command                         | Description                          |
|----------------------------------|--------------------------------------|
| `docker-compose up`             | Start all services                   |
| `docker-compose up -d`          | Start services in the background     |
| `docker-compose down`           | Stop and remove all containers       |
| `docker-compose restart`        | Restart all running services         |
| `docker-compose build`          | Build/rebuild all images             |
| `docker-compose up --build`     | Build and start fresh                |

---

## 📈 Logs

| Command                                 | Description                        |
|------------------------------------------|------------------------------------|
| `docker-compose logs`                   | Show all logs                      |
| `docker-compose logs -f`                | Follow all logs                    |
| `docker-compose logs fastapi`           | View logs for FastAPI service      |
| `docker-compose logs celery`            | View logs for Celery service       |
| `docker-compose logs flower`            | View Flower dashboard logs         |

---

## 📦 Shell Access

| Command                             | Description                         |
|--------------------------------------|-------------------------------------|
| `docker-compose exec fastapi bash`  | Open shell in FastAPI container     |
| `docker-compose exec celery sh`     | Open shell in Celery container      |
| `docker-compose exec redis redis-cli` | Connect to Redis CLI inside container |

---

## ⚖️ Scaling Workers

| Command                                      | Description                        |
|-----------------------------------------------|------------------------------------|
| `docker-compose up --scale celery=3 -d`       | Start 3 Celery worker containers   |
| `docker-compose up --scale celery=1 -d`       | Scale down to 1 worker             |

---

## 🧹 Cleanup

| Command                                     | Description                        |
|----------------------------------------------|------------------------------------|
| `docker-compose down -v`                   | Stop all and remove volumes        |
| `docker system prune -af --volumes`        | Clean up all unused resources      |

---