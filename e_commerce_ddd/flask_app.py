"""Flask app."""

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from e_commerce_ddd import config, orm, repository, services
from e_commerce_ddd.domain import model

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_url()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"]
    )

    try:
        batch_ref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batch_ref": batch_ref}, 201
