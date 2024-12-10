import pytest
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app import app, db, User, Appointment  # Assuming app, db, and models are in app.py
import random
import string

@pytest.fixture(scope='module')
def test_client():
    # Set up the Flask test client
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'  # Use a separate test database
    app.config['TESTING'] = True
    client = app.test_client()

    # Create tables before running tests
    with app.app_context():
        db.create_all()
    yield client

    # Drop tables after tests are done
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def new_user(test_client):
    # Create a new user for testing within the app context with a unique email
    unique_email = f"test{random.randint(1000, 9999)}@example.com"  # Ensure the email is unique
    with app.app_context():
        user = User(name="Test User", email=unique_email, role="Customer")
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture(scope='function')
def new_appointment(new_user, test_client):
    # Create a new appointment for testing within the app context
    with app.app_context():
        appointment = Appointment(user_id=new_user.id, date="2024-12-15", time="10:00 AM")
        db.session.add(appointment)
        db.session.commit()
    return appointment

def test_add_appointment(test_client, new_user):
    # Test adding an appointment
    response = test_client.post('/appointments', json={
        'user_id': new_user.id,
        'date': '2024-12-15',
        'time': '10:00 AM'
    })
    assert response.status_code == 201
    assert b'Appointment booked successfully!' in response.data

def test_update_appointment(test_client, new_appointment):
    # Test updating an appointment
    appointment = Appointment.query.first()
    response = test_client.put(f'/appointments/{appointment.id}', json={
        'date': '2024-12-16',
        'time': '11:00 AM'
    })
    assert response.status_code == 200
    assert b'Appointment updated successfully!' in response.data

    # Verify the changes in the database
    updated_appointment = Appointment.query.get(appointment.id)
    assert updated_appointment.date == '2024-12-16'
    assert updated_appointment.time == '11:00 AM'

def test_delete_appointment(test_client, new_appointment):
    # Test deleting an appointment
    appointment = Appointment.query.first()
    response = test_client.delete(f'/appointments/{appointment.id}')
    assert response.status_code == 200
    assert b'Appointment canceled successfully!' in response.data

    # Verify the appointment is deleted
    deleted_appointment = Appointment.query.get(appointment.id)
    assert deleted_appointment is None

def test_add_appointment_user_not_found(test_client):
    # Test adding an appointment for a non-existent user
    response = test_client.post('/appointments', json={
        'user_id': 9999,  # Invalid user ID
        'date': '2024-12-15',
        'time': '10:00 AM'
    })
    assert response.status_code == 404
    assert b'User not found!' in response.data
