from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import re

from ocr import extract_text
from validator import validate_record
from database import SessionLocal, LandRecord


app = FastAPI(
    title="Land Record AI",
    description="Intelligent Land Record Digitization and Validation System",
    version="1.0"
)


# =========================================
# CORS
# =========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"]

)


# =========================================
# HOME
# =========================================

@app.get("/")
def home():

    return {

        "message":
        "Land Record Digitization System is running!"

    }


# =========================================
# STRUCTURED DATA EXTRACTION
# =========================================

def extract_record(text):


    # -------------------------------------
    # SURVEY NUMBER
    # -------------------------------------

    survey_match = re.search(

        r"(?:Survey\s*(?:No\.?|Number)|सर्वे\s*(?:नं\.?|क्रमांक))"
        r"\s*[:\-]?\s*([A-Za-z0-9\/\-]+)",

        text,

        re.IGNORECASE

    )


    # -------------------------------------
    # OWNER NAME
    # -------------------------------------

    owner_match = re.search(

        r"(?:Owner\s*Name|Owner|Name\s*of\s*Owner|"
        r"मालकाचे\s*नाव|मालकाचे नाव)"
        r"\s*[:\-]?\s*([A-Za-z .]+)",

        text,

        re.IGNORECASE

    )


    # -------------------------------------
    # LAND AREA
    # -------------------------------------

    area_match = re.search(

        r"(?:Land\s*Area|Area|Land\s*Size|क्षेत्र)"
        r"\s*[:\-]?\s*([0-9.]+\s*"
        r"(?:acre|acres|hectare|hectares|ha|sq\.?\s*ft)?)",

        text,

        re.IGNORECASE

    )


    # -------------------------------------
    # LOCATION
    # -------------------------------------

    location_match = re.search(

        r"(?:Location|Village|District|स्थान|गाव|जिल्हा)"
        r"\s*[:\-]?\s*([A-Za-z .]+)",

        text,

        re.IGNORECASE

    )


    return {

        "owner_name":
            owner_match.group(1).strip()
            if owner_match
            else "Not detected",


        "survey_number":
            survey_match.group(1).strip()
            if survey_match
            else "Not detected",


        "land_area":
            area_match.group(1).strip()
            if area_match
            else "Not detected",


        "location":
            location_match.group(1).strip()
            if location_match
            else "Not detected"

    }


# =========================================
# UPLOAD + OCR + VALIDATION
# =========================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    file_bytes = await file.read()


    # OCR

    text = extract_text(
        file_bytes,
        file.filename
    )


    # Extract structured fields

    record = extract_record(text)


    # Validate

    validation = validate_record(
        record
    )


    return {

        "filename": file.filename,

        "ocr_text": text,

        "record": record,

        "validation": validation

    }


# =========================================
# APPROVAL REQUEST
# =========================================

class ApprovalRequest(BaseModel):

    owner_name: str

    survey_number: str

    land_area: str

    location: str

    ocr_text: str = ""

    owner_confidence: float = 0.0

    survey_confidence: float = 0.0

    area_confidence: float = 0.0

    location_confidence: float = 0.0


# =========================================
# APPROVE + SAVE RECORD
# =========================================

@app.post("/approve")
def approve_record(
    record: ApprovalRequest
):

    db = SessionLocal()


    try:

        # Create database record

        new_record = LandRecord(

            owner_name=
                record.owner_name,

            survey_number=
                record.survey_number,

            land_area=
                record.land_area,

            location=
                record.location,

            ocr_text=
                record.ocr_text,

            owner_confidence=
                record.owner_confidence,

            survey_confidence=
                record.survey_confidence,

            area_confidence=
                record.area_confidence,

            location_confidence=
                record.location_confidence,

            status="Approved"

        )


        # Add record

        db.add(new_record)


        # Save

        db.commit()


        # Get generated ID

        db.refresh(new_record)


        return {

            "message":
                "Record approved and saved successfully!",

            "record_id":
                new_record.id,

            "status":
                new_record.status

        }


    finally:

        db.close()


# =========================================
# GET SAVED RECORDS
# =========================================

@app.get("/records")
def get_records():

    db = SessionLocal()


    try:

        records = (

            db.query(LandRecord)

            .order_by(
                LandRecord.id.desc()
            )

            .all()

        )


        return [

            {

                "id":
                    record.id,

                "owner_name":
                    record.owner_name,

                "survey_number":
                    record.survey_number,

                "land_area":
                    record.land_area,

                "location":
                    record.location,

                "status":
                    record.status,

                "created_at":
                    record.created_at

            }

            for record in records

        ]


    finally:

        db.close()