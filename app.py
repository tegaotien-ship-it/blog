import os
from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from froms import signUpfrom
from signupform import MyRegisterForm
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail,Message
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length,Email,EqualTo
from flask_wtf import FlaskForm
app = Flask(__name__)
app.secret_key = "pelz"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'key'
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config['MAIL_USERNAME']="tegaotien@gmail.com"
app.config['MAIL_PASSWORD']="cmgn ondw xgbo icps"
app.config["MAIL_DEFAULT_SENDER"]="tegaotien@gmail.com"

mail=Mail(app)


# ── upload config ──
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── extensions ──
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# ── helper ──
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── models ──
class Blog(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

    def __init__(self, title, content, user_id, image=None):
        self.title = title
        self.content = content
        self.image = image
        self.user_id = user_id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    blogs = db.relationship("Blog", backref="author", lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    def get_reset_token(self,expires_sec=1800):
        s=URLSafeTimedSerializer(app.config["SECRET_KEY"])
        return s.dumps({'user_id':self.id})
    
    @staticmethod
    def verify_reset_token(token):
        s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class RequestResetForm(FlaskForm):
      email=StringField("Email",validators=[DataRequired(),Email()])
      submit=SubmitField("Request Password Reset")
    #   if email does not exist
      def validate_email(self,email):
          user=User.query.filter_by(email=email.data).first()
          if user:
              raise ValidationError("There is no account with that email,you must register first.")

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField(
    'Confirm Password', 
    validators=[DataRequired(), EqualTo('password', message='Passwords must match.')] # ⬅️ Pass 'password' here
)


    submit=SubmitField( "Reset Password")
# FIX A: User.query.get() is removed in SQLAlchemy 2.x — use db.session.get() instead
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── HOME ──
@app.route('/')
def home_page():
    page=request.args.get("page",1,type=int)
    blogs = Blog.query.paginate(page=page,per_page=4)

    return render_template('home.html', blogs=blogs)

# ── DASHBOARD ──
@app.route('/dashboard')
@login_required
def dashboard():
    user_blogs = Blog.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', blogs=user_blogs, title="Blogs Page", total=len(user_blogs))


# ── LOGIN ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash('Logged in successfully', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


# ── LOGOUT ──
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


# ── REGISTER ──


@app.route('/register', methods=['GET', 'POST'])
def register():
    signupform=MyRegisterForm()
    if request.method == 'POST':
        username = signupform.name.data
        email    = signupform.email.data
        password = bcrypt.generate_password_hash(signupform.password.data).decode('utf-8')

        user = User(username=username, email=email, password=password)
        db.session.add(user)

        try:
            db.session.commit()
            flash('Account created! You can now log in.', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            db.session.rollback()          # ← required, clears the broken transaction
            flash('That username or email is already taken.', 'danger')

    return render_template('register.html',form=signupform)


# ── ADD BLOG ──
@app.route('/addblog', methods=['GET', 'POST'])
@login_required
def add_blog_page():
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        file = request.files.get('image')

        if not title or not content:
            flash('Title and content are required', 'danger')
            return render_template('addblogpage.html')

        if Blog.query.filter_by(title=title).first():
            flash('Title already exists', 'danger')
            return render_template('addblogpage.html')

        image_filename = None
        if file and file.filename != "" and allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        blog = Blog(title=title, content=content, image=image_filename, user_id=current_user.id)
        db.session.add(blog)

        try:
            db.session.commit()
            flash('Blog created successfully', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding blog: {e}")
            flash('Something went wrong, please try again', 'danger')

    return render_template('addblogpage.html')


# ── VIEW BLOG ──
@app.route('/viewblog/<title>')
def viewblog(title):
    blog = Blog.query.filter_by(title=title).first_or_404()
    return render_template("viewblog.html", blog=blog)


# ── DELETE BLOG ──
# FIX B: Query.get_or_404() is also removed in SQLAlchemy 2.x — use db.get_or_404()
@app.route('/delete/<int:id>')
@login_required
def deleteuser(id):
    blog = db.get_or_404(Blog, id)

    if blog.user_id != current_user.id:
        flash("You can't delete this post", "danger")
        return redirect(url_for('dashboard'))

    db.session.delete(blog)
    try:
        db.session.commit()
        flash('Blog deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Something went wrong, please try again', "danger")
    return redirect(url_for('dashboard'))

@app.route('/signup')
def signup():
    form=signUpfrom()
    return render_template('signup.html', form=form)



# ── UPDATE BLOG ──
@app.route('/updateblog/<int:id>', methods=['GET', 'POST'])
@login_required
def updateblog(id):
    # FIX B (same): use db.get_or_404() instead of Query.get_or_404()
    blog = db.get_or_404(Blog, id)

    if blog.user_id != current_user.id:
        flash('Not allowed to edit this blog', "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_title = request.form.get('title', '').strip()
        new_content = request.form.get('content', '').strip()
        file = request.files.get('image')

        if not new_title or not new_content:
            error = "Title and content cannot be empty"
            return render_template('updateblog.html', blog=blog, error=error)

        existing = Blog.query.filter_by(title=new_title).first()
        if existing and existing._id != blog._id:
            error = "A blog with this title already exists"
            return render_template('updateblog.html', blog=blog, error=error)

        blog.title = new_title
        blog.content = new_content

        if file and file.filename != "" and allowed_file(file.filename):
            image_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            blog.image = image_filename

        try:
            db.session.commit()
            flash('Blog updated', 'success')
            return redirect(url_for("viewblog", title=blog.title))
        except Exception as e:
            db.session.rollback()
            return render_template('updateblog.html', blog=blog, error='Something went wrong, please try again')

    return render_template('updateblog.html', blog=blog)

def send_reset_email(user):
    token=User.get_reset_token(user)

    msg=Message("Password Reset Request",sender='tegaotien@gmail.com',recipients=[user.email])
    msg.body=f'''
    To reset your password visit the following link:
{url_for('reset_token',token=token, _external=True)}
    if you did not make this request ignore this message
 '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if request.method=="POST":
       print(form.email.data)
       user=User.query.filter_by(email=form.email.data).first()
       print("user:",user)
       send_reset_email(user)
       flash("An Email have been sent with instructions to reset password","info")
       return redirect(url_for("login"))
    return render_template("resetpassword.html",form=form)
    
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash("Thai is an invalid token","warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if request.method=="POST":
       hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
       user.password=hashed_password
       print("hashed_password",hashed_password)
       db.session.commit()
       flash("You password have been updated!","success")
       return redirect(url_for("login"))
    return render_template("resettoken.html",form=form)
    



# ── DB INIT ──
# FIX C: db.drop_all() was wiping ALL data on every single restart — removed it
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)