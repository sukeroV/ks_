from datetime import timedelta
from pytz import timezone

class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/ks_db'
    CHINA_TZ = timezone('Asia/Shanghai')  # 添加中国时区
    PORT = 6565