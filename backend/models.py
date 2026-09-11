from datetime import datetime, timezone

from sqlalchemy import DateTime, String, UniqueConstraint, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DictionarySource(Base):
    __tablename__ = "dictionary_sources"

    __table_args__ = (UniqueConstraint("name","version",name="uq_dictionary_source_name_version",),)
    

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100),
                                      nullable=False)
    
    version: Mapped[str] = mapped_column(String(50),
                                         nullable=False)
    
    license_name: Mapped[str] = mapped_column(String(100),
                                         nullable=False)
    
    license_url: Mapped[str] = mapped_column(String(500),
                                         nullable=False)
    
    source_url: Mapped[str] = mapped_column(String(500),
                                            nullable=False)

    content_sha256: Mapped[str] = mapped_column(String(64),
                                            nullable=False)

    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  default=utc_now,
                                                  nullable=False)
    
class Lexeme(Base):
    __tablename__ = "lexemes"

    __table_args__ = (UniqueConstraint("source_id","normalized_lemma","part_of_speech",
                                       name="uq_lexeme_source_lemma_pos",),)

    id: Mapped[int] = mapped_column(primary_key=True)

    source_id: Mapped[int] = mapped_column(ForeignKey("dictionary_sources.id",ondelete="CASCADE"),
                                           nullable=False)
    
    lemma: Mapped[str] = mapped_column(String(255),
                                       nullable=False)
    
    normalized_lemma: Mapped[str] = mapped_column(String(255),
                                                  index=True,
                                                  nullable=False)
    
    part_of_speech: Mapped[str] = mapped_column(String(30),
                                                default="unknown",
                                                nullable=False)
    
class SourceSense(Base):
    __tablename__ = "source_senses"

    __table_args__ = (
        UniqueConstraint(
            "lexeme_id",
            "source_order",
            name="uq_source_sense_lexeme_order",
        ),
        CheckConstraint(
            "verification_status IN "
            "('imported', 'verified', 'needs_review', 'rejected')",
            name="ck_source_sense_verification_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    lexeme_id: Mapped[int] = mapped_column(ForeignKey("lexemes.id", ondelete="CASCADE"),
                                           nullable=False)
    
    source_order: Mapped[int] = mapped_column(nullable=False)

    verification_status: Mapped[str] = mapped_column(String(30),
                                                     default="imported",
                                                     nullable=False,)
    
class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(primary_key=True)

    sense_id: Mapped[int] = mapped_column(
        ForeignKey("source_senses.id", ondelete="CASCADE"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="ru",
        nullable=False,
    )

    source_order: Mapped[int] = mapped_column(
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    normalized_text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        default="imported",
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "sense_id",
            "language",
            "normalized_text",
            name="uq_translation_sense_language_text",
        ),
        UniqueConstraint(
            "sense_id",
            "language",
            "source_order",
            name="uq_translation_sense_language_order",
        ),
        CheckConstraint(
            "verification_status IN "
            "('imported', 'verified', 'needs_review', 'rejected')",
            name="ck_translation_verification_status",
        ),
    )

class Definition(Base):
    __tablename__ = "definitions"

    id: Mapped[int] = mapped_column(primary_key=True)

    sense_id: Mapped[int] = mapped_column(
        ForeignKey("source_senses.id", ondelete="CASCADE"),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )

    source_order: Mapped[int] = mapped_column(
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    text_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        default="imported",
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "sense_id",
            "language",
            "text_sha256",
            name="uq_definition_sense_language_hash",
        ),
        UniqueConstraint(
            "sense_id",
            "language",
            "source_order",
            name="uq_definition_sense_language_order",
        ),
        CheckConstraint(
            "verification_status IN "
            "('imported', 'verified', 'needs_review', 'rejected')",
            name="ck_definition_verification_status",
        ),
    )

class Pronunciation(Base):
    __tablename__ = "pronunciations"

    id: Mapped[int] = mapped_column(primary_key=True)

    lexeme_id: Mapped[int] = mapped_column(
        ForeignKey("lexemes.id", ondelete="CASCADE"),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_order: Mapped[int] = mapped_column(
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "lexeme_id",
            "text",
            name="uq_pronunciation_lexeme_text",
        ),
        UniqueConstraint(
            "lexeme_id",
            "source_order",
            name="uq_pronunciation_lexeme_order",
        ),
    )