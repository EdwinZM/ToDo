
from flask import Flask, render_template, redirect, request, session
from flask.ctx import RequestContext
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import check_password_hash, generate_password_hash, Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///list.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.secret_key = "jasldfjaodfadfajdfljdflk"

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    is_anonymous = False
    items = relationship("Item")

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/", methods=["GET", "POST", "DELETE"])
def home():
    items = []
    logged = False

    if request.method == "POST":
        item = request.form["item"]

        new_item = Item(item=item, user_id=current_user.get_id()) 
        
        db.session.add(new_item)
        db.session.commit()

        return redirect("/")

    if current_user.is_authenticated:
        logged = True
        id = int(current_user.get_id())
        user = User.query.get(id)
        items = user.items
    return render_template("index.html", logged=logged, items=items)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        users = User.query.all()

        email = request.form["email"]
        password = request.form["password"]

        for user in users: 
            if user.email == email:
                is_auth = check_password_hash(user.password, password)
                if is_auth:
                    login_user(user)
                    return redirect("/")
                else:
                    error = "Incorrect Password"
                    return render_template("login", error=error)
        error = "User not found!"
        
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        users = User.query.all()

        email = request.form["email"]
        password = request.form["password"]

        for user in users:
            if user.email == email:
                error = "User already exists!"
                return render_template("signup.html", error=error)
        
        pw_hash = generate_password_hash(password).decode("utf-8")

        new_user = User(email = email, password = pw_hash)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect("/")
        
    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/delete_item<id>", methods=["GET","DELETE"])
def delete_item(id):
    item_to_delete = Item.query.get(id)

    db.session.delete(item_to_delete)
    db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)