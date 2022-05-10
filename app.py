from fastapi import FastAPI, Depends, Request, Form, status
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from joblib import load
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
import pandas as pd
from database import SessionLocal, engine
import re


models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app = FastAPI()
 


class DataModel(BaseModel):

    label: float 
    study_and_condition: str
    #class Config:
      #orm_mode = True

#Esta función retorna los nombres de las columnas correspondientes con el modelo esxportado en joblib.
    def columns(self):
        return ["label","study_and_condition"] 


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("base.html",
                                      {"request": request, "todo_list": todos})

@app.post("/addArbol")
def add( request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    diccionario = {"label":[0.0],"study_and_condition": [title]}
    df = pd.DataFrame(diccionario)
    x = df["study_and_condition"]
    print(df)
    model = load("assets/modeloP1E2Arbol.pkl")
    result = model.predict(x)
    new_todo = models.Todo(title = result[0])
    db.add(new_todo)   
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

def limpiar(texto):
    '''
    Esta función limpia el texto de diferentes palabras y caracteres que puedan no afectar el modelo
    El orden en el que se va limpiando el texto no es arbitrario.
    El listado de signos de puntuación se ha obtenido de: print(string.punctuation)
    y re.escape(string.punctuation)
    '''
    
    # Se convierte todo el texto a minúsculas
    nuevo_texto = texto.lower()
    # Eliminación de signos de puntuación
    regex = '[\\!\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\,\\-\\.\\/\\:\\;\\<\\=\\>\\?\\@\\[\\\\\\]\\^_\\`\\{\\|\\}\\~]'
    nuevo_texto = re.sub(regex , ' ', nuevo_texto)
    # Eliminación de conjunciones y palabras innecesarias (o que se repiten en todas las filas)
    conj = [" and "," are "," for "," of "," with "," to "," as "," or "," do "," the "," in "," than ", "study ", " interventions "]
    for i in conj:
        nuevo_texto = re.sub(i, ' ', nuevo_texto)
    # Eliminación de números
    nuevo_texto = re.sub("\d+", ' ', nuevo_texto)
    # Eliminación de espacios en blanco múltiples
    nuevo_texto = re.sub("\\s+", ' ', nuevo_texto)

    return(nuevo_texto)

@app.post("/addRandom")
def add( request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    diccionario = {"label":[0.0],"study_and_condition": [title]}
    df = pd.DataFrame(diccionario)
    x = df["study_and_condition"]
    print(df)
    model = load("assets/modeloP1E2Forest.pkl")
    result = model.predict(x)
    new_todo = models.Todo(title = result[0])
    db.add(new_todo)   
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.post("/addRegresion")
def add( request: Request, title: str = Form(...), db: Session = Depends(get_db)):
    diccionario = {"label":[0.0],"study_and_condition": [title]}
    df = pd.DataFrame(diccionario)
    x = df["study_and_condition"]
    print(df)
    model = load("assets/modeloP1E2Regresion.pkl")
    result = model.predict(x)
    new_todo = models.Todo(title = result[0])
    db.add(new_todo)   
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/update/{todo_id}")
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
