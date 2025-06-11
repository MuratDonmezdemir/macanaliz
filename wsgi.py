"""
WSGI config for MacAnaliz project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
from app import create_app

# Create application instance
application = create_app("config.DevelopmentConfig")

if __name__ == "__main__":
    application.run(debug=True)
