from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, current_user, logout_user
from app.forms import RegistrationForm, LoginForm
from app.blockchain import Blockchain
from app.secret import SecretManager
from app.transaction import Transaction
from datetime import datetime

main = Blueprint('main', __name__)
blockchain = Blockchain()
blockchain.load_blockchain()  # Load the blockchain from the JSON file
secret_manager = SecretManager()  # Create an instance of SecretManager

# Initialize an empty list to store contributions (for demonstration purposes)
contributions = []

# Phase details for project phases
phase_details = {
    "Planning": {
        "description": "This phase involves defining the project scope and objectives.",
        "tasks": ["Define project goals", "Identify stakeholders", "Create a project timeline"],
    },
    "Design": {
        "description": "In this phase, detailed designs and specifications are created.",
        "tasks": ["Create architectural designs", "Develop engineering specifications"],
    },
    "Construction": {
        "description": "The actual construction of the project takes place in this phase.",
        "tasks": ["Build structures", "Install systems and equipment"],
    },
    "Commissioning": {
        "description": "Testing and preparing the project for operation.",
        "tasks": ["Test systems", "Ensure compliance with regulations"],
    },
    "Operational": {
        "description": "The project is now operational and producing outputs.",
        "tasks": ["Monitor performance", "Conduct maintenance"],
    },
    "Maintenance": {
        "description": "Ongoing maintenance to ensure project longevity.",
        "tasks": ["Perform regular inspections", "Address issues as they arise"],
    },
    "Evaluation": {
        "description": "Assessing the project's outcomes and sustainability.",
        "tasks": ["Evaluate project success", "Report findings"],
    },
}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/project_overview')
def project_overview():
    """Overview of the project with goals and timeline."""
    return render_template('project_overview.html')

@main.route('/project_phases')
def project_phases():
    """List all project phases with their status."""
    phases = [
        {"name": "Planning", "status": "In Progress"},
        {"name": "Design", "status": "Not Started"},
        {"name": "Construction", "status": "Not Started"},
        {"name": "Commissioning", "status": "Not Started"},
        {"name": "Operational", "status": "Not Started"},
        {"name": "Maintenance", "status": "Not Started"},
        {"name": "Evaluation", "status": "Not Started"},
    ]
    return render_template('project_phases.html', phases=phases)

@main.route('/project_phases/<phase_name>')
def project_phase_details(phase_name):
    """Detailed view of a specific project phase."""
    phase_info = phase_details.get(phase_name)
    if phase_info:
        return render_template('project_phases_details.html', phase_name=phase_name, phase_info=phase_info)
    else:
        flash('Phase not found.', 'danger')
        return redirect(url_for('main.project_phases'))

