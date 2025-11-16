# Project Management Tool

A robust full-stack Project Management Application designed to streamline team workflows. It features role-based access control (RBAC) for Managers and Developers, a dynamic task tracking system, and a real-time dashboard for project metrics. Uniquely, it integrates the Groq API to automatically generate detailed user stories from simple project descriptions.

**Developed by:** Subhankar Prusty

---

## 🚀 Live Demo

* **Frontend Deployment:** [!! INSERT YOUR VERCEL LINK HERE !!]
* **Backend Deployment:** [!! INSERT YOUR RENDER LINK HERE !!]

---

## 🌟 Key Features

* **User Authentication:** Secure registration and login using **JWT (JSON Web Tokens)** with hashed passwords (`bcrypt`).
* **Role-Based Access:**
    * **Managers:** Can create/delete projects, add team members, create/assign/delete tasks, and view dashboard metrics.
    * **Developers:** Can view assigned tasks and update status (To Do -> In Progress -> Done).
* **Project & Task Management:** Full CRUD capabilities for managing workflow.
* **Dashboard Metrics:** Real-time view of "Total Projects", "Total Tasks", "Tasks by Status", and an **"Overdue Tasks"** alert system.
* **BONUS: AI-Powered User Stories:** Uses the **GROQ API** (Llama-3.1-8b-instant model) to instantly generate agile user stories based on a text description of a project and saves them to the database.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React.js (Vite), Axios, React Router |
| **Backend** | Python (Flask), Flask-RESTful |
| **Database** | MySQL (Local Development) / PostgreSQL (Production) |
| **ORM** | Flask-SQLAlchemy |
| **Authentication** | Flask-JWT-Extended |
| **AI Integration** | Groq Python SDK |
| **Testing** | Pytest |

---

## 📁 Project Folder Structure

```plaintext
📦 ProjectManagementTool
├── 📂 backend
│   ├── app.py
│   ├── 📂 models
│   ├── 📂 routes
│   ├── 📂 services
│   ├── 📂 tests
│   └── requirements.txt
│
├── 📂 frontend
│   ├── 📂 src
│   ├── 📂 public
│   └── package.json
|
├── ERD of Project Management Tool Project.pdf
|
├──ProjectManagementTool.postman_collection.json
|
└── README.md


```
---

## ⚙️ Local Setup Instructions

Follow these steps to run the project on your local machine.

### Prerequisites
* Python 3.10+
* Node.js & npm
* MySQL Server (running locally)

### 1. Clone the Repository
```bash
git clone https://github.com/subhankar9898/ProjectManagementTool.git

cd ProjectManagementTool
```
### 2. Backend Setup

Navigate to the backend folder:

````Bash

cd backend
````

Create and activate a virtual environment:

```Bash

python -m venv venv
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (CMD):
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

Install dependencies:

```Bash

pip install -r requirements.txt
```

Configure Environment Variables: Create a file named .env in the backend folder and add the following:

```bash
DB_PASSWORD=your_local_mysql_password
JWT_SECRET_KEY=any_random_super_secret_key
GROQ_API_KEY=your_gsk_..._key_from_groq
```
(Note: If your MySQL password contains special characters like @, URL-encode them, e.g., %40).

Database Setup: Open your MySQL client (Workbench) and run the following SQL commands to create your databases and tables:

```bash

CREATE DATABASE project_management_tool;
CREATE DATABASE test_project_management_tool;
USE project_management_tool;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Manager', 'Developer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE project_members (
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('To Do', 'In Progress', 'Done') NOT NULL DEFAULT 'To Do',
    deadline DATE,
    project_id INT NOT NULL,
    assignee_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE user_stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    story_text TEXT NOT NULL,
    project_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```
Run the server:

```Bash

python app.py

```
Server will run at http://127.0.0.1:5000

### 3. Frontend Setup

Open a new terminal and navigate to the frontend folder:

```Bash

cd frontend
```

Install dependencies:

```Bash

npm install
```

Run the development server:

```Bash

npm run dev
```
App will run at http://localhost:5173


## 📡 API Endpoints Summary

### Authentication
* `POST /api/register` - Register new user (Manager/Developer/Admin)
* `POST /api/login` - Login and receive access token

### Projects
* `GET /api/projects` - Get all projects for logged-in user
* `POST /api/projects` - Create a new project
* `PUT /api/projects/<id>` - Edit project details
* `DELETE /api/projects/<id>` - Delete a project
* `POST /api/projects/<id>/members` - Add a developer to a project

### Tasks
* `GET /api/projects/<id>/tasks` - Get all tasks for a project
* `POST /api/projects/<id>/tasks` - Create a new task
* `PUT /api/tasks/<id>` - Edit task details
* `DELETE /api/tasks/<id>` - Delete a task
* `PATCH /api/tasks/<id>/status` - Update task status

### AI & Dashboard
* `GET /api/dashboard-metrics` - Get stats (Overdue, Total, Status counts)
* `POST /api/projects/<id>/generate-stories` - Generate AI user stories via GROQ
* `GET /api/projects/<id>/stories` - View saved user stories

---


## 🤖 How the AI Feature Works

The AI User Story Generator is a bonus feature designed to assist Project Managers.
1.  A Manager enters a plain-text project description (e.g., "An app for booking appointments...").
2.  When submitted, the backend API (`POST /api/projects/<id>/generate-stories`) securely calls the **GROQ API** using a high-speed Llama 3 model.
3.  A specific system prompt instructs the AI to return a JSON object containing a list of user stories in the "As a..., I want to..., so that..." format.
4.  The backend parses the AI's response, saves each story to the `user_stories` table in the database, and links it to the project.
5.  The frontend then re-fetches the list of stories and displays them on the page.

---

## 📁 Deliverables Included
* **Source Code:** Complete frontend and backend code.
* **ER Diagram:** `ERD.pdf` (You must add this file to your repository).
* **Postman Collection:** `ProjectManagementTool.postman_collection.json` (You must export this from Postman and add it to your repository).

---

## 🧪 Testing
Unit tests for backend security and logic are included.
To run tests:
```bash
cd backend
```
pytest

---

## 🔮 Assumptions & Improvements
* **Assumption:** The system currently relies on manual role assignment during registration (Admin/Manager/Developer).
* **Improvement:** Future versions could include a dedicated "Admin Panel" UI for user management.
* **Improvement:** Adding a drag-and-drop interface (Kanban) for easier task status updates.

---

## 📄 License

This project is open-source and licensed under the **MIT License**.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page or submit a pull request.

---

## 🙏 Acknowledgements

* This project was built to demonstrate full-stack development skills.
* Thanks to **Groq** for providing an incredibly fast and accessible LLM API.

---
