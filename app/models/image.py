from datetime import datetime,timezone
from sqlalchemy import String,Integer,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.core.database import Base

class Image(Base):
    __tablename__="image"
    id:Mapped[int]=mapped_column(
        primary_key=True,index=True
    )
    
    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    original_filename:Mapped[str]=mapped_column(
        String(255),
        unique=False,
        nullable=False
    )
    storage_key:Mapped[str]=mapped_column(
        String(500),
        nullable=False,
        index=True
    )
    
    mime_type:Mapped[str]=mapped_column(
        String(100),
        nullable=False
    )
    
    format: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
)

    user = relationship(
        "User",
        back_populates="images"
    )
    transformations=relationship(
        "ImageTransformation",
        back_populates="image",
        cascade="all,delete-orphan",
        lazy='selectin'
    )