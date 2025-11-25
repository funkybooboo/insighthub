
import pytest
from unittest.mock import MagicMock, patch

from src.main import ProvisionerWorker

@pytest.fixture
def provisioner_worker():
    with patch('src.main.get_db_connection'), \
         patch('src.main.VectorStoreProvisioner'), \
         patch('src.main.GraphStoreProvisioner'):
        worker = ProvisionerWorker()
        worker.connection = MagicMock()
        worker.vector_provisioner = MagicMock()
        worker.graph_provisioner = MagicMock()
        worker.publish_event = MagicMock()
        yield worker

def test_process_event_success(provisioner_worker: ProvisionerWorker, mocker):
    """
    Test that the provisioner worker processes a workspace.provision_requested event successfully.
    """
    # Arrange
    mocker.patch.object(provisioner_worker, '_update_workspace_status')
    mocker.patch.object(provisioner_worker, '_update_workspace_resources')
    mocker.patch.object(provisioner_worker, '_publish_status_event')

    event_data = {
        "workspace_id": "ws1",
        "user_id": "user1",
        "rag_config": {"retriever_type": "vector"}
    }
    
    provisioner_worker.vector_provisioner.provision_workspace_collection.return_value = "test_collection"

    # Act
    provisioner_worker.process_event(event_data)

    # Assert
    provisioner_worker.vector_provisioner.provision_workspace_collection.assert_called_once_with("ws1", {"retriever_type": "vector"})
    provisioner_worker._update_workspace_status.assert_any_call("ws1", "provisioning", "Initializing workspace resources...")
    provisioner_worker._update_workspace_resources.assert_called_once_with("ws1", "test_collection", None)
    provisioner_worker._update_workspace_status.assert_any_call("ws1", "ready", "Workspace provisioning completed")
    assert provisioner_worker._publish_status_event.call_count == 2