@main.route('/contribute', methods=['GET', 'POST'])
def contribute():
    """Handle user contributions to the project."""
    if 'username' not in session:
        flash('You need to log in or register to contribute.', 'warning')
        return redirect(url_for('main.login'))  # Redirect to the login page

    if request.method == 'POST':
        contribution = request.form.get('contribution')
        
        # Logic to save the contribution to the blockchain
        new_contribution = {
            "user": session['username'],
            "text": contribution
        }
        
        blockchain.add_contribution(new_contribution)  # Implement this method in your Blockchain class
        
        flash('Your contribution has been submitted successfully!', 'success')
        return redirect(url_for('main.contribute'))
    
    # Fetch contributions from the blockchain
    contributions = blockchain.get_user_contributions(session['username'])  # Implement this method
    return render_template('contribute.html', contributions=contributions)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        secret_phrase = form.secret_phrase.data
        
        # Retrieve user data from the blockchain
        user_data = blockchain.get_user_data(username)  # Implement this method in your Blockchain class
        
        if user_data:
            encrypted_secret_phrase = user_data.get('encrypted_secret_phrase')
            profession = user_data.get('profession')
            
            # Decrypt the stored encrypted secret phrase
            decrypted_secret_phrase = secret_manager.decrypt_secret_phrase(encrypted_secret_phrase)
            
            # Verify the secret phrase
            if decrypted_secret_phrase == secret_phrase:
                session['username'] = username
                session['profession'] = profession
                flash('Login successful! Welcome back.', 'success')
                return redirect_to_dashboard(profession)
            else:
                flash('Invalid secret phrase. Please try again.', 'danger')
        else:
            flash('Invalid username. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    profession = session['profession']
    
    # Redirect to the appropriate dashboard based on profession
    return redirect_to_dashboard(profession)

def redirect_to_dashboard(profession):
    """Redirect to the appropriate dashboard based on the user's profession."""
    if profession == 'civil_engineer':
        return redirect(url_for('main.civil_engineer_dashboard'))
    elif profession == 'mechanical_engineer':
        return redirect(url_for('main.mechanical_engineer_dashboard'))
    elif profession == 'electronics_engineer':
        return redirect(url_for('main.electronics_engineer_dashboard'))
    else:
        return redirect(url_for('main.dashboard'))  # Default dashboard if profession is unknown

@main.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Here you can add logic to process the contact form, such as sending an email or saving to a database
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact_us'))

    return render_template('contact_us.html')

@main.route('/carbon_emission_report')
def carbon_emission_report():
    """Display the carbon emission report."""
    return render_template('carbon_emission_report.html')

@main.route('/engineer_dashboard')
def engineer_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    profession = session['profession']
    
    return render_template('engineer_dashboard.html', username=username, profession=profession)

@main.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile settings."""
    notification_settings = request.form.get('notification_settings')
    
    # Logic to update the user's notification settings in the database
    # Example: user = User.query.get(session['user_id'])
    # user.notification_settings = notification_settings
    # db.session.commit()
    
    flash('Profile settings updated successfully!', 'success')
    return redirect(url_for('main.profile'))

@main.route('/profile')
def profile():
    """Display the user profile."""
    user_data = blockchain.get_user_data(session['username'])  # Fetch user data from blockchain
    contributions = blockchain.get_user_contributions(session['username'])  # Fetch contributions
    return render_template('profile.html', contributions=contributions, user_data=user_data)

@main.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route called")  # Debugging output
    form = RegistrationForm()
    print("Form data:", request.form)  # Debugging output
    if form.validate_on_submit():
        print("Form validated")  # Debugging output
        try:
            username = form.username.data
            secret_phrase = form.secret_phrase.data
            profession = form.profession.data
            
            print(f"Attempting to register user: {username}")  # Debugging output

            # Check if the username is already taken
            if not blockchain.is_username_available(username):
                flash('Username is already taken. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)

            # Logic to save the new user to the blockchain
            encrypted_secret = secret_manager.encrypt_secret_phrase(secret_phrase)
            
            # Append the new user to the blockchain
            success, message = blockchain.add_user(username, encrypted_secret, profession)  # Use the updated method
            print(message)  # Log the message returned from add_user
            
            if not success:
                flash('An error occurred during registration. Please try again.', 'danger')
                return render_template('register.html', form=form)

            print(f"User {username} registered successfully.")  # Debugging output
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            print(f"Error during registration: {e}")  # Debugging output
            flash('An error occurred during registration. Please try again.', 'danger')
    else:
        print("Form errors:", form.errors)  # Debugging output
    
    return render_template('register.html', form=form)

@main.route('/create_project', methods=['GET', 'POST'])
def create_project():
    """Handle the creation of a new project."""
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        description = request.form.get('description')

        # Check if the project name already exists
        existing_project = blockchain.get_project_by_name(project_name)  # Implement this method
        if existing_project:
            flash('A project with this name already exists. Please choose a different name.', 'danger')
            return render_template('create_project.html')

        # Logic to save the new project to the blockchain
        new_project = {
            "project_name": project_name,
            "description": description,
            "created_by": session['username'],
            "timestamp": datetime.now().isoformat()
        }

        # Append the new project to the blockchain
        blockchain.add_project(new_project)

        flash('Project created successfully!', 'success')
        return redirect(url_for('main.project_overview'))

    return render_template('create_project.html')


  