import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import io

from patterns import analyze_chart_image

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Tredar Bigin - Screenshot Chart Analyzer")

# static आणि templates साठी absolute path
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_chart(request: Request, file: UploadFile = File(...)):
    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        result = {
            "error": "Image उघडता आला नाही. कृपया valid chart screenshot upload करा."
        }
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": result,
            },
        )

    analysis = analyze_chart_image(image)

    result = {
        "filename": file.filename,
        "trend": analysis["trend"],
        "action": analysis["action"],
        "confidence": analysis["confidence"],
        "reason": analysis["reason"],
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
