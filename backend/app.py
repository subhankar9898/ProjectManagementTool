from dotenv import load_dotenv
import os

load_dotenv() # This loads the variables from your .env file
from flask import Flask, request, jsonify
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from groq import Groq
# --- App Initialization ---
app = Flask(__name__)
load_dotenv()

# --- Database Configuration ---
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Heroku/Render's PostgreSQL URL fix
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Fallback to local MySQL database
    DB_USERNAME = "root"
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = "project_management_tool"
    DB_HOST = "127.0.0.1"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False




# Configure JWT settings (we need a 'secret key' to sign the tokens)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") # Your secret key

# --- Extensions Initialization ---
# Initialize JWT
jwt = JWTManager(app)

# Configure CORS to allow your frontend
CORS(app, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:5173",  # Local development
    "https://projectmanagementtool-khaki.vercel.app", # Your main Vercel app
    "https://projectmanagementtool-n8mk6qnne-subhankar9898s-projects.vercel.app" # The Vercel preview from your screenshot
]}})

# Import and initialize the database *after* app config
from models import db, User, Project, Task, UserStory
db.init_app(app) # Initialize db with the app

# --- A Simple Test Route ---
@app.route('/')
def hello():
    return "Hello, your backend is running!"

# --- User Authentication Endpoints ---

@app.route('/api/register', methods=['POST'])
def register_user():
    # Get the JSON data from the request
    data = request.get_json()

    # Extract fields
    email = data.get('email')
    full_name = data.get('full_name')
    password = data.get('password')
    role = data.get('role', 'Developer') # Default to 'Developer' if not provided

    # Basic validation
    if not email or not full_name or not password:
        return jsonify({"message": "Email, full_name, and password are required!"}), 400

    if role not in ['Admin', 'Manager', 'Developer']:
        return jsonify({"message": "Invalid role!"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered!"}), 400

    # Create new user object
    new_user = User(
        full_name=full_name,
        email=email,
        role=role
    )
    # Hash the password
    new_user.set_password(password)

    # Add to database
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": f"User {full_name} registered successfully as a {role}!"
    }), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    # Get the JSON data from the request
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required!"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Check if user exists and if the password is correct
    if user and user.check_password(password):
        # Create a new access token
        access_token = create_access_token(identity=str(user.id)) # Use str(user.id)
        return jsonify({
            "message": "Login successful!",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            }
        }), 200
    else:
        # If user doesn't exist or password incorrect
        return jsonify({"message": "Invalid email or password!"}), 401

@app.route('/api/protected', methods=['GET'])
@jwt_required()  # This decorator protects the route
def protected_route():
    # Get the user ID from the token (it's a string)
    current_user_id = get_jwt_identity()
    
    # Find the user in the database
    user = User.query.get(int(current_user_id)) # Convert ID to int

    if not user:
        return jsonify({"message": "User not found!"}), 404

    return jsonify({
        "message": f"Hello, {user.email}! You have access.",
        "user_info": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200

# --- Project Module Endpoints ---

@app.route('/api/projects', methods=['POST'])
@jwt_required() # Protect this route
def create_project():
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity()) # We stored it as a string, so convert back to int

    # Get data from the request
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"message": "Project name is required!"}), 400

    # Get the user's role
    user = User.query.get(current_user_id)
    
    # Authorization: Only Admins or Managers can create projects
    if user.role not in ['Admin', 'Manager']:
        return jsonify({"message": "You are not authorized to create projects!"}), 403 # 403 Forbidden

    # Create new project
    new_project = Project(
        name=name,
        description=description,
        owner_id=current_user_id  # The creator is the owner
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        
        # Also add the creator as a member of the project
        new_project.members.append(user)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": "Project created successfully!",
        "project": {
            "id": new_project.id,
            "name": new_project.name,
            "description": new_project.description,
            "owner_id": new_project.owner_id
        }
    }), 201

@app.route('/api/projects', methods=['GET'])
@jwt_required() # Protect this route
def get_all_projects():
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Find the user
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"message": "User not found!"}), 404

    # 'user.projects' works because of the 'backref' we set up
    # in the 'project_members' relationship in models.py
    projects = user.projects 

    # Format the output
    output = []
    for project in projects:
        output.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id
        })

    return jsonify({"projects": output}), 200

