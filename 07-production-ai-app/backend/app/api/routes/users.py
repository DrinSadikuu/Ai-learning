from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)