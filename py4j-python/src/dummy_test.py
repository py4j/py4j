from py4j.java_gateway import JavaGateway, CallbackServerParameters


class FalseAddition(object):
    def doOperation(self, i, j, k=None):
        if k is None:
            # Integer overflow!
            return 3722507311
        else:
            return 3722507311

    class Java:
        implements = ['py4j.examples.Operator']


if __name__ == "__main__":
    java_gateway = JavaGateway(CallbackServerParameters())
    operator = FalseAddition()
    print('Before the call')
    try:
        java_gateway.entry_point.randomTernaryOperator(operator)
    except Exception:
        pass
    print('After the call')
    java_gateway.shutdown()
    print('After shutdown')
