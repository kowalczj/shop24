from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name = request.form['product_name']
        description = request.form['product_description']
        price = request.form['product_price']

        new_product = Todo(
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
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks = tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    product = Todo.query.get_or_404(id)

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

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/orders")
def orders():
    return render_template("orders.html")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8080)   # This didn't work for me, so I set it to the line under
    app.run(debug=True)
