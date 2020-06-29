from flask import render_template, url_for, redirect, request, abort, flash
from stack import app, db, bcrypt
from stack.models import User, Post, Comment
from stack.forms import RegistrationForm, LoginForm, AskForm, CommentForm
from flask_login import login_user, current_user, logout_user, LoginManager, UserMixin, login_required
import os
import secrets
from PIL import Image
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Incorrect username/password!', 'danger')
    return render_template('login.html', form=form)


def send_confirmation_email(email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    confirm_url = url_for('confirm_email', token=confirm_serializer.dumps(email,
                          salt='email-confirmation-salt'),
                          _external=True)

    html = render_template('activate.html', confirm_url=confirm_url)

    send_email('Confirm Your Email Address', [email], html)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt',
                                         max_age=3600)
    except:
        flash('The comfirmation link is invalid or expired', 'error')
        return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user.confirmed:
            flash('Account already confirmed.Please login')
        else:
            user.confirmed = True
            user.confirmed_on = datetime.now()
            db.session.add(user)
            db.session.commit()
            flash('Thank you for confirming your email')

        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, email=form.email.data,
                            password=hashed_password, confirmed=False)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            return redirect(url_for('index'))


        except IntegrityError:
            db.session.rollback()
            flash('ERROR!Email already exists!')

    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#save profile pictures
def save_picture(form_picture):
    random_hex = secrets.token_hex(4)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    posts = Post.query.filter_by(author=user)
    image_file = url_for('static', filename='profile_pics/' +
                         current_user.image)

    return render_template('profile.html', title='Account',
                           image_file=image_file, posts=posts)


@app.route("/user/<username>", methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('user.html', user=user, posts=posts)


def post_img(form_image):
    random_hex = secrets.token_hex(4)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/posts', picture_fn)

    output_size = (400, 400)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/ask", methods=['GET', 'POST'])
@login_required
def new_post():
    form = AskForm()
    if form.validate_on_submit():
        if form.image.data:
            image = post_img(form.image.data)
            post = Post(title=form.title.data, content=form.content.data,
                        image=image, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your Post has been created!')
            return redirect(url_for('index'))
        else:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!')
            return redirect(url_for('index'))
    return render_template('post_questions.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>",  methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    users = User.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(text=form.content.data, post=post, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted')
        return redirect(url_for('post', post_id=post_id))
    return render_template('detail.html', title=post.title, post=post, form=form, users=users)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = AskForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()

        return redirect(url_for('index', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_questions.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))
