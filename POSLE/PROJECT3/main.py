from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.edit_form import EditProfile
from forms.post_form import PostForm
from forms.register import RegisterForm
from forms.login import LoginForm
from data.post import Post
from data.users import User
from data.favorites import Favorite
from data.likes import Like
from forms.comments_form import CommentsForm
from data.comments import Comments
from data import db_session
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init('db/post_media.db')
    app.run()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit() and request.method == 'POST':
        db_sess = db_session.create_session()
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            is_private=form.is_private.data
        )
        if 'image' and request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f'{datetime.now().timestamp()}_{filename}'
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                post.image = unique_filename
        db_sess.add(post)
        db_sess.commit()
        add_exp(current_user.id, 10)
        return redirect('/')
    return render_template('post.html', title='Добавление новости', form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return render_template('index.html', filename=filename)


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id, Post.user == current_user).first()
    if post:
        if post.image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
            except:
                pass
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id, Post.user == current_user).first()
    if not post:
        abort(404)
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.is_private.data = post.is_private
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_private = form.is_private.data
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                if post.image:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
                    except:
                        pass
                filename = secure_filename(file.filename)
                unique_filename = f'{datetime.now().timestamp()}_{filename}'
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)
                post.image = unique_filename
        db_sess.commit()
        return redirect('/')
    return render_template('post.html', title='Редактирование новости', form=form)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    comment_form = CommentsForm()
    if current_user.is_authenticated:
        posts = (db_sess.query(Post).filter((Post.user == current_user) | (Post.is_private != True)).order_by
                 (Post.created_date.desc()).all())
    else:
        posts = db_sess.query(Post).filter(Post.is_private != True).order_by(Post.created_date.desc()).all()
    return render_template('index.html', post=posts, comment_form=comment_form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        if len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароль должен содержать как минимум 8 символов")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        if len(form.username.data) < 4:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Юзернейм должен содержать как минимум 4 символа")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            username = form.username.data,
            age=form.age.data,
            email=form.email.data,
            password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/user/<username>')
def user(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    if user is None:
        abort(404)
    posts_all = db_sess.query(Post).filter(Post.user_id == user.id)
    if current_user.is_authenticated and current_user == user:
        posts = posts_all.order_by(Post.created_date.desc()).all()
        favorites = db_sess.query(Post).filter_by(user_id=current_user.id).all()
    else:
        posts = posts_all.filter(Post.is_private == False).order_by(Post.created_date.desc()).all()
        favorites = []
    comment_form = CommentsForm()
    return render_template('profile.html', user=user, favorites=favorites,
                           posts=posts, comment_form=comment_form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.username = form.username.data
            user.age = form.age.data
            db_sess.commit()
            return redirect(f'/user/{user.username}')
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.username.data = current_user.username
        form.age.data = current_user.age
    return render_template('edit.html', form=form)


@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        favorites = db_sess.query(Favorite).filter_by(user_id=current_user.id).all()
        favorite_posts = [fav.post for fav in favorites if fav.post]
    return render_template('favorites.html', title='Избранное', posts=favorite_posts)


@app.route('/add_favorites/<int:id>', methods=['GET', 'POST'])
def add_favorites(id):
    db_sess = db_session.create_session()
    post_id = request.form.get('post_id')
    if not post_id:
        abort(404)
    existing_favorite = db_sess.query(Favorite).filter(Favorite.post_id == id,
                                                       Favorite.user_id == current_user.id).first()
    if not existing_favorite and current_user.is_authenticated:
        favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db_sess.add(favorite)
        db_sess.commit()
    return redirect('/')


@app.route('/favorites_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def favorites_delete(id):
    db_sess = db_session.create_session()
    favorite_id = db_sess.query(Favorite).filter(Favorite.post_id == id).first()
    if favorite_id:
        db_sess.delete(favorite_id)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/favorites')


@app.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')


@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()
    db_sess = db_session.create_session()
    if query:
        results = db_sess.query(User).filter(User.username.ilike(f'%{query}%')).all()
    else:
        results = []
    return render_template('search_res.html', query=query, results=results, title='Результаты поиска')


@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    db_sess = db_session.create_session()
    existing_like = db_sess.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    post = db_sess.query(Post).get(post_id)
    if post:
        add_exp(post.user_id, 2)
    if existing_like:
        db_sess.delete(existing_like)
        post.like_count -= 1
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db_sess.add(new_like)
        post.like_count += 1
    db_sess.commit()
    return redirect(request.referrer or '/')


@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comments(text=form.text.data, user_id=current_user.id, post_id=post_id)
        db_sess.add(comment)
        db_sess.commit()
        add_exp(current_user.id, 5)
    return redirect(request.referrer or '/')


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comments).filter(
        Comments.id == comment_id, Comments.user_id == current_user.id).first()
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    return redirect(request.referrer or '/')


def add_exp(user_id, points):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if user:
        user.exp += points
        exp_needed = user.level * 100
        if user.exp >= exp_needed:
            user.level += 1
            user.exp = 0
        db_sess.commit()


if __name__ == '__main__':
    main()
