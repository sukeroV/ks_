from app import create_app
import logging
import app.config as config

app = create_app()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.Config.PORT, debug=True)