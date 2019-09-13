import hashlib

from flask import Flask, render_template, request, flash, url_for, jsonify
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

## Init app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect

from forms import UserForm, AdminUserForm

migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:postgres@localhost/alar'
    app.config['SECRET_KEY'] = "just secret"
    app.config['WTF_CSRF_SECRET_KEY'] = "just secret"

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'login'
    login_manager.login_message = None
    return app


app = create_app()

## Models
LEVELS = {
    'admin': 1,
    'guest': 2
}


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'schema': 'alar'}

    id = db.Column(db.Integer, primary_key=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    role = relationship('UserRole', uselist=False)

    @staticmethod
    def get(id):
        try:
            return db.session.query(User).filter(User.id == id).one()
        except NoResultFound:
            return None

    def set_role(self, role_name):
        role = UserRole()
        role.user_id = self.id
        role.role_id = Role.get(role_name)
        db.session.add(role)
        db.session.commit()

    def update_role(self, role_name):
        user = db.session.query(User).filter(User.id == self.id).one()
        user.role.role_id = Role.get(role_name)
        db.session.commit()

    def is_admin(self):
        role = db.session.query(Role).filter(Role.id == self.role.role_id).one()
        if role.level == LEVELS['admin']:
            return True
        return False


class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String(32), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False, default=LEVELS['guest'])

    @staticmethod
    def get(name):
        if isinstance(name, int):
            role = db.session.query(Role).filter(Role.id == name).one()
        else:
            role = db.session.query(Role).filter(Role.name == name).one()
        return role.id


class UserRole(BaseModel):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('alar.users.id'), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('alar.roles.id'))

    def __repr__(self):
        role = db.session.query(Role).filter(Role.id == self.role_id).one()
        return role.name


## Prepare
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def md5hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def signal_log_in(user):
    login_user(user)


## Views
@app.route('/')
@login_required
def index():
    users = db.session.query(User).all()

    form = AdminUserForm()
    if current_user.is_admin():
        roles = db.session.query(Role).all()
        form.role.choices = [(role.id, role.name) for role in roles]
        return render_template('index.html', users=users, form=form)
    return render_template('index.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if len(db.session.query(User).all()) < 1:
        return redirect(url_for('register'))
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user = db.session.query(User).filter(User.username == form.username.data, User.password == md5hash(form.password.data)).one()
            flash(f'User {user.username} was logged in')
            signal_log_in(user)
            return redirect(request.args.get('next') or url_for('index'))
        except NoResultFound:
            flash('Check username/password')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('User was logout')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You must logged out')
        return redirect(url_for('index'))
    form = UserForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.password = md5hash(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            signal_log_in(user)
            if len(db.session.query(User).all()) == 1:
                user.set_role('admin')
            else:
                user.set_role('guest')
            flash('User successfully registered')
            return redirect(request.args.get('next') or url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('This user already exists!')
        except:
            db.session.rollback()
            flash('Error')
    return render_template('register.html', form=form)


def check_user_data(request):
    if len(request.form.get('username')) < 4 or len(request.form.get('username')) > 64:
        return jsonify({'result': False,
                        'message': 'username must be more or equel 4 letters and less or equel 64 letters'}), 400
    if len(request.form.get('password')) < 4 or len(request.form.get('password')) > 32:
        return jsonify(
            {'result': False, 'message': 'password must be more or equel 4 letters and less or equel 32 letters'}), 400

    return


## API
version = 1.0


@app.route(f'/api/{version}/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route(f'/api/{version}/users', methods=['POST'])
def api_users(user_id=None):
    if request.method == 'GET':
        try:
            user = db.session.query(User).filter(User.id == user_id).one()
            data = {'user_id': user.id, 'username': user.username, 'role': str(user.role), 'role_id': user.role.role_id,
                    'result': True}
            return jsonify(data), 200
        except NoResultFound:
            data = {'result': False}
            return jsonify(data), 404

    if request.method == 'POST':
        check = check_user_data(request)
        if check:
            return check
        user = User()
        user.username = request.form.get('username')
        user.password = md5hash(request.form.get('password'))
        try:
            db.session.add(user)
            db.session.commit()
            user.set_role(request.form.get('role_id', 0, int))
            return jsonify({'result': True, 'user_id': user.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'result': False, 'message': 'username must be unique'}), 409
        except:
            db.session.rollback()
            return jsonify({'result': False}), 500

    if request.method == 'PUT':
        if not current_user.is_admin():
            return jsonify({'result': False, 'message': 'You don\'t have access to this method'}), 403
        try:
            user = db.session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            return jsonify({'result': False, 'message': 'You can\'t update if user not exists'}), 406
        except:
            return jsonify({'result': False}), 500

        if request.form.get('username'):
            user.username = request.form.get('username')
            if len(request.form.get('username')) < 4:
                return jsonify({'result': False, 'message': 'Username length must be more or equal 4'}), 406

        if len(request.form.get('password')) < 4:
            return jsonify({'result': False, 'message': 'Password length must be more or equal 4'}), 406

        if request.form.get('password') and len(request.form.get('password')) > 0:
            if md5hash(request.form.get('password')) != user.password:
                user.password = md5hash(request.form.get('password'))
                print('Пароль обновлен')
        if request.form.get('role_id', 0, int):
            user.update_role(request.form.get('role_id', 0, int))
        db.session.commit()
        return jsonify({'result': True}), 201
    if request.method == 'DELETE':
        if not current_user.is_admin():
            return jsonify({'result': False, 'message': 'You don\'t have access to this method'}), 403
        try:
            user = db.session.query(User).filter(User.id == request.form.get('user_id', 0, int)).one()
        except NoResultFound:
            return jsonify({'result': False, 'message': 'You can\'t update if user not exists'}), 406
        except:
            return jsonify({'result': False}), 500

        db.session.delete(user)
        db.session.commit()
        return jsonify({'result': True}), 204
    return jsonify({}), 405
