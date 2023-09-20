"""Test batches."""

from datetime import date

from e_commerce_ddd.domain.model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    """Test allocating to a batch reduces the available quantity."""

    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18
