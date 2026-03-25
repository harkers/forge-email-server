from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .repository import create_case, list_cases, get_case

app = FastAPI(title="Privacy Intake", version="0.1.0")
templates = Jinja2Templates(directory="app/templates")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "cases": list_cases()})

@app.get("/cases/new", response_class=HTMLResponse)
def new_case(request: Request):
    return templates.TemplateResponse("new_case.html", {"request": request})

@app.post("/cases")
def create_case_route(
    request_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    submitted_by: str = Form(...),
    urgency: str = Form("normal"),
    business_area: str = Form(""),
    controller_name: str = Form(""),
    client_name: str = Form(""),
    deadline_at: str = Form(""),
    confidentiality_level: str = Form("internal"),
    contains_phi: bool = Form(False),
    contains_special_category: bool = Form(False),
    international_transfer: bool = Form(False),
):
    payload = {
        "request_type": request_type,
        "title": title,
        "description": description,
        "submitted_by": submitted_by,
        "urgency": urgency,
        "business_area": business_area or None,
        "controller_name": controller_name or None,
        "client_name": client_name or None,
        "deadline_at": deadline_at or None,
        "confidentiality_level": confidentiality_level,
        "contains_phi": contains_phi,
        "contains_special_category": contains_special_category,
        "international_transfer": international_transfer,
        "metadata": {},
    }
    created = create_case(payload)
    return RedirectResponse(url=f"/cases/{created['id']}", status_code=303)

@app.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail(case_id: str, request: Request):
    data = get_case(case_id)
    return templates.TemplateResponse("case_detail.html", {"request": request, **data})

@app.get("/api/cases")
def api_cases():
    return JSONResponse(list_cases())
