from app import app
from config import Config
app.config.from_object(Config)

if __name__ == "__main__":
    app.run(host='192.168.1.108')