from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = "What is going on"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Registration(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already used.Choose another.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(128))

    def setPW(self, password):
        self.password_hash = generate_password_hash(password)

    def checkPW(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Task %r>' % self.id


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class Order(db.Model):
    id =                  db.Column(db.Integer, primary_key=True)
    customer_id =          db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date =          db.Column(db.DateTime, default=datetime.utcnow)
    shipment_priority =   db.Column(db.Integer)

    def __repr__(self):
        return '<Task %r>' % self.id


class OrderProduct(db.Model):
    id =           db.Column(db.Integer, primary_key=True)
    order_id =     db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id =   db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity =     db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

class Customer(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(50), nullable=False)
    last_name	 = db.Column(db.String(50), nullable=False)
    email	 = db.Column(db.String(100), nullable=False)
    phone        = db.Column(db.String(10), nullable=True)
    street_addr  = db.Column(db.String(50), nullable=True)
    state        = db.Column(db.String(2), nullable=True)
    zipcode      = db.Column(db.String(5), nullable=True)
    city         = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return '<Customer {}>'.format(self.id)


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = Registration()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.setPW(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully registered, please log in!')
        return redirect(url_for('login'))
    if request.method == 'POST' and not form.validate():
        flash("Unable to register, either your email or username is already in use. Please try again!")
    return render_template('registration.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.checkPW(form.password.data):
            flash("Unable to login, either your username or password were incorrect. Please try again!")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('You were successfully logged in')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    print('You are now logged out!')
    return redirect(url_for('login'))


@app.route("/", methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        name = request.form['product_name']
        description = request.form['product_description']
        price = request.form['product_price']

        new_product = Product(
            product_name=name,
            product_description=description,
            product_price=price
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/')
        except:
            return "Error: There was a problem adding the new product data"
    else:
        tasks = Product.query.order_by(Product.date_created).all()
        return render_template("index.html", tasks = tasks)


@app.route('/customers', methods=['POST', 'GET'])
@login_required
def customers():
    customers = Customer.query.all()
    if request.method == 'GET':
        return render_template('customers.html', results = customers)
    elif request.method == 'POST':
        customer = Customer(first_name     = request.form['first_name'],
                            last_name      = request.form['last_name'],
                            email          = request.form['email'],
                            phone          = request.form['phone'],
                            street_addr    = request.form['street_addr'],
                            state          = request.form['state'],
                            zipcode        = request.form['zipcode'],
                            city           = request.form['city'])
        db.session.add(customer)
        db.session.commit()
        return render_template('customers.html', results = customers)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Product.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.product_description = request.form['product_description']
        product.product_price = request.form['product_price']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=product)


@app.route("/orders", methods=['POST', 'GET'])
@login_required
def orders():
    if request.method == 'POST':
        customerID = request.form['customer_id']
        shipmentPriority = request.form['shipment_priority']

        new_order = Order(
            customer_id=customerID,
            shipment_priority=shipmentPriority,
        )

        try:
            db.session.add(new_order)
            db.session.commit()
            return redirect('/orders')
        except Exception as ex:
            print("Error: ", ex)
            return "Error: There was a problem adding the new order data"
    else:
        tasks = Order.query.order_by(Order.shipment_priority).all()
        return render_template("orders.html", tasks = tasks)


@app.route('/orders/delete/<int:id>')
def ordersDelete(id):
    task_to_delete = Order.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/orders')
    except:
        return 'There was a problem deleting that task'


@app.route('/orders/update/<int:id>', methods=['GET', 'POST'])
def ordersUpdate(id):
    order = Order.query.get_or_404(id)

    if request.method == 'POST':
        order.customer_id = request.form['customer_id']
        order.shipment_priority = request.form['shipment_priority']

        print("order: ", order.customer_id)
        print("order: ", order.shipment_priority)

        try:
            db.session.commit()
            return redirect('/orders')
        except Exception as e:
            print(e)
            return 'There was an issue updating your task'

    else:
        return render_template('updateOrder.html', task=order)


@app.route("/orderproduct", methods=['POST', 'GET'])
def orderproduct():
    orderId = request.form['id']
    tasks = OrderProduct.query.filter(OrderProduct.id == orderId).order_by(OrderProduct.id).all()
    return render_template("orderproduct.html", tasks = tasks)


@app.route("/vendors")
@login_required
def vendors():
    return render_template("vendors.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080)   # This didn't work for me, so I set it to the line under
    app.run(debug=True)
