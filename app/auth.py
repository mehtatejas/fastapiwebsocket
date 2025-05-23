from fastapi import HTTPException, status

async def verify_token(token: str):
    if not token or "invalid" in token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"user": "demo-user"}
