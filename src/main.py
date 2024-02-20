from fastapi import FastAPI

from src.internal.routes import item, user

# Создаем экземпляр приложения FastAPI
app = FastAPI(
    title="Проект для демонстрации модульного и интеграционного тестирования."
)

# Подключем роутеры items и users
app.include_router(user.router)
app.include_router(item.router)
