"""Flask app."""

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from e_commerce_ddd import config, orm, repository
from e_commerce_ddd.domain import model

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_url()))
app = Flask(__name__)


def is_valid_sku(sku: str, batches: model.Batch) -> bool:
    """Check whether sku is valid."""

    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"]
    )

    if not is_valid_sku(line.sku, batches):
        return {"message": f"Invalid sku {line.sku}"}, 400

    try:
        batch_ref = model.allocate(line, batches)
    except model.OutOfStock as e:
        return {"message": str(e)}, 400

    session.commit()
    return {"batch_ref": batch_ref}, 201
