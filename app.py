from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)

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
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class Order(db.Model):
    id =                  db.Column(db.Integer, primary_key=True)
    account_id =          db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
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

@app.route("/", methods=['POST', 'GET'])
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
        return render_template("index.html", tasks = tasks)

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

@app.route("/vendors")
def vendors():
    return render_template("vendors.html")


@app.route("/orders", methods=['POST', 'GET'])
def orders():
    if request.method == 'POST':
        accountID = request.form['account_id']
        shipmentPriority = request.form['shipment_priority']

        new_order = Order(
            account_id=accountID,
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
        order.account_id = request.form['account_id']
        order.shipment_priority = request.form['shipment_priority']

        print("order: ", order.account_id)
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
    if request.method == 'POST':
        if 'order_id' in request.form:
            
            orderID = request.form['order_id']
            productID = request.form['product_id']
            quantity = request.form['quantity']
            url = '/orderproduct?id=' + str(orderID)

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
            return render_template("orderproduct.html",tasks=tasks, orderID = orderID)
    elif request.method == 'GET':
        orderID = request.args['id']
        tasks = OrderProduct.query.filter(OrderProduct.order_id == orderID).order_by(OrderProduct.id).all()
        return render_template("orderproduct.html",tasks=tasks, orderID = orderID)


@app.route('/orderproduct/delete/<int:orderID>/<int:id>')
def orderProductDelete(orderID, id):
    print("id: ", id)
    url = '/orderproduct?id=' + str(orderID)
    print("url: ", url)
    task_to_delete = OrderProduct.query.get_or_404(id)
    print("task_to_delete: ", task_to_delete)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url)
    except:
        return 'There was a problem deleting that task'

@app.route('/orderhistory', methods=['POST', 'GET'])
def orderHistory():
    if request.method == 'POST':
        accountID = request.form['searched_account_id']
        tasks = Order.query.filter(Order.account_id == accountID).order_by(Order.shipment_priority).all()        
        try:
            return render_template('orderhistorydetails.html', tasks=tasks)
        except Exception as ex:
            print("Error: ", ex)
            return "Error: There was a problem viewing the order history"
    else:
        return render_template('orderhistory.html')

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080)   # This didn't work for me, so I set it to the line under
    app.run(debug=True)