from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv
import os
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

ARCHIVO_CSV = "registros.csv"
CARPETA_FOTOS = "fotos"
CARPETA_STATIC = "static"
CARPETA_TEMPLATES = "templates"

os.makedirs(CARPETA_FOTOS, exist_ok=True)
os.makedirs(CARPETA_STATIC, exist_ok=True)
os.makedirs(CARPETA_TEMPLATES, exist_ok=True)

app = FastAPI()
app.mount("/fotos", StaticFiles(directory=CARPETA_FOTOS), name="fotos")
app.mount("/static", StaticFiles(directory=CARPETA_STATIC), name="static")
templates = Jinja2Templates(directory=CARPETA_TEMPLATES)

# ---------- helpers ----------
def leer_registros():
    if not os.path.exists(ARCHIVO_CSV):
        return []
    with open(ARCHIVO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def escribir_todos(registros):
    fieldnames = ["id", "fecha", "categoria", "detalle", "foto"]
    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(registros)

async def guardar_registro_async(categoria: str, detalle: str, foto: UploadFile):
    path_foto = ""
    if foto and foto.filename:
        ext = os.path.splitext(foto.filename)[1]
        nombre_foto = f"{uuid.uuid4().hex}{ext}"
        ruta_disco = os.path.join(CARPETA_FOTOS, nombre_foto)
        contenido = await foto.read()
        with open(ruta_disco, "wb") as f:
            f.write(contenido)
        path_foto = f"/fotos/{nombre_foto}"

    nuevo = {
        "id": uuid.uuid4().hex,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "categoria": categoria,
        "detalle": detalle,
        "foto": path_foto
    }

    escribir_cabecera = not os.path.exists(ARCHIVO_CSV)
    fieldnames = ["id", "fecha", "categoria", "detalle", "foto"]
    with open(ARCHIVO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if escribir_cabecera:
            writer.writeheader()
        writer.writerow(nuevo)
    logging.info(f"Registro guardado: {nuevo['id']}")
    return nuevo["id"]

def eliminar_foto_si_existe(path_publico):
    if not path_publico:
        return
    nombre = os.path.basename(path_publico)
    ruta_disco = os.path.join(CARPETA_FOTOS, nombre)
    try:
        if os.path.exists(ruta_disco):
            os.remove(ruta_disco)
            logging.info(f"Foto eliminada: {ruta_disco}")
    except Exception as e:
        logging.warning(f"No se pudo eliminar la foto {ruta_disco}: {e}")

# ---------- rutas ----------
@app.get("/")
async def home(request: Request):
    registros = leer_registros()
    registros_mostrar = registros[-10:]
    return templates.TemplateResponse("index.html", {"request": request, "registros": registros_mostrar})

@app.post("/agregar")
async def agregar(categoria: str = Form(...), detalle: str = Form(...), foto: UploadFile = File(None)):
    await guardar_registro_async(categoria, detalle, foto)
    return RedirectResponse(url="/", status_code=303)

@app.post("/borrar")
async def borrar(id: str = Form(...)):
    registros = leer_registros()
    encontrado = None
    for r in registros:
        if r.get("id") == id:
            encontrado = r
            break
    if encontrado:
        eliminar_foto_si_existe(encontrado.get("foto", ""))
        registros = [r for r in registros if r.get("id") != id]
        escribir_todos(registros)
        logging.info(f"Registro borrado: {id}")
    else:
        logging.warning(f"No se encontró registro con id {id}")
    return RedirectResponse(url="/", status_code=303)

# ---------- Run si es local ----------
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
