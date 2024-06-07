import sys
import os

# 현재 디렉토리의 부모 디렉토리를 프로젝트 루트로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


import pytest


# def pytest_configure(config):
#     os.environ["PYTEST"] = "True"


@pytest.fixture(scope="session")
def test_client():

    from app import create_app

    application = create_app(test=True)
    test_client = application.test_client()

    return test_client
