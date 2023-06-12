from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, forms, errors, signal_view, ticket_view, trade_view, component_view
