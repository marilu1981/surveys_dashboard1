"""
Authentication configuration for the Surveys Dashboard
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Configuration for authentication
AUTH_CONFIG = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': 'Admin User',
                'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # 'password'
            },
            'marilu': {
                'name': 'Marilu Smith',
                'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # 'password'
            }
        }
    },
    'cookie': {
        'name': 'surveys_dashboard_cookie',
        'key': 'some_signature_key',
        'expiry_days': 30
    },
    'preauthorized': {
        'emails': ['admin@example.com']
    }
}

def get_authenticator():
    """Get the authenticator instance"""
    return stauth.Authenticate(
        AUTH_CONFIG['credentials'],
        AUTH_CONFIG['cookie']['name'],
        AUTH_CONFIG['cookie']['key'],
        AUTH_CONFIG['cookie']['expiry_days'],
        AUTH_CONFIG['preauthorized']
    )

def hash_password(password):
    """Hash a password for storage"""
    return stauth.Hasher([password]).generate()[0]

def add_user(username, name, password):
    """Add a new user to the configuration"""
    hashed_password = hash_password(password)
    AUTH_CONFIG['credentials']['usernames'][username] = {
        'name': name,
        'password': hashed_password
    }
    return AUTH_CONFIG
