from fastapi import  status, HTTPException, APIRouter, Depends
from sqlmodel import Session

from google import genai
from google.genai import types

from pydantic import BaseModel, Field

from ..database import get_db
from ..auth.views import get_current_user
from ..models import User


router = APIRouter(prefix="/main", tags=["Main App"])

class db_input(BaseModel):
    api_key: str
    user_language: str

class user_input(BaseModel):
    model: str
    input_topic: str
    input_essay: str

class user_info(BaseModel):
    user_email: str
    api_key: str | None
    language: str

class requirements(BaseModel):
    score: float = Field(description="The overall score of the essay")
    TR_score : float = Field(description="The score of TR part")
    LR_score : float = Field(description="The score of LR part")
    CC_score : float = Field(description="The score of CC part")
    GRA_score : float = Field(description="The score of GRA part")
    reason : str = Field(description="Point out the reasons for the score")
    improvement : str = Field(description="Point out directions for improvement.")

@router.post('/user/storage/', status_code=200)
async def api_storage(input_data: db_input, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.api_key = input_data.api_key
    current_user.language = input_data.user_language
    db.add(current_user)

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error has occured")
    return current_user

async def handle_input(GEMINI_API_KEY: str, model: str, topic: str, essay: str, language: str):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
        media_resolution="MEDIA_RESOLUTION_MEDIUM",
        response_mime_type="application/json",
        response_schema=requirements,
        system_instruction=f"""You are an IELTS examiner. I will submit my essay, and you will give it a score and briefly point out any issues.You should use {language} to respond"""
        ),

        input = f"""Topic: {topic}. Essay: {essay}"""

        response = client.models.generate_content(
        model=model, 
        contents=input,
        config=generate_content_config,
        )

        if response.text:
            parsed_response = requirements.model_validate_json(response.text)
            output = {
                "Overall_score": parsed_response.score,
                "TR": parsed_response.TR_score,
                "LR": parsed_response.LR_score,
                "CC": parsed_response.CC_score,
                "GRA": parsed_response.GRA_score,
                "reason": parsed_response.reason,
                "improvement": parsed_response.improvement
                },
        
            return output
        else:
            print(response)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model error")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error occured")

@router.post('/response/')
async def handle_response(input_data: user_input, db: User = Depends(get_current_user)):
    api_key = db.api_key
    language = db.language
    model = input_data.model
    topic = input_data.input_topic
    essay = input_data.input_essay

    output = await handle_input(api_key=api_key, language=language, model=model, topic=topic, essay=essay)
    if not output:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No score generated")
    
    return output

@router.get('/user/info/')
async def get_user_info(current_user: User = Depends(get_current_user)):
    """
    Fetches the current user's email and saved API key.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    return user_info(user_email=current_user.email, api_key=current_user.email, language=current_user.language)

@router.delete('/user/delete')
async def delete_user_account(db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    db.delete(current_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Some error occured when deleting the user, detail: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")
    return
