from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional
import json
SQLALCHEMY_DATABASE_URL = "sqlite:///./arctic.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="Ученик")
    region = Column(String, default="Москва")
    avatar_url = Column(String, default="https://api.dicebear.com/7.x/bottts/svg?seed=arctic")
    is_verified = Column(Boolean, default=True)
    passed_test = Column(Boolean, default=False)
class DBProject(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    nomination = Column(String, default="Экология Арктики")
    annotation = Column(String, nullable=True)
    file_url = Column(String, nullable=True)
    status = Column(String, default="на проверке")
    author_username = Column(String, index=True)
    average_score = Column(Float, default=0.0)
class DBExpertReview(Base):
    __tablename__ = "expert_reviews"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer)
    expert_username = Column(String)
    relevance_score = Column(Integer, default=0)
    innovation_score = Column(Integer, default=0)
    feasibility_score = Column(Integer, default=0)
    comment = Column(String, nullable=True)
class DBTest(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Вступительное тестирование")
    description = Column(Text, default="Тестирование по материалам арктических исследований.")
    questions_json = Column(Text)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Arctic Minimal API", version="8.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_test(db: Session):
    if not db.query(DBTest).first():
        default_questions = [
            {"id": "1", "q": "На сколько процентов СМП сокращает доставку из Европы в Азию?", "type": "choice", "opts": ["На 15%", "На 40%", "На 70%"], "correct": "На 40%"},
            {"id": "2", "q": "Какая часть территории РФ находится в зоне вечной мерзлоты?", "type": "choice", "opts": ["Около 25%", "Более 60%", "Ровно 90%"], "correct": "Более 60%"},
            {"id": "3", "q": "Какой вид энергетики наиболее эффективен в полярную ночь?", "type": "choice", "opts": ["Солнечные батареи", "Ветроэнергетика", "Геотермальные станции"], "correct": "Ветроэнергетика"},
            {"id": "4", "q": "Какие приборы применяются для контроля многолетнемерзлых грунтов?", "type": "choice", "opts": ["Автономные термометрические датчики", "Оптические телескопы", "Метеозонды"], "correct": "Автономные термометрические датчики"},
            {"id": "5", "q": "В каком океане расположен Северный морской путь?", "type": "choice", "opts": ["Тихий океан", "Северный Ледовитый океан", "Индийский океан"], "correct": "Северный Ледовитый океан"},
            {"id": "6", "q": "Кто является главным хозяином и символом Арктики?", "type": "choice", "opts": ["Бурый медведь", "Белый медведь", "Арктический волк"], "correct": "Белый медведь"},
            {"id": "7", "q": "Какой заповедник известен как «родильный дом» белых медведей?", "type": "choice", "opts": ["Медвежьи острова", "Таймырский", "Врангелевский"], "correct": "Медвежьи острова"},
            {"id": "8", "q": "Преобладающий тип грунта на большей части севера Якутии:", "type": "choice", "opts": ["Песчаные дюны", "Многолетняя мерзлота", "Чернозем"], "correct": "Многолетняя мерзлота"},
            {"id": "9", "q": "Метод наблюдения за белыми медведями с воздуха:", "type": "choice", "opts": ["Авиамониторинг", "Спутниковый радар", "Эхолокация"], "correct": "Авиамониторинг"},
            {"id": "10", "q": "Что обеспечивает проводку судов по СМП круглый год?", "type": "choice", "opts": ["Ледокольный флот", "Буксиры", "Танкеры"], "correct": "Ледокольный флот"},
            {"id": "11", "q": "Какое море омывает побережье Ямала и Гыдана?", "type": "choice", "opts": ["Карское море", "Охотское море", "Черное море"], "correct": "Карское море"},
            {"id": "12", "q": "Какое море расположено к западу от Карского?", "type": "choice", "opts": ["Баренцево море", "Берингово море", "Каспийское море"], "correct": "Баренцево море"},
            {"id": "13", "q": "Самый северный город и порт материковой России:", "type": "choice", "opts": ["Диксон", "Дудинка", "Певек"], "correct": "Диксон"},
            {"id": "14", "q": "Крупный арктический порт на реке Лена:", "type": "choice", "opts": ["Тикси", "Хатанга", "Амдерма"], "correct": "Тикси"},
            {"id": "15", "q": "Комплекс мероприятий по оценке воздействия на северную природу:", "type": "choice", "opts": ["Экологический мониторинг", "Аудит финансов", "Геодезия"], "correct": "Экологический мониторинг"},
            {"id": "16", "q": "Введите название региона/полярной зоны (в нижнем регистре):", "type": "text", "correct": "арктика"},
            {"id": "17", "q": "Введите термин, обозначающий многолетнемерзлые грунты (в нижнем регистре):", "type": "text", "correct": "мерзлота"},
            {"id": "18", "q": "Введите полное название главного транспортного коридора (СМП, в нижнем регистре):", "type": "text", "correct": "северный морской путь"},
            {"id": "19", "q": "Введите ледяную глыбу, плавающую в океане (в нижнем регистре):", "type": "text", "correct": "айсберг"},
            {"id": "20", "q": "Введите науку о взаимоотношениях живых организмов со средой (в нижнем регистре):", "type": "text", "correct": "экология"}
        ]
        test_obj = DBTest(title="Вступительное тестирование", questions_json=json.dumps(default_questions, ensure_ascii=False))
        db.add(test_obj)
        db.commit()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    init_default_test(db)
    db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.broadcast_count()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_count(self):
        count = len(self.active_connections)
        for connection in self.active_connections:
            try:
                await connection.send_json({"type": "ONLINE_COUNT", "count": count})
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/online")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_count()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "Ученик"
    region: str = "Москва"
    captcha_answer: int

class UserLogin(BaseModel):
    username: str
    password: str

class ProfileUpdate(BaseModel):
    username: str
    new_username: Optional[str] = None
    avatar_url: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    nomination: str
    annotation: str
    file_url: Optional[str] = ""
    author_username: Optional[str] = "Гость"

class ReviewCreate(BaseModel):
    project_id: int
    expert_username: str
    relevance_score: int
    innovation_score: int
    feasibility_score: int
    comment: str

class QuizSubmission(BaseModel):
    username: Optional[str] = None
    answers: Dict[str, str]

@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if user.captcha_answer != 8:
        raise HTTPException(status_code=400, detail="Неверный ответ на капчу (3 + 5 = 8)")
    if db.query(DBUser).filter((DBUser.username == user.username) | (DBUser.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    passed = True if user.role == "Партнер" else False
    db_user = DBUser(
        username=user.username, email=user.email, password=user.password,
        role=user.role, region=user.region, is_verified=True, passed_test=passed,
        avatar_url=f"https://api.dicebear.com/7.x/bottts/svg?seed={user.username}"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Успешно", "username": db_user.username, "role": db_user.role}

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter((DBUser.username == user.username) | (DBUser.email == user.username)).filter(DBUser.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    return {"username": db_user.username, "role": db_user.role, "region": db_user.region, "avatar_url": db_user.avatar_url, "passed_test": db_user.passed_test}

@app.post("/profile/update")
def update_profile(profile: ProfileUpdate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == profile.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Не найден")
    if profile.new_username and profile.new_username.strip():
        db_user.username = profile.new_username
    if profile.avatar_url and profile.avatar_url.strip():
        db_user.avatar_url = profile.avatar_url
    db.commit()
    db.refresh(db_user)
    return {"message": "Обновлено", "username": db_user.username, "avatar_url": db_user.avatar_url}

@app.get("/test/active")
def get_active_test(db: Session = Depends(get_db)):
    test_obj = db.query(DBTest).first()
    questions = json.loads(test_obj.questions_json)
    safe_questions = [{"id": q["id"], "q": q["q"], "type": q["type"], **({"opts": q["opts"]} if "opts" in q else {})} for q in questions]
    return {"title": test_obj.title, "description": test_obj.description, "questions": safe_questions}

@app.post("/quiz/submit")
def submit_quiz(submission: QuizSubmission, db: Session = Depends(get_db)):
    # Тест доступен всем — авторизация НЕ требуется
    test_obj = db.query(DBTest).first()
    questions = json.loads(test_obj.questions_json)
    correct = sum(
        1 for q in questions
        if str(submission.answers.get(q["id"], "")).strip().lower() == q["correct"].lower()
    )
    percentage = round((correct / len(questions)) * 100, 1)
    passed = percentage >= 70.0

    # Если пользователь авторизован — сохраняем результат
    if submission.username:
        user = db.query(DBUser).filter(DBUser.username == submission.username).first()
        if user and passed:
            user.passed_test = True
            db.commit()

    return {
        "correct_answers": correct,
        "total_questions": len(questions),
        "score_percentage": percentage,
        "passed": passed,
    }

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    return db.query(DBProject).all()

@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Проверка авторизации/теста отключена — проект может создать любой
    db_proj = DBProject(
        name=project.name,
        nomination=project.nomination,
        annotation=project.annotation,
        file_url=project.file_url,
        author_username=project.author_username or "Гость",
        status="на проверке",
    )
    db.add(db_proj)
    db.commit()
    db.refresh(db_proj)
    return db_proj

@app.post("/expert/review")
def submit_expert_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = DBExpertReview(project_id=review.project_id, expert_username=review.expert_username, relevance_score=review.relevance_score, innovation_score=review.innovation_score, feasibility_score=review.feasibility_score, comment=review.comment)
    db.add(db_review)
    proj = db.query(DBProject).filter(DBProject.id == review.project_id).first()
    if proj:
        reviews = db.query(DBExpertReview).filter(DBExpertReview.project_id == review.project_id).all()
        proj.average_score = round(sum([(r.relevance_score + r.innovation_score + r.feasibility_score) / 3 for r in reviews]) / len(reviews), 1)
        proj.status = "оценен"
    db.commit()
    return {"message": "Сохранено"}

@app.get("/admin/analytics")
def get_analytics(db: Session = Depends(get_db)):
    return {
        "total_participants": db.query(DBUser).count(),
        "total_projects": db.query(DBProject).count(),
        "users_by_role": {role: db.query(DBUser).filter(DBUser.role == role).count() for role in ['Ученик', 'Учитель', 'Эксперт', 'Партнер', 'Админ']},
        "regions_covered": 32
    }