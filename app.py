import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from data import users, offers, orders

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
app.app_context().push()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    offers = relationship('Offer')
    orders = relationship('Order')


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    # orders = relationship('Order')
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = relationship('User')


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(500))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = relationship('User')
    executor_id = db.Column(db.Integer, db.ForeignKey('offer.executor_id'))
    # offer = relationship('Offer')


def insert_data():
    new_users = []
    for user in users:
        new_users.append(
            User(
                id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone'],
            )
        )
    new_orders = []
    for order in orders:
        new_orders.append(
            Order(
                id=order['id'],
                name=order['name'],
                description=order['description'],
                start_date=datetime.strptime(order['start_date'], '%m/%d/%Y').date(),
                end_date=datetime.strptime(order['end_date'], '%m/%d/%Y').date(),
                address=order['address'],
                price=order['price'],
                customer_id=order['customer_id']
            )
        )
    new_offers = []
    for offer in offers:
        new_offers.append(
            Offer(
                id=offer['id'],
                order_id=offer['order_id'],
                executor_id=offer['executor_id']
            )
        )
    with db.session.begin():
        db.session.add_all(new_users)
        db.session.add_all(new_orders)
        db.session.add_all(new_offers)


@app.route('/users', methods=['GET', 'POST'])
def all_users():
    if request.method == 'GET':
        users = db.session.query(User).all()
        users_list = []
        for user in users:
            users_list.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone})
        return jsonify(users_list)
    elif request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        new_user = User(id=data['id'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        age=data['age'],
                        email=data['email'],
                        role=data['role'],
                        phone=data['phone']
                        )
        with db.session.begin():
            db.session.add(new_user)
        # db.session.commit()
        return jsonify('user added')


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_user(id):
    if request.method == 'GET':
        user = User.query.get(id)
        if user:
            return json.dumps({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone})
        else:
            return jsonify('invalid id')
    elif request.method == 'PUT':
        data = json.loads(request.data)
        user_to_change = User.query.get(id)
        if user_to_change:
            user_to_change.id = data['id']
            user_to_change.first_name = data['first_name']
            user_to_change.last_name = data['last_name']
            user_to_change.age = data['age']
            user_to_change.email = data['email']
            user_to_change.role = data['role']
            user_to_change.phone = data['phone']
            # with db.session.begin():
            db.session.add(user_to_change)
            db.session.commit()
            return jsonify(data)
        else:
            return jsonify('invalid id')

    if request.method == 'DELETE':
        user_to_delete = User.query.get(id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return jsonify(f'Deleted id:{id}')
        else:
            return jsonify('invalid id')


@app.route('/orders', methods=['GET', 'POST'])
def all_orders():
    if request.method == 'GET':
        orders = db.session.query(Order).all()
        orders_list = []
        for order in orders:
            orders_list.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': order.customer_id,
                'executor_id': order.executor_id})
        return jsonify(orders_list)
    elif request.method == 'POST':
        data = json.loads(request.data)
        new_order = Order(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
            address=data['address'],
            price=data['price'],
            customer_id=data['customer_id'],
            executor_id=data['executor_id']
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify('order added')


@app.route('/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_order(id):
    if request.method == 'GET':
        order = Order.query.get(id)
        if order:
            return jsonify({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': order.customer_id,
                'executor_id': order.executor_id})
        else:
            return jsonify('invalid id')
    elif request.method == 'PUT':
        data = json.loads(request.data)
        order_to_change = Order.query.get(id)
        if order_to_change:
            order_to_change.id = data['id']
            order_to_change.name = data['name']
            order_to_change.description = data['description']
            order_to_change.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
            order_to_change.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
            order_to_change.address = data['address']
            order_to_change.price = data['price']
            order_to_change.customer_id = data['customer_id']
            order_to_change.customer_id = data['executor_id']
            db.session.add(order_to_change)
            db.session.commit()
            return jsonify(data)
        else:
            return jsonify('invalid id')

    elif request.method == 'DELETE':
        order_to_delete = Order.query.get(id)
        if order_to_delete:
            db.session.delete(order_to_delete)
            db.session.commit()
            return jsonify(f'Deleted id:{id}')
        else:
            return jsonify('invalid id')


@app.route('/offers', methods=['GET', 'POST'])
def all_offers():
    if request.method == 'GET':
        offers = db.session.query(Offer).all()
        offers_list = []
        for offer in offers:
            offers_list.append({
                'id': offer.id,
                'order_id': offer.order_id,
                'executor_id': offer.executor_id,
            })
        return json.dumps(offers_list)
    elif request.method == 'POST':
        data = json.loads(request.data)
        new_offer = Offer(
            id=data['id'],
            order_id=data['order_id'],
            executor_id=data['executor_id']
        )
        db.session.add(new_offer)
        db.session.commit()
        return jsonify('offer added')


@app.route('/offers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def one_offer(id):
    if request.method == 'GET':
        offer = Offer.query.get(id)
        if offer:
            return json.dumps({
                'id': offer.id,
                'order_id': offer.order_id,
                'executor_id': offer.executor_id, })
        else:
            return jsonify('invalid id')
    if request.method == 'PUT':
        data = json.loads(request.data)
        offer_to_change = Offer.query.get(id)
        if offer_to_change:
            offer_to_change.id = data['id']
            offer_to_change.order_id = data['order_id']
            offer_to_change.executor_id = data['executor_id']
            db.session.add(offer_to_change)
            db.session.commit()
            return jsonify(data)
        else:
            return jsonify('invalid id')
    if request.method == 'DELETE':
        offer_to_delete = Offer.query.get(id)
        if offer_to_delete:
            db.session.delete(offer_to_delete)
            db.session.commit()
            return jsonify(f'Deleted id:{id}')
        else:
            return jsonify('invalid id')


def main():
    print()
    app.run(debug=True)


if __name__ == "__main__":
    db.create_all()
    insert_data()
    main()
