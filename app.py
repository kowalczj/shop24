from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop24.db'
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


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


class Product(db.Model):
    id =                    db.Column(db.Integer, primary_key=True)
    product_name =          db.Column(db.String(200), nullable=False)
    product_description =   db.Column(db.String(200), nullable=False)
    product_price =         db.Column(db.Numeric(10, 2), nullable=False)
    product_cost =          db.Column(db.Numeric(10, 2), nullable=False)
    date_created =          db.Column(db.DateTime, default=datetime.utcnow)
    category_id =           db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


class Order(db.Model):
    id =                  db.Column(db.Integer, primary_key=True)
    customer_id =          db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


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
        cost = request.form['product_cost']
        price = request.form['product_price']
        category = request.form['category_id']

        if float(price) < (1.3 * float(cost)):
            price = round((1.3 * float(cost)), 2)


        new_product = Product(
            product_name=name,
            product_description=description,
            product_price=price,
            product_cost=cost,
            category_id=category
        )

        print("Product data:")
        print(new_product.id)
        print(new_product.product_name)
        print(new_product.product_description)
        print(new_product.product_price)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/')
        except:
            return "Error: There was a problem adding the new product data"
    else:
        tasks = Product.query.order_by(Product.date_created).all()
        categories= Category.query.all()
        return render_template("index.html", tasks = tasks, categories=categories)


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
        try:
            db.session.add(customer)
            db.session.commit()
            return redirect('/customers')
        except Exception as ex:
            print("Error: ", ex)
            return "Error: There was a problem adding the new customer data"
        # return render_template('customers.html', results = customers)


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
        product.product_cost = request.form['product_cost']
        product.category_id = request.form['category_id']

        if float(product.product_price) < (1.3 * float(request.form['product_cost'])):
            product.product_price = round((1.3 * float(request.form['product_cost'])), 2)
            
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        categories= Category.query.all()
        return render_template('update.html', product=product, categories=categories)


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
        products = Product.query.all()
        customers = Customer.query.all()
        return render_template("orders.html", tasks = tasks, products=products, customers=customers)


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
    customers= Customer.query.all()

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
        customers= Customer.query.all()
        return render_template('update_order.html', task=order, customers=customers)


@app.route("/order_product", methods=['POST', 'GET'])
def orderproduct():
    if request.method == 'POST':
        if 'order_id' in request.form:

            orderID = request.form['order_id']
            productID = request.form['product_id']
            quantity = request.form['quantity']
            url = '/order_product?id=' + str(orderID)

            newOrderProduct = OrderProduct(
                order_id=orderID,
                product_id=productID,
                quantity=quantity,
            )

            try:
                db.session.add(newOrderProduct)
                db.session.commit()
                # return render_template('orderproduct.html')
                return redirect(url)
            except Exception as ex:
                print("Error: ", ex)
                return "Error: There was a problem adding the new order data"
        elif 'id' in request.form:

            orderID = request.form['id']
            tasks = OrderProduct.query.filter(OrderProduct.order_id == orderID).order_by(OrderProduct.id).all()
            return render_template("order_product.html",tasks=tasks, orderID = orderID)
    elif request.method == 'GET':
        orderID = request.args['id']
        tasks = OrderProduct.query.filter(OrderProduct.order_id == orderID).order_by(OrderProduct.id).all()
        products = Product.query.all()
        return render_template("order_product.html",tasks=tasks, orderID = orderID, products=products)


@app.route("/vendors")
@login_required
def vendors():
    return render_template("vendors.html")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/order_product/delete/<int:orderID>/<int:id>')
def orderProductDelete(orderID, id):
    print("id: ", id)
    url = '/order_product?id=' + str(orderID)
    print("url: ", url)
    task_to_delete = OrderProduct.query.get_or_404(id)
    print("task_to_delete: ", task_to_delete)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url)
    except:
        return 'There was a problem deleting that task'


@app.route('/order_product/update/<int:orderID>/<int:id>')
def orderProductUpdate(orderID, id):
    url = '/order_product?id=' + str(orderID)
    order_product = OrderProduct.query.get_or_404(id)
    if request.method == 'POST':
        order_product.product_id = request.form['product_id']
        order_product.quantity = request.form['quantity']

        try:
            db.session.commit()
            return redirect(url)
        except Exception as e:
            print(e)
            return 'There was an issue updating your task'

    else:
        url = '/order_product?id=' + str(orderID)
        order_product = OrderProduct.query.get_or_404(id)
        return render_template('update_order_product.html', orderID=orderID, id=id)


@app.route('/metrics')
@login_required
def metrics():
    metrics = db.session.query(OrderProduct.product_id, func.sum(OrderProduct.quantity).label('quantity')).group_by(OrderProduct.product_id).all()
    products = Product.query.all()
    if request.method == 'GET':
        return render_template('metrics.html', tasks=metrics, products=products)


@app.route('/orderhistory', methods=['POST', 'GET'])
def orderHistory():
    if request.method == 'POST':
        accountID = request.form['searched_account_id']
        tasks = Order.query.filter(Order.customer_id == accountID).order_by(Order.shipment_priority).all()
        try:
            return render_template('orderhistorydetails.html', tasks=tasks)
        except Exception as ex:
            print("Error: ", ex)
            return "Error: There was a problem viewing the order history"
    else:
        return render_template('orderhistory.html')


@app.route("/category", methods=['POST', 'GET'])
@login_required
def category():
    if request.method == 'POST':
        category_name = request.form['category_name']

        new_category = Category(
            category_name=category_name
        )

        try:
            db.session.add(new_category)
            db.session.commit()
            return redirect('/category')
        except:
            return "Error: There was a problem adding the new category"
    else:
        categories = Category.query.all()
        return render_template("category.html", categories=categories)


@app.route('/category/update/<int:id>', methods=['GET', 'POST'])
def category_update(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.category_name = request.form['category_name']

        try:
            db.session.commit()
            return redirect('/category')
        except:
            return 'There was an issue updating your task'

    else:
        categories = Category.query.all()
        return render_template('update_category.html', category=category)


@app.route('/category/delete/<int:id>')
def category_delete(id):
    category_to_delete = Category.query.get_or_404(id)

    try:
        db.session.delete(category_to_delete)
        db.session.commit()
        return redirect('/category')
    except:
        return 'There was a problem deleting that task'



if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080)   # This didn't work for me, so I set it to the line under
    app.run(debug=True)
