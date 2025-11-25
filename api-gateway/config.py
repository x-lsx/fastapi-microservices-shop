class Settings:
    USER_SERVICE_URL = "http://users-service:8000"
    PRODUCT_SERVICE_URL="http://products-service:8000"
    CART_SERVICE_URL="http://cart-service:8000"
    ORDER_SERVICE_URL="http://orders-service:8000"
    SECRET_KEY = "c43b9ce695290281592492d4eefe4ee0"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
settings = Settings()