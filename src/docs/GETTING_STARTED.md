# 🚀 Getting Started with Todo App

## Quick Setup (5 minutes)

### Option 1: Docker (Recommended)
```bash
# Clone and run
git clone <your-repo>
cd todo-app
docker-compose up
```
✅ App running at: http://localhost:3000

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
✅ API running at: http://localhost:8000

#### Frontend Setup
```bash
cd frontend
python -m http.server 8080
```
✅ Frontend at: http://localhost:8080

## 📖 How to Use

1. **Add Todo**: Click "Add Task" and enter details
2. **Complete Todo**: Click the checkbox to mark complete
3. **Edit Todo**: Click on task text to edit
4. **Delete Todo**: Click the delete button
5. **Filter Todos**: Use filter buttons (All/Active/Completed)

## 🔧 Development

### Backend Development
- API docs: http://localhost:8000/docs
- Add new endpoints in `backend/main.py`
- Database models in `backend/src/domain/models.py`

### Frontend Development
- Main logic: `frontend/src/app.js`
- Styling: `frontend/src/styles.css`
- Layout: `frontend/index.html`

### Testing
```bash
cd backend
pytest
```

## 🚀 Deployment

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
```

### Production Build
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 📚 Documentation
- [API Documentation](docs/api/README.md)
- [Architecture Overview](docs/architecture/README.md)
- [Deployment Guide](docs/DEPLOYMENT_CHECKLIST.md)

## 🆘 Troubleshooting

### Common Issues
- **Port already in use**: Change ports in `docker-compose.yml`
- **Database errors**: Check DATABASE_URL in `.env`
- **CORS issues**: Update CORS_ORIGINS in `.env`

### Getting Help
1. Check logs: `docker-compose logs`
2. Review API docs: http://localhost:8000/docs
3. Verify environment: Check `.env` file

---
*Ready to build amazing todos! 🎉*