@app.route('/api/projects/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_project_member(project_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    # Only Admins or Managers can add members
    if user.role not in ['Admin', 'Manager']:
        return jsonify({"message": "You are not authorized!"}), 403

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"message": "Project not found!"}), 404
    
    data = request.get_json()
    user_id_to_add = data.get('user_id')
    
    if not user_id_to_add:
        return jsonify({"message": "User ID is required!"}), 400

    user_to_add = User.query.get(user_id_to_add)
    if not user_to_add:
        return jsonify({"message": "User not found!"}), 404
        
    if user_to_add in project.members:
        return jsonify({"message": "User is already a member!"}), 400
        
    try:
        project.members.append(user_to_add)
        db.session.commit()
        return jsonify({"message": f"User {user_to_add.full_name} added to project {project.name}."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

# --- Task Module Endpoints ---

@app.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Check user's role
    user = User.query.get(current_user_id)
    if user.role not in ['Admin', 'Manager']:
        return jsonify({"message": "You are not authorized to create tasks!"}), 403

    # Check if the project exists
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"message": "Project not found!"}), 404
    
    # Check if the manager is a member of it
    if user not in project.members:
         return jsonify({"message": "You are not a member of this project!"}), 403

    # Get data from the request
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline') # Expected format: "YYYY-MM-DD"
    assignee_id = data.get('assignee_id') # The ID of the developer to assign

    if not title:
        return jsonify({"message": "Task title is required!"}), 400

    # Optional: Check if the assignee is a real user
    assignee = None
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee or assignee.role != 'Developer':
            return jsonify({"message": "Invalid assignee. User must be a Developer."}), 400
        # Check if assignee is a member of the project
        if assignee not in project.members:
             return jsonify({"message": "Assignee is not a member of this project!"}), 400

    # Create the new task
    new_task = Task(
        title=title,
        description=description,
        deadline=deadline,
        project_id=project.id,
        assignee_id=assignee_id
    )

    try:
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": "Task created successfully!",
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "status": new_task.status,
            "project_id": new_task.project_id,
            "assignee_id": new_task.assignee_id
        }
    }), 201

@app.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks_for_project(project_id):
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Find the user and project
    user = User.query.get(current_user_id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({"message": "Project not found!"}), 404
        
    # Authorization: User must be a member of the project to see its tasks
    if user not in project.members:
         return jsonify({"message": "You are not authorized to view these tasks!"}), 403

    # Get all tasks for the project
    tasks = project.tasks # This works because of the 'relationship' in models.py

    # Format the output
    output = []
    for task in tasks:
        # Get assignee details
        assignee_name = None
        if task.assignee:
            assignee_name = task.assignee.full_name

        output.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline,
            "project_id": task.project_id,
            "assignee_id": task.assignee_id,
            "assignee_name": assignee_name
        })

    return jsonify({"tasks": output}), 200

@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Get the new status from the request
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"message": "New status is required!"}), 400

    if new_status not in ['To Do', 'In Progress', 'Done']:
        return jsonify({"message": "Invalid status value!"}), 400
        
    # Find the task
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found!"}), 404
        
    # Find the user
    user = User.query.get(current_user_id)
    
    # === AUTHORIZATION ===
    # Only the assigned developer OR a manager/admin can change the status
    if user.role == 'Developer' and task.assignee_id != current_user_id:
        # A developer is trying to change a task that isn't theirs
        return jsonify({"message": "You are not authorized to update this task!"}), 403
        
    if user.role not in ['Admin', 'Manager'] and task.assignee_id != current_user_id:
        # A developer (who isn't assigned) is trying to update
        return jsonify({"message": "You are not authorized!"}), 403

    # All checks passed, update the status
    try:
        task.status = new_status
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({
        "message": f"Task status updated to '{new_status}'!",
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "assignee_id": task.assignee_id
        }
    }), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Check user's role
    user = User.query.get(current_user_id)
    if user.role not in ['Admin', 'Manager']:
        return jsonify({"message": "You are not authorized to delete tasks!"}), 403

    # Find the task
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found!"}), 404
        
    # Optional: Check if the manager is part of the project
    # (Good practice, but we'll skip for simplicity)

    # All checks passed, delete the task
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "Task deleted successfully!"}), 200

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    # Get the user ID from the token
    current_user_id = int(get_jwt_identity())
    
    # Find the user and project
    user = User.query.get(current_user_id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({"message": "Project not found!"}), 404
        
    # === AUTHORIZATION ===
    # Only the project owner or an Admin can delete the project
    if user.role != 'Admin' and project.owner_id != current_user_id:
        return jsonify({"message": "You are not authorized to delete this project!"}), 403

    # All checks passed, delete the project
    # Note: Our 'cascade="all, delete-orphan"' in the model
    # should automatically delete all tasks associated with this project.
    try:
        db.session.delete(project)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    return jsonify({"message": "Project deleted successfully!"}), 200

@app.route('/api/dashboard-metrics', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"message": "User not found!"}), 404

    # Get all projects this user is a member of
    user_projects = user.projects

    if not user_projects:
        return jsonify({"total_projects": 0, "total_tasks": 0, "tasks_by_status": {}}), 200

    project_ids = [p.id for p in user_projects]

    # Count all tasks in those projects
    total_tasks = Task.query.filter(Task.project_id.in_(project_ids)).count()

    # Count tasks by status
    todo_count = Task.query.filter(Task.project_id.in_(project_ids), Task.status == 'To Do').count()
    inprogress_count = Task.query.filter(Task.project_id.in_(project_ids), Task.status == 'In Progress').count()
    done_count = Task.query.filter(Task.project_id.in_(project_ids), Task.status == 'Done').count()

    # --- New code for overdue tasks ---
    from sqlalchemy import and_
    today = datetime.utcnow().date()

    overdue_count = Task.query.filter(
        Task.project_id.in_(project_ids),
        Task.deadline < today,
        Task.status != 'Done'
    ).count()
    # --- End new code ---

    return jsonify({
        "total_projects": len(user_projects),
        "total_tasks": total_tasks,
        "tasks_by_status": {
            "To Do": todo_count,
            "In Progress": inprogress_count,
            "Done": done_count
        },
        "tasks_overdue": overdue_count 
    }), 200

# --- BONUS: AI User Story Generator ---

@app.route('/api/projects/<int:project_id>/generate-stories', methods=['POST'])
@jwt_required()
def generate_user_stories(project_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({"message": "Project not found!"}), 404

    # Authorization: Only project members can generate stories
    if user not in project.members or user.role not in ['Admin', 'Manager']:
         return jsonify({"message": "You are not authorized for this project!"}), 403

    data = request.get_json()
    project_description = data.get('projectDescription')
    if not project_description:
        return jsonify({"message": "projectDescription is required!"}), 400

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        system_prompt = "You are an expert Agile project manager. Your task is to generate a list of user stories from a project description. You must ONLY return a JSON object in the format {\"userStories\": [\"...\", \"...\"]}. Each string must follow the format: 'As a [role], I want to [action], so that [benefit].'"
        user_prompt = f"Here is the project description: '{project_description}'"

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        response_content = chat_completion.choices[0].message.content

        # 5. Parse and Save the stories
        import json
        response_json = json.loads(response_content)

        stories_list = []
        if isinstance(response_json, dict) and "userStories" in response_json:
            stories_list = response_json.get("userStories", [])
        elif isinstance(response_json, list):
            stories_list = [item for item in response_json if isinstance(item, str) and item.strip()]

        # --- New Part: Save to Database ---
        new_stories = []
        for story_text in stories_list:
            new_story = UserStory(story_text=story_text, project_id=project.id)
            db.session.add(new_story)
            new_stories.append(new_story)
        db.session.commit()
        # --- End New Part ---

        # Return the new stories as a list of dictionaries
        return jsonify([story.to_dict() for story in new_stories]), 201

    except Exception as e:
        print(f"AI generation error: {e}")
        return jsonify({"message": "Error generating AI user stories."}), 500
    
@app.route('/api/projects/<int:project_id>/stories', methods=['GET'])
@jwt_required()
def get_user_stories(project_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({"message": "Project not found!"}), 404
    if user not in project.members:
         return jsonify({"message": "You are not authorized to view this project!"}), 403

    stories = [story.to_dict() for story in project.stories]
    return jsonify(stories), 200
    
@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def edit_project(project_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    project = Project.query.get(project_id)

    if not project:
        return jsonify({"message": "Project not found!"}), 404

    # Authorization: Only Admin or the project owner can edit
    if user.role != 'Admin' and project.owner_id != current_user_id:
        return jsonify({"message": "You are not authorized to edit this project!"}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({"message": "Project name is required!"}), 400

    try:
        project.name = name
        project.description = description
        db.session.commit()
        
        # Return the updated project
        return jsonify({
            "message": "Project updated successfully!",
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "owner_id": project.owner_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    # Authorization: Only Admin or Manager can edit task details
    if user.role not in ['Admin', 'Manager']:
        return jsonify({"message": "You are not authorized to edit this task!"}), 403

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Task not found!"}), 404

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    deadline = data.get('deadline')
    assignee_id = data.get('assignee_id')

    if not title:
        return jsonify({"message": "Task title is required!"}), 400

    try:
        task.title = title
        task.description = description
        task.deadline = deadline
        
        # Optional: Validate new assignee_id if it's provided
        if assignee_id:
            assignee = User.query.get(assignee_id)
            if not assignee or assignee.role != 'Developer':
                return jsonify({"message": "Invalid assignee ID!"}), 400
            if assignee not in task.project.members:
                    return jsonify({"message": "Assignee is not a member of this project!"}), 400
            task.assignee_id = assignee_id
        else:
            task.assignee_id = None # Allow un-assigning

        db.session.commit()
        
        return jsonify({
            "message": "Task updated successfully!",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assignee_id": task.assignee_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500

# --- Run the App ---
# This makes the app runnable with `python app.py`
if __name__ == '__main__':
    app.run(debug=True)
