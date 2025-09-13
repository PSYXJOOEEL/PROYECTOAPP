from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from datetime import datetime
import os, uuid
from database import init_db, ejecutar, consultar

app = FastAPI()
init_db()

# Carpeta para fotos
os.makedirs("fotos", exist_ok=True)
app.mount("/fotos", StaticFiles(directory="fotos"), name="fotos")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    registros = consultar("SELECT id, fecha, categoria, detalle, foto FROM registros ORDER BY fecha DESC")
    return templates.TemplateResponse("index.html", {"request": request, "registros": registros})

@app.post("/agregar")
async def agregar(categoria: str = Form(...), detalle: str = Form(...), foto: UploadFile = File(None)):
    id_reg = str(uuid.uuid4())
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ruta_foto = ""
    if foto:
        nombre_foto = f"{id_reg}_{foto.filename}"
        ruta_foto = f"fotos/{nombre_foto}"
        with open(ruta_foto, "wb") as f:
            f.write(await foto.read())
    ejecutar("INSERT INTO registros (id, fecha, categoria, detalle, foto) VALUES (?, ?, ?, ?, ?)",
             (id_reg, fecha, categoria, detalle, ruta_foto))
    return RedirectResponse("/", status_code=303)

@app.post("/borrar")
def borrar(id: str = Form(...)):
    ejecutar("DELETE FROM registros WHERE id = ?", (id,))
    return RedirectResponse("/", status_code=303)
