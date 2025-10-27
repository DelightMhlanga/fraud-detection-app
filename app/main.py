from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Fraud Detection System is running!"