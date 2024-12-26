from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """用户表：存储用户基本信息"""
    __tablename__ = 'user'
    user_id = db.Column(db.String(15), primary_key=True, comment='用户ID')
    name = db.Column(db.String(50), nullable=False, comment='用户姓名')
    id_card = db.Column(db.String(18), nullable=False, comment='身份证号')
    grade = db.Column(db.Integer, nullable=False, comment='年级')
    _password = db.Column('password', db.String(512), nullable=False, comment='加密密码')
    phone = db.Column(db.String(11), comment='电话号码')
    
    practice_records = db.relationship('PracticeRecord', backref='user', lazy=True)
    
    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def verify_password(self, password):
        return check_password_hash(self._password, password)
    
    __table_args__ = (
        {'comment': '用户信息表'}
    )

class ExerciseSet(db.Model):
    """习题集表：存储习题集基本信息"""
    __tablename__ = 'exercise_set'
    exercise_set_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='习题集ID')
    user_id = db.Column(db.String(15), db.ForeignKey('user.user_id'), nullable=True, comment='用户ID')
    total_expressions = db.Column(db.Integer, nullable=False, comment='总题目数')
    bracket_expressions = db.Column(db.Integer, nullable=False, default=0, comment='括号题目数')
    time_limit = db.Column(db.Integer, nullable=False, comment='时间限制(分钟)')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    operators = db.Column(db.String(1000), nullable=False, comment='运算符列表')
    operator_count = db.Column(db.Integer, nullable=False, comment='运算符数量')
    min_number = db.Column(db.Integer, nullable=False, comment='最小值')
    max_number = db.Column(db.Integer, nullable=False, comment='最大值')
    
    expressions = db.relationship('Expression', backref='exercise_set', lazy=True)
    practice_records = db.relationship('PracticeRecord', backref='exercise_set', lazy=True)
    
    __table_args__ = (
        db.CheckConstraint('total_expressions > 0', name='check_total_expressions'),
        db.CheckConstraint('bracket_expressions >= 0', name='check_bracket_expressions'),
        db.CheckConstraint('time_limit > 0', name='check_time_limit'),
        {'comment': '习题集信息表'}
    )

class PracticeRecord(db.Model):
    """练习记录表"""
    __tablename__ = 'practice_record'
    
    record_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
    exercise_set_id = db.Column(db.Integer, db.ForeignKey('exercise_set.exercise_set_id'), nullable=False)
    completion_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # 练习时长（秒）
    is_timeout = db.Column(db.Boolean, default=False)  # 是否超时
    is_completed = db.Column(db.Boolean, default=False)  # 是否完成所有题目
    
    total_expressions = db.Column(db.Integer, nullable=False, comment='总题目数')
    bracket_expressions = db.Column(db.Integer, nullable=False, default=0, comment='括号题目数')
    time_limit = db.Column(db.Integer, nullable=False, comment='时间限制(分钟)')
    operators = db.Column(db.String(50), nullable=False, comment='运算符列表')
    operator_count = db.Column(db.Integer, nullable=False, comment='运算符数量')
    min_number = db.Column(db.Integer, nullable=False, comment='最小值')
    max_number = db.Column(db.Integer, nullable=False, comment='最大值')

    __table_args__ = (
        {'comment': '练习记录表'}
    )

class Expression(db.Model):
    """算式表：存储具体的算式信息"""
    __tablename__ = 'expression'
    expression_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算式ID')
    exercise_set_id = db.Column(db.Integer, db.ForeignKey('exercise_set.exercise_set_id'), nullable=False, comment='所属习题集ID')
    expression_text = db.Column(db.String(100), nullable=False, comment='算式表达式')
    has_brackets = db.Column(db.Boolean, nullable=False, default=False, comment='是否含括号')
    operator_count = db.Column(db.Integer, nullable=False, default=1, comment='运算符数量')
    answer = db.Column(db.Float, nullable=False, comment='正确答案')
    
    answer_records = db.relationship('AnswerRecord', backref='expression', lazy=True)
    
    __table_args__ = (
        db.CheckConstraint('operator_count > 0 AND operator_count < 10', name='check_operator_count'),
        {'comment': '算式信息表'}
    )

class AnswerRecord(db.Model):
    """答题记录表：记录用户的答题情况"""
    __tablename__ = 'answer_record'
    answer_record_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='答题记录ID')
    expression_id = db.Column(db.Integer, db.ForeignKey('expression.expression_id'), nullable=False, comment='算式ID')
    user_answer = db.Column(db.Float, nullable=False, comment='用户答案')
    is_correct = db.Column(db.Boolean, nullable=False, comment='是否正确')
    answer_time = db.Column(db.Float, nullable=False, comment='答题时间(秒)')
    
    error_record = db.relationship('ErrorRecord', backref='answer_record', lazy=True)
    
    __table_args__ = (
        {'comment': '答题记录表'}
    )

class ErrorRecord(db.Model):
    """错题记录表：记录用户的错题信息"""
    __tablename__ = 'error_record'
    error_record_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='错题记录ID')
    answer_record_id = db.Column(db.Integer, db.ForeignKey('answer_record.answer_record_id'), nullable=False, comment='对应���答题记录ID')
    is_exported = db.Column(db.Boolean, default=False, comment='是否已导出')
    export_time = db.Column(db.DateTime, nullable=True, comment='导出时间')
    
    __table_args__ = (
        {'comment': '错题记录表'}
    ) 