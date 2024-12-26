from app import create_app, db
from app.models import User, ExerciseSet, PracticeRecord, Expression, AnswerRecord, ErrorRecord

app = create_app()

def init_db():
    with app.app_context():
        # 删除所有现有表
        db.drop_all()
        # 创建所有表
        db.create_all()
        print("数据库表已创建完成！")

        # 创建测试用户（可选）
        test_user = User(
            user_id='test001',
            name='测试用户',
            id_card='110101200001011234',
            grade=3,
            phone='13800138000'
        )
        test_user.password = '123456'  # 密码会自动加密
        db.session.add(test_user)
        db.session.commit()
        print("测试用户已创建！")

if __name__ == "__main__":
    init_db() 