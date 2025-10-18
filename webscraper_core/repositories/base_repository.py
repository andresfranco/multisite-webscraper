from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository for SQLAlchemy ORM models.

    Usage:
      # If you have an existing Session:
      repo = BaseRepository(session=existing_session)

      # Or with a sessionmaker factory:
      SessionLocal = sessionmaker(bind=engine)
      repo = BaseRepository(session_factory=SessionLocal)

      users = repo.fetch_all(User)                      # List[User]
      user = repo.fetch_by_id(User, 1)                  # Optional[User]
      posts = repo.fetch_by_criteria(Post, {"author_id": 3})
      repo.close()
    """

    def __init__(self,
                 session: Optional[Session] = None,
                 model: Optional[Type[T]] = None,
                 session_factory: Optional[Callable[[], Session]] = None):
        if session is None and session_factory is None:
            raise ValueError("Either session or session_factory must be provided")
        self._session = session
        self._session_factory = session_factory
        self.model = model

    @property
    def session(self) -> Session:
        """Get the current session, creating one if necessary."""
        return self._get_session()

    def _get_session(self) -> Session:
        if self._session is None:
            # session_factory is a sessionmaker or any callable returning Session
            self._session = self._session_factory()  # type: ignore[operator]
        return self._session

    def _validate_model(self, model: Type[T]) -> None:
        # Basic validation: must be a SQLAlchemy declarative model (have __table__)
        if not hasattr(model, "__table__"):
            raise ValueError(f"Invalid SQLAlchemy model: {model!r}")

    def fetch_all(self, model: Type[T]) -> List[T]:
        """Return all rows as mapped model instances."""
        self._validate_model(model)
        session = self._get_session()
        try:
            return session.query(model).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error when querying model '{model.__name__}': {e}")

    def fetch_by_id(self, model: Type[T], record_id: Any) -> Optional[T]:
        """Return a single mapped instance by primary key (or None). Uses Session.get()."""
        self._validate_model(model)
        session = self._get_session()
        try:
            # Session.get works with single- or composite- primary keys (for composite, pass tuple)
            return session.get(model, record_id)
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error when getting '{model.__name__}' id={record_id}: {e}")

    def fetch_by_criteria(self, model: Type[T], criteria: Dict[str, Any]) -> List[T]:
        """
        Return rows that match all column=value pairs in criteria.
        If criteria is empty, returns all rows.
        """
        self._validate_model(model)
        if not criteria:
            return self.fetch_all(model)

        # Validate column names against model's table columns to reduce injection surface
        allowed_cols = {c.name for c in model.__table__.columns}
        for col in criteria.keys():
            if col not in allowed_cols:
                raise ValueError(f"Invalid column name for model {model.__name__}: {col}")

        session = self._get_session()
        try:
            return session.query(model).filter_by(**criteria).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error when querying model '{model.__name__}': {e}")

    def close(self) -> None:
        """Close the underlying SQLAlchemy Session (if present)."""
        if self._session is not None:
            try:
                self._session.close()
            finally:
                self._session = None