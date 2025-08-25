#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
from web_app import app

if __name__ == "__main__":
    app.run()