import re

def password_validator(password: str) -> list:
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if password.isdigit():
        errors.append("Password must contain non-numeric characters.")
    
    if password.lower() in ['password', '12345678', 'qwerty', 'abc123', 'iloveyou', 'welcome', 'admin', 'letmein', 'monkey', 'dragon', 'football', 'user', 'test']:
        errors.append("Password is too common.")
    
    if password.isspace() or not password:
        errors.append("Password cannot be empty or just whitespace.")
    
    if password.lower() == password or password.upper() == password:
        errors.append("Password must contain both uppercase and lowercase characters.")
    
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit.")
    
    if not any(char.isalpha() for char in password):
        errors.append("Password must contain at least one letter.")
    
    if not any(char in '!@#$%^&*_' for char in password):
        errors.append("Password must contain at least one special character (!@#$%^&*_).")
    
    if ' ' in password:
        errors.append("Password cannot contain spaces.")
    
    if len(set(password)) < 4:
        errors.append("Password must contain at least 4 unique characters.")
    
    if any(ord(char) < 32 or ord(char) > 126 for char in password):
        errors.append("Password contains invalid characters.")
    
    return errors

def username_validator(username: str) -> list:
    errors = []
    
    if len(username) < 4 or len(username) > 150:
        errors.append("Username must be between 4 and 30 characters long.")
    
    if not username.isalnum():
        errors.append("Username can only contain letters and numbers.")
    
    if username.lower() in ['admin', 'user', 'test', 'guest', 'root', 'system']:
        errors.append("This username is reserved. Please choose another one.")
    
    if ' ' in username:
        errors.append("Username cannot contain spaces.")
    
    return errors

def first_name_validator(f_name: str) -> list:
    errors = []
    
    if not f_name.isalpha():
        errors.append("First name can only contain alphabetic characters.")
    
    if len(f_name) < 2 or len(f_name) > 150:
        errors.append("First name must be between 2 and 150 characters long.")
    
    return errors

def last_name_validator(l_name: str) -> list:
    errors = []
    
    if not l_name.isalpha():
        errors.append("Last name can only contain alphabetic characters.")
    
    if len(l_name) < 2 or len(l_name) > 150:
        errors.append("Last name must be between 2 and 150 characters long.")
    
    return errors

def phone_number_validator(phone_number: str) -> list:
    pattern = r"^(?:9\d{9}|09\d{9}|\+?98\d{10})$"
    
    if not re.fullmatch(pattern, phone_number):
        return ["Phone Number is not valid."]
    