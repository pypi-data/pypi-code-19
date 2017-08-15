from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pyedu.app import db
from flask_login import AnonymousUserMixin


# db = SQLAlchemy()

class Level:
    STUDENT = 10
    TEACHER = 20
    SUPERUSER = 99

mn_teacher_lecture = db.Table('mn_teacher_lecture',
    db.Column('teacher_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('lecture_id', db.Integer, db.ForeignKey('lectures.id'), primary_key=True)
)

mn_student_lecture = db.Table('mn_student_lecture',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('lecture_id', db.Integer, db.ForeignKey('lectures.id'), primary_key=True)
)


class Role(db.Model):
    """

    """
    __tablename__ = 'roles'

    # define columns
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    level = db.Column(db.Integer(), nullable=False)

    # relationships
    users = db.relationship('User', back_populates='role')

    @classmethod
    def insert_default_roles(cls):
        """
        Insert the Student, Teacher and Superuser role.
        :return:
        """

        r_super = Role.query.filter_by(name='superuser').first()
        if r_super is None:
            r_super = Role(name='superuser', level=99)

        r_teach = Role.query.filter_by(name='teacher').first()
        if r_teach is None:
            r_teach = Role(name='teacher', level=20)

        r_stud = Role.query.filter_by(name='student').first()
        if r_stud is None:
            r_stud = Role(name='student', level=10)

        db.session.add_all([r_super, r_stud, r_teach])
        db.session.commit()

    def __repr__(self):
        return '<ID=%s ROLE %s>' % (self.id, self.name)


class User(db.Model):
    """

    """
    __tablename__ = 'users'

    # define columns
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    full_name = db.Column(db.String(1024), nullable=True)
    email = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    edited = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    role = db.relationship('Role', back_populates='users')
    teaching = db.relationship('Lecture', secondary='mn_teacher_lecture', back_populates='teachers')
    enrolled = db.relationship('Lecture', secondary='mn_student_lecture', back_populates='students')
    edited_tasks = db.relationship('Task', secondary='assignments', back_populates='solvers')

    @property
    def password(self):
        return '************'

    @password.setter
    def password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        db.session.add(self)
        db.session.commit()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        if self.role.name.lower() == role.lower():
            return True
        else:
            return False

    def has_level(self, level):
        if self.role.level >= level:
            return True
        else:
            return False

    def is_enrolled(self, lecture):
        return lecture.is_enrolled(self)

    @staticmethod
    def insert_default_users(superuser_mail, superuser_password):
        """
        Insert or update the default superuser.

        :param superuser_mail:
        :param superuser_password:
        :return:
        """
        r_superuser = Role.query.filter_by(name='superuser').first()
        Superuser = User.query.filter_by(username='superuser').first()
        if Superuser is None:
            Superuser = User(username='superuser', role=r_superuser, confirmed=True)
        Superuser.email = superuser_mail
        Superuser.password = superuser_password
        db.session.add(Superuser)
        db.session.commit()

    def get_next_task(self):
        """

        :return:
        """
        if self.is_anonymous or not self.has_role('student'):
            return None

        # get the latest log
        log = Log.query.filter_by(student_id=self.id).order_by(Log.tstamp.desc()).first()
        if log is None:
            return None

        # get the task
        task = Task.query.filter_by(id=log.task_id).first()
        if task is None:
            print('Task of id %d does not exist, but should.' % log.task_id)
            return None
        if task.has_solved(self):
            return task.next
        else:
            return task



    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.confirmed

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return '<ID=%s USER %s (%s) >' % (self.id, self.username, self.role.name)


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        if role.lower() == 'anonymous':
            return True
        else:
            return False

    def has_level(self, level):
        if level == 0:
            return True
        else:
            return False

    def get_next_task(self):
        return None


class Lecture(db.Model):
    """

    """
    __tablename__ = 'lectures'

    # define columns
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    edited = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    lessons = db.relationship('Lesson', back_populates='lecture')
    teachers = db.relationship('User', secondary='mn_teacher_lecture', back_populates='teaching')
    students = db.relationship('User', secondary='mn_student_lecture', back_populates='enrolled')

    def enroll(self, student):
        # is it a student
        if not student.has_role('student'):
            return False

        if student in self.students:
            return False
        else:
            self.students.append(student)
            db.session.add(self)
            db.session.commit()
            return True

    def is_enrolled(self, student):
        return student in self.students

    def is_teaching(self, teacher):
        return teacher in self.teachers

    @property
    def enrollments(self):
        return len(self.students)

    @property
    def lesson_count(self):
        return len(self.lessons)

    def __repr__(self):
        return '<ID=%s %s Lecture >' % (self.id, self.name)


class Lesson(db.Model):
    """

    """
    __tablename__ = 'lessons'
    __table_args__ = (
        db.UniqueConstraint('lecture_id', 'name'),
    )

    # define columns
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    lecture_id = db.Column(db.Integer(), db.ForeignKey('lectures.id'), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    edited = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    lecture = db.relationship('Lecture', back_populates='lessons')
    tasks = db.relationship('Task', back_populates='lesson')

    @property
    def count(self):
        return len(self.tasks)

    def has_completed(self, student, required_only=False):
        """
        load all `pyedu.models.Task`s of this instance and return if the given student has solved all.
        If required_only is True, only required Tasks will be evaluated.

        :param student:
        :param required_only:
        :return:
        """
        if required_only:
            return all([task.has_solved(student=student) for task in self.tasks if task.required])
        else:
            return all([task.has_solved(student=student) for task in self.tasks])

    def progress(self, student, required_only=False):
        """
        Returns the number of solved tasks.
        If required_only is True, only required Tasks will be evaluated.

        :param student:
        :return:
        """
        if required_only:
            return len([True for task in self.tasks if task.required and task.has_solved(student=student)])
        else:
            return len([True for task in self.tasks if task.has_solved(student=student)])

    @property
    def task_count(self):
        return len(self.tasks)

    def __repr__(self):
        return '<ID=%s Lesson %s >' % (self.id, self.name)


class Task(db.Model):
    """

    """
    __tablename__ = 'tasks'

    # define columns
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    lesson_id = db.Column(db.Integer(), db.ForeignKey('lessons.id'), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    solution = db.Column(db.Text(), nullable=False)
    required = db.Column(db.Boolean(), nullable=False, default=True)
    seq = db.Column(db.Integer(), nullable=True, unique=True)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    edited = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    solvers = db.relationship('User', secondary='assignments', back_populates='edited_tasks')

    # relationships
    lesson = db.relationship('Lesson', back_populates='tasks')

    def has_solved(self, student):
        """
        load the :py:class:: `pyedu.models.Assignment` of the given :py:class:: `pyedu.models.User` istance to this
        Task instance and return the solved state of the :py:class:: `pyedu.models.Assignment`.
        If no assignment is found return False.

        :param student: :py:class:: `pyedu.models.User`, with a 'student' role
        :return: bool, if Task was solved by given User
        """
        assign = Assignment.query.filter_by(task_id=self.id, student_id=student.id).first()
        if assign is None:
            return False
        else:
            return assign.solved

    def get_user_body(self, student):
        """
        Load the assignment of the given user. If any, return the assignment body, else the  task body.

        :param student:
        :return:
        """
        assignment = Assignment.query.filter_by(student_id=student.id, task_id=self.id).first()

        if assignment is None:
            return self.body
        else:
            return assignment.body

    @property
    def next(self):
        return Task.query.filter_by(lesson_id=self.lesson_id).filter(Task.seq > self.seq).order_by(Task.seq).first()

    @property
    def previous(self):
        return Task.query.filter_by(lesson_id=self.lesson_id).filter(Task.seq < self.seq).order_by(Task.seq.desc()).first()


    def __repr__(self):
        return '<ID=%s Task %s >' % (self.id, self.name)


class Assignment(db.Model):
    """

    """
    __tablename__ = 'assignments'

    # define columns
    student_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('tasks.id'), primary_key=True)
    body = db.Column(db.Text(), nullable=False)
    solved = db.Column(db.Boolean(), default=False, nullable=False)
    attempts = db.Column(db.Integer(), default=0, nullable=False)
    last_edited = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def increment(self):
        self.attempts += 1


class Log(db.Model):
    """

    """
    __tablename__ = 'logs'

    # define columns
    student_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('tasks.id'), primary_key=True)
    tstamp = db.Column(db.DateTime(), default=datetime.utcnow, primary_key=True)


