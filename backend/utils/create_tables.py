import backend.models.dictionary
import backend.models.user
import backend.models.user_word

from backend.database import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Tables created")