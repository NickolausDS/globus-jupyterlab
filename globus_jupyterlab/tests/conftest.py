import pathlib
import pytest
import copy
from unittest.mock import Mock
import globus_sdk
from globus_sdk.tokenstorage import SimpleJSONFileAdapter
import base64
import pickle
import tornado.web

from globus_jupyterlab.handlers import get_handlers, HANDLER_MODULES
from globus_jupyterlab.handlers.base import BaseAPIHandler
from globus_jupyterlab.tests.mocks import MockGlobusAPIError, MOCK_TOKENS
from globus_jupyterlab.login_manager import LoginManager
from globus_jupyterlab.globus_config import GlobusConfig


@pytest.fixture
def app(token_storage, monkeypatch):
    monkeypatch.setattr(
        BaseAPIHandler.login_manager, "storage", token_storage("filename")
    )
    application = tornado.web.Application(get_handlers(HANDLER_MODULES, "/", ""))
    return application


@pytest.fixture
def logged_in(token_storage) -> SimpleJSONFileAdapter:
    """Simulate a logged in Globus application"""
    token_storage.tokens = copy.deepcopy(MOCK_TOKENS)
    return token_storage


@pytest.fixture
def login_expired(logged_in) -> SimpleJSONFileAdapter:
    for token_data in logged_in.tokens.values():
        token_data["expires_at_seconds"] = 0
    return logged_in


@pytest.fixture
def login_refresh(logged_in) -> SimpleJSONFileAdapter:
    for token_data in logged_in.tokens.values():
        token_data["refresh_token"] = "mock_refresh_token"
    return logged_in


@pytest.fixture
def logged_out(token_storage) -> SimpleJSONFileAdapter:
    token_storage.tokens = {}
    return token_storage


@pytest.fixture
def gcp(monkeypatch) -> globus_sdk.LocalGlobusConnectPersonal:
    """Mock GCP, return the class instance"""
    # Set instance vars to return some mock values
    monkeypatch.setattr(globus_sdk, "LocalGlobusConnectPersonal", Mock())
    return globus_sdk.LocalGlobusConnectPersonal.return_value


@pytest.fixture
def sdk_error(monkeypatch) -> globus_sdk.GlobusAPIError:
    monkeypatch.setattr(globus_sdk, "GlobusAPIError", MockGlobusAPIError)
    return globus_sdk.GlobusAPIError


@pytest.fixture
def transfer_client(monkeypatch) -> globus_sdk.TransferClient:
    """Mock the tranfer client, return the class instance"""
    monkeypatch.setattr(globus_sdk, "TransferClient", Mock())
    return globus_sdk.TransferClient.return_value


@pytest.fixture
def oauthenticator(monkeypatch) -> dict:
    data = {"client_id": "client_uuid", "tokens": dict()}
    encoded_data = base64.b64encode(pickle.dumps(data))
    monkeypatch.setenv("GLOBUS_DATA", str(encoded_data))
    return data


@pytest.fixture()
def token_storage(monkeypatch) -> SimpleJSONFileAdapter:
    class MockStorage:
        tokens = {}

        def __init__(self, filename):
            pass

        def get_by_resource_server(self):
            return self.tokens

        def get_token_data(self, resource_server):
            return self.get_by_resource_server()[resource_server]

        def clear_tokens(self):
            MockStorage.tokens = {}

        on_refresh = Mock()
        store = Mock()

    storage = MockStorage
    monkeypatch.setattr(LoginManager, "storage_class", MockStorage)
    monkeypatch.setattr(pathlib.Path, "unlink", MockStorage.clear_tokens)
    return storage
