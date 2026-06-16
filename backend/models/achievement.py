from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from database import Base

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    badge_id = Column(String(100), nullable=False)
    badge_name = Column(String(200), nullable=False)
    badge_description = Column(String(500), nullable=True)
    badge_icon = Column(String(10), nullable=True)
    category = Column(String(100), nullable=True)
    earned_at = Column(DateTime, server_default=func.now())
    xp_reward = Column(Integer, default=0)
