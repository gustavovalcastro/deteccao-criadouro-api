from .user import router as userRouter
from .userPortal import router as userPortalRouter
from .campaign import router as campaignRouter
from .result import router as resultRouter

routers = [
    userRouter,
    userPortalRouter,
    campaignRouter,
    resultRouter,
]
