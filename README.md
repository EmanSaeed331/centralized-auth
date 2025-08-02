# Centralized Authentication System

A FastAPI-based centralized authentication system with LDAP integration and group-based authorization.

## 🚀 Features

- LDAP authentication with OpenLDAP integration
- Group-based authorization (GroupA/GroupB access control)
- Secure session management
- Docker containerization
- Interactive API documentation

## 🛠️ Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/Emansaeed331/centralized-auth.git
cd centralized-auth
```

2. **Start the application:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Web App: http://localhost:8080
- API Docs: http://localhost:8080/docs

## 👤 Test Users

| Username | Password | Groups | Dashboard Access |
|----------|----------|--------|------------------|
| `user1` | `password1` | GroupA | Admin Dashboard |
| `user2` | `password2` | GroupB | User Dashboard |

## 🔧 Local Development (Optional)

If you want to run without Docker:

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start LDAP server:**
```bash
docker-compose up openldap -d
```

4. **Run application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Usage Instructions

### How to Use the Application

1. **Start the system:**
```bash
docker-compose up --build
```

2. **Open your browser and go to:** http://localhost:8080

3. **Login with test users:**
   - **alice/password123** → Access to Admin Dashboard
   - **bob/password123** → Access to User Dashboard  
   - **charlie/password123** → Access to Both Dashboards

4. **Navigate between dashboards:**
   - Admin users see administrative functions
   - Regular users see standard user interface
   - Mixed permissions allow access to both

5. **Logout:** Click the logout link to end your session

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirects to appropriate dashboard |
| `/login` | GET/POST | Login page and authentication |
| `/dashboard-a` | GET | Admin dashboard (GroupA) |
| `/dashboard-b` | GET | User dashboard (GroupB) |
| `/logout` | GET | Logout and clear session |
| `/docs` | GET | Interactive API documentation |

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file to customize:
```env
LDAP_SERVER=localhost
LDAP_PORT=1389
LDAP_BASE_DN=dc=example,dc=org
```

### Docker Commands
```bash
# Start services
docker-compose up --build

# Run in background  
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs app
```

## 🧪 Testing

### Manual Testing
1. Start application: `docker-compose up --build`
2. Go to http://localhost:8080
3. Try logging in with test users (alice, bob, charlie)
4. Verify proper dashboard access based on groups
5. Test logout functionality

### API Testing
```bash
# Test login
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=password1"
```

## 🚨 Troubleshooting

**LDAP Connection Issues:**
```bash
docker-compose logs openldap
```

**Authentication Problems:**
- Check username/password (case sensitive)
- Verify user exists in LDAP
- Check application logs: `docker-compose logs app`

**Permission Denied:**
- Verify user belongs to correct group
- Check session is active (refresh browser)

## 📁 Project Structure

```
centralized-auth/
├── main.py              # FastAPI application
├── auth.py              # LDAP authentication
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service setup
├── ldap-seed.ldif       # Test LDAP data
└── app/templates/       # HTML templates
    ├── login.html
    ├── dashboard_a.html
    └── dashboard_b.html
```

## 🔐 Security Features

- Secure session management (1-hour timeout)
- LDAP authentication with group authorization
- CSRF protection
- HttpOnly cookies
- Input validation and sanitization 