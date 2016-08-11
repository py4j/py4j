from py4j import binary_protocol as bprotocol


def test_int_encoder():
    encoder = bprotocol.IntEncoder()
    value = "Hello"

    assert encoder.encode(value, type(value)) == bprotocol.CANNOT_ENCODE
