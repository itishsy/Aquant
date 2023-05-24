#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(port=5000, host='172.172.4.131', debug=True)
