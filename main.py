from fastapi import FastAPI, Form, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from auth import LDAPAuth
import secrets
from typing import Optional

app = FastAPI(title="Centralized Auth Demo")

# Add session middleware with a secure random key
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    session_cookie="auth_session",
    max_age=3600  # 1 hour session
)

# Mount templates directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to login page if not authenticated, otherwise to appropriate dashboard."""
    if "username" not in request.session:
        return RedirectResponse(url="/login")
    
    if "GroupA" in request.session.get("groups", []):
        return RedirectResponse(url="/dashboard-a")
    elif "GroupB" in request.session.get("groups", []):
        return RedirectResponse(url="/dashboard-b")
    
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page."""
    # Clear any existing session
    request.session.clear()
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission."""
    authenticated, groups = LDAPAuth.authenticate_user(username, password)
    
    if not authenticated:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )
    
    # Store user info in session
    request.session["username"] = username
    request.session["groups"] = groups
    
    # Redirect based on group membership
    if "GroupA" in groups:
        return RedirectResponse(url="/dashboard-a", status_code=303)
    elif "GroupB" in groups:
        return RedirectResponse(url="/dashboard-b", status_code=303)
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "No valid group membership"}
        )

@app.get("/dashboard-a", response_class=HTMLResponse)
async def dashboard_a(request: Request):
    """Show admin dashboard (Group A)."""
    # Check authentication
    if "username" not in request.session:
        return RedirectResponse(url="/login")
    
    # Check authorization
    if "GroupA" not in request.session.get("groups", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return templates.TemplateResponse(
        "dashboard_a.html",
        {
            "request": request,
            "username": request.session["username"],
            "groups": request.session["groups"]
        }
    )

@app.get("/dashboard-b", response_class=HTMLResponse)
async def dashboard_b(request: Request):
    """Show user dashboard (Group B)."""
    # Check authentication
    if "username" not in request.session:
        return RedirectResponse(url="/login")
    
    # Check authorization
    if "GroupB" not in request.session.get("groups", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return templates.TemplateResponse(
        "dashboard_b.html",
        {
            "request": request,
            "username": request.session["username"],
            "groups": request.session["groups"]
        }
    )

@app.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    request.session.clear()
    return RedirectResponse(url="/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 