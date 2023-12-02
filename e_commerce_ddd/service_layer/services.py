"""Service layer."""

from sqlalchemy.orm import Session

from e_commerce_ddd.adapters.repository import AbstractRepository
from e_commerce_ddd.domain import model


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]):
    return sku in {b.sku for b in batches}


def allocate(
    line: model.OrderLine,
    repo: AbstractRepository,
    session: Session,
) -> str:
    batches = repo.list()

    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")

    batchref = model.allocate(line, batches)

    session.commit()
    return batchref
