import abc

from sqlalchemy import select
from sqlalchemy.orm import Session

from e_commerce_ddd.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, batch: model.Batch):
        self.session.add(batch)

    def get(self, reference) -> model.Batch:
        batch_select_stmt = select(model.Batch).where(
            model.Batch.reference == reference
        )
        query_result = self.session.execute(batch_select_stmt)
        return query_result.scalar_one()

    def list(self) -> list[model.Batch]:
        return self.session.execute(select(model.Batch))
