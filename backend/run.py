from app import create_app
import logging

app = create_app()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6565, debug=True) 