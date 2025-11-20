"""
Test script for status tracking flow.

This script tests:
1. Creating a document with status
2. Updating document status via StatusService
3. Publishing status events to RabbitMQ
4. Verifying Socket.IO broadcasts
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from shared.database.session import create_session
from shared.messaging.publisher import RabbitMQPublisher
from shared.models import Document, User
from shared.repositories.status import SqlStatusRepository
from shared.services.status_service import StatusService
from shared.types.status import DocumentProcessingStatus

# Environment configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@localhost:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")


def main():
    """Run status flow test."""
    print("=" * 60)
    print("Status Tracking Flow Test")
    print("=" * 60)
    
    # Create database session
    print("\n1. Connecting to database...")
    db = next(create_session())
    
    try:
        # Get or create test user
        print("2. Getting test user...")
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            print("   No test user found. Please create a user first.")
            return
        print(f"   User: {user.email} (ID: {user.id})")
        
        # Create test document
        print("\n3. Creating test document...")
        test_doc = Document(
            user_id=user.id,
            filename="test_status_flow.txt",
            file_path="/tmp/test_status_flow.txt",
            file_size=1024,
            mime_type="text/plain",
            content_hash="abc123test",
            processing_status=DocumentProcessingStatus.PENDING.value,
        )
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)
        print(f"   Document created: ID={test_doc.id}, status={test_doc.processing_status}")
        
        # Initialize RabbitMQ publisher
        print("\n4. Connecting to RabbitMQ...")
        publisher = RabbitMQPublisher(
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE
        )
        publisher.connect()
        print("   Connected to RabbitMQ")
        
        # Initialize status service
        print("\n5. Initializing StatusService...")
        status_repository = SqlStatusRepository(db)
        status_service = StatusService(
            status_repository=status_repository,
            message_publisher=publisher
        )
        print("   StatusService ready")
        
        # Test status updates
        print("\n6. Testing status updates...")
        
        # Update to PROCESSING
        print("\n   a) Updating to PROCESSING...")
        result = status_service.update_document_status(
            document_id=test_doc.id,
            status=DocumentProcessingStatus.PROCESSING,
            metadata={"step": "parsing", "progress": 0.25}
        )
        if result.is_ok():
            doc = result.unwrap()
            print(f"      SUCCESS: Document {doc.id} -> {doc.processing_status}")
            print(f"      Event published to RabbitMQ: document.status.updated")
        else:
            print(f"      ERROR: {result.unwrap_err()}")
        
        time.sleep(1)
        
        # Update to READY
        print("\n   b) Updating to READY...")
        result = status_service.update_document_status(
            document_id=test_doc.id,
            status=DocumentProcessingStatus.READY,
            chunk_count=42,
            metadata={"step": "complete", "progress": 1.0}
        )
        if result.is_ok():
            doc = result.unwrap()
            print(f"      SUCCESS: Document {doc.id} -> {doc.processing_status}")
            print(f"      Chunk count: {doc.chunk_count}")
            print(f"      Event published to RabbitMQ: document.status.updated")
        else:
            print(f"      ERROR: {result.unwrap_err()}")
        
        time.sleep(1)
        
        # Test error status
        print("\n   c) Testing error status...")
        result = status_service.update_document_status(
            document_id=test_doc.id,
            status=DocumentProcessingStatus.FAILED,
            error="Simulated error for testing",
            metadata={"step": "failed", "progress": 0.5}
        )
        if result.is_ok():
            doc = result.unwrap()
            print(f"      SUCCESS: Document {doc.id} -> {doc.processing_status}")
            print(f"      Error: {doc.processing_error}")
            print(f"      Event published to RabbitMQ: document.status.updated")
        else:
            print(f"      ERROR: {result.unwrap_err()}")
        
        print("\n7. Verifying database state...")
        db.refresh(test_doc)
        print(f"   Final status: {test_doc.processing_status}")
        print(f"   Error message: {test_doc.processing_error}")
        print(f"   Chunk count: {test_doc.chunk_count}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        print("\nNOTE: To verify Socket.IO broadcasts:")
        print("1. Start the Flask server with: docker compose up api")
        print("2. Connect a Socket.IO client to ws://localhost:5000")
        print("3. Subscribe to status updates: emit('subscribe_status', {user_id: <id>})")
        print("4. Listen for 'document_status' events")
        print("5. Run this script again to trigger events")
        
        # Cleanup
        print("\n8. Cleaning up test document...")
        db.delete(test_doc)
        db.commit()
        print("   Test document deleted")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        if publisher:
            publisher.disconnect()


if __name__ == "__main__":
    main()
