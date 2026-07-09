# LGC System — Local Government Complaint Management

## Project overview
Flask + MySQL web application for managing citizen complaints at local government level.

## Tech stack
- Backend: Python, Flask
- Database: MySQL
- Frontend: HTML, CSS, JavaScript, Chart.js
- Auth: Werkzeug password hashing + SHA2 dual verification
- Deploy: Railway

## Roles
- Citizen: register, submit complaints, track status
- Staff: view and update assigned complaints
- Admin: manage staff, view all complaints, dashboards

## Key rules
- Never hardcode credentials — use .env always
- Debug mode must be False in production
- All routes must have error handling
- Passwords never stored in plain text

## Current status
- [ ] Environment variables setup
- [ ] Gitignore created
- [ ] Dummy data removed
- [ ] README updated
- [ ] Deployment prep done
