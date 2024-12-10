from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin or Customer

    def __repr__(self):
        return f'<User {self.name}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return f'<Appointment {self.date} {self.time}>'

#routes
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    time = data.get('time')

    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found!'}), 404

    new_appointment = Appointment(user_id=user_id, date=date, time=time)
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment booked successfully!'}), 201

@app.route('/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    # Get the appointment to delete
    appointment = Appointment.query.get_or_404(id)

    # Delete the appointment
    db.session.delete(appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment canceled successfully!'}), 200

@app.route('/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):
    # Get the appointment to update
    appointment = Appointment.query.get_or_404(id)

    # Get the updated data from the request
    data = request.get_json()
    new_date = data.get('date', appointment.date)
    new_time = data.get('time', appointment.time)

    # Update the appointment
    appointment.date = new_date
    appointment.time = new_time

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Appointment updated successfully!'}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
