"""Pytest-codspeed adapter for macro scenarios.

Lives alongside ``scenarios/micro.py`` and is excluded from default
pytest discovery (see ``conftest.py:collect_ignore``). Only invoked
explicitly: by the CodSpeed CI workflow (``.github/workflows/codspeed.yml``)
which passes this path to pytest with ``--codspeed``. The perf framework's
own harness (``python -m py4j.tests.perf``) has its own macro runner and
doesn't use this file.

Each parametrized entry becomes a separately tracked CodSpeed benchmark
on the dashboard, so regressions show up per-scenario rather than as one
opaque aggregate.

Scenario coverage rationale: four macros covering the perf
characteristics most prone to regression on the py4j socket / call path:

* ``X1-1``  — single-thread concurrent_1_thread (10k sequential calls).
              Baseline round-trip latency floor.
* ``X2-10k`` — iterate_javalist_10k. The canonical "N round-trips"
              anti-pattern; targets of the JavaIterator / bulk-fetch
              optimization area.
* ``X4``    — callback_sort_100_items. Java->Python callback hot path;
              the most complex code path in py4j.
* ``X6``    — pool_saturation_50_threads. Connection pool behavior
              under high concurrency, tail-latency sensitive.

Adding more scenarios later is one parametrize entry per scenario.
"""

import pytest

from py4j.tests.perf.jvm import (
    JvmNotBuiltError,
    JvmStartupError,
    fresh_jvm,
)
from py4j.tests.perf.scenarios.macro import (
    X1_1Thread,
    X2_10k,
    X4_Callbacks,
    X6_PoolSaturation,
    X7_16k,
    X8_16k,
)


# X7-16k exercises the bytes-decoding recv path (decode_bytearray);
# X8-16k exercises the bytes-encoding send path. Together they cover
# both halves of the byte-codec / Nagle-sensitive bandwidth surface
# in CodSpeed CI. Without either, byte-codec optimizations are
# invisible to the per-PR dashboard — every prior macro returns
# int / list / void / callback and the byte path was a measurement
# blind spot.
_MACRO_SCENARIOS = [
    X1_1Thread, X2_10k, X4_Callbacks, X6_PoolSaturation,
    X7_16k, X8_16k,
]


@pytest.fixture(scope="function")
def macro_gateway(request):
    """Fresh JVM per macro scenario, with the callback server enabled
    when the scenario class declares ``enable_callbacks = True``.

    Yields ``(gateway, scenario_cls)`` so the test function can both
    drive the JVM and re-instantiate the scenario for setup + measure.
    """
    scenario_cls = request.param
    enable_callbacks = getattr(scenario_cls, "enable_callbacks", False)
    try:
        with fresh_jvm(enable_callbacks=enable_callbacks) as gw:
            yield gw, scenario_cls
    except JvmNotBuiltError as e:
        pytest.skip(str(e))
    except JvmStartupError as e:
        pytest.skip(str(e))


@pytest.mark.parametrize(
    "macro_gateway", _MACRO_SCENARIOS, indirect=True,
    ids=[cls.id for cls in _MACRO_SCENARIOS],
)
def test_macro_scenario(benchmark, macro_gateway):
    """Run one macro scenario through the benchmark fixture.

    pytest-codspeed (and pytest-benchmark) both honor the ``benchmark``
    fixture and handle iteration scaling automatically. Each
    ``measure()`` call is an expensive macro operation (thousands of
    calls or large-list iteration) so per-iteration measurement is
    appropriate.
    """
    gateway, scenario_cls = macro_gateway
    scenario = scenario_cls()
    if hasattr(scenario, "setup"):
        scenario.setup(gateway)
    benchmark(scenario.measure, gateway)
