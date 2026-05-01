# Team Task Manager

A full-stack task management app with role-based access (Admin / Member), project creation, task assignment, status tracking, and a dashboard.

## Backend

- Flask REST API
- SQLite database via SQLAlchemy
- JWT authentication
- Admin-only project creation
- Task creation, assignment, and status updates
- Dashboard stats with overdue task tracking

### Run backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Frontend

- React app
- Login / Signup
- Admin dashboard with project/task creation
- Member dashboard with personal tasks and status updates

### Run frontend

```bash
cd frontend
npm install
npm start
```

## Notes

- Backend API runs at `http://127.0.0.1:5000`
- Frontend communicates with the backend using `axios`
- Create an admin user via signup and select Admin role
- Use the dashboard to create projects, assign tasks, and update task status

## Deployment

- The backend can be deployed using Railway or any Python hosting service.
- Set `REACT_APP_API_URL` to your deployed backend URL before building the frontend.
- The root `Procfile` is configured to run the Flask backend with `python backend/app.py`.

## Environment

- Frontend uses `REACT_APP_API_URL` to switch between local and deployed backend URLs.
