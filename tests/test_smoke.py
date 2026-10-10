import fleetguard


def test_package_exposes_version():
    assert fleetguard.__version__ == "0.1.0"
