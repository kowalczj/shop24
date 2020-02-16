from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)

class ProductTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float(10), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Product %r>' % self.id

class OrderTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_table.id'), nullable=False)
    order_name = db.Column(db.String(200), nullable=False)
    is_priority = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return '<Order %r>' % self.id

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

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name = request.form['product_name']
        description = request.form['product_description']
        price = request.form['product_price']
        quantity = request.form['product_quantity']

        new_product = ProductTable(
            product_name=name,
            product_description=description,
            product_price=price,
            product_quantity=quantity
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/')
        except:
            return "Error: There was a problem adding the new product data"
    else:
        prods = ProductTable.query.order_by(ProductTable.date_created).all()
        return render_template("index.html", prods = prods)

@app.route('/customers', methods=['POST', 'GET'])
def customers():

    customers = Customer.query.all()

    if request.method == 'GET':

        return render_template('customers.html', results = customers)       

    elif request.method == 'POST':
    
        customer = Customer(first_name     = request.form['first_name'], 
                            last_name      = request.form['last_name'],
                            email          = request.form['email'],
                            phone          = request.form['phone'], 
                            street_addr    = request.form['street_adr'],
                            state          = request.form['state'],
                            zipcode        = request.form['zipcode'],
                            city           = request.form['city'])

        db.session.add(customer)
        db.session.commit()
        
        return render_template('customers.html', results = customers)  

@app.route('/delete/<int:id>')
def delete(id):
    prod_to_delete = ProductTable.query.get_or_404(id)

    try:
        db.session.delete(prod_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that product'

@app.route('/order/<int:id>', methods=['GET', 'POST'])
def order(id):
    prod_to_order = ProductTable.query.get_or_404(id)
    priority = request.form.get('order_priority')
    is_checked = False
    if request.method == 'POST':
        if priority is not None:
            is_checked = True
        new_order = OrderTable(
            product_id=prod_to_order.id,
            order_name=prod_to_order.product_name,
            is_priority=is_checked
        )
        try:
            db.session.add(new_order)
            db.session.commit()
            ords = OrderTable.query.order_by(OrderTable.is_priority.desc()).all()
            return render_template('orders.html', ords=ords)
        except:
            return 'There was a problem ordering that product'
    else:
        return render_template('order.html', ord=prod_to_order)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    product = ProductTable.query.get_or_404(id)

    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.product_description = request.form['product_description']
        product.product_price = request.form['product_price']
        product.product_quantity = request.form['product_quantity']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your product'

    else:
        return render_template('update.html', prod=product)

@app.route("/vendors")
def vendors():
    return render_template("vendors.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/orders")
def orders():
    ords = OrderTable.query.order_by(OrderTable.is_priority.desc()).all()
    return render_template('orders.html', ords=ords)

if __name__ == "__main__":
    app.run(debug=True)
