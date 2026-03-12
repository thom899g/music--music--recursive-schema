"""
Firebase Manager - State management and event streaming
Handles all Firebase operations for the event-driven architecture
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, db as realtime_db
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages Firebase connections and operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.app = None
            self.db = None
            self.rtdb = None
    
    def initialize(self, credential_path: str = "firebase-creds.json") -> None:
        """Initialize Firebase with credentials"""
        if self.initialized:
            logger.warning("Firebase already initialized")
            return
            
        try:
            # Check if credential file exists
            if not os.path.exists(credential_path):
                raise FileNotFoundError(f"Firebase credentials not found at {credential_path}")
            
            # Initialize Firebase Admin
            cred = credentials.Certificate(credential_path)
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://recursive-schema-default-rtdb.firebaseio.com/'
            })
            
            # Initialize Firestore and Realtime Database
            self.db = firestore.client()
            self.rtdb = realtime_db.reference()
            
            self.initialized = True
            logger.info("Firebase initialized successfully")
            
        except FirebaseError as e:
            logger.error(f"Firebase initialization error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def save_manifest(self, manifest_data: Dict[str, Any], collection: str = "campaigns") -> str:
        """Save manifest to Firestore"""
        if not self.initialized:
            raise RuntimeError("Firebase not initialized")
        
        try:
            # Add timestamp
            manifest_data['firestore_updated'] = firestore.SERVER_TIMESTAMP
            
            # Save to Firestore
            doc_ref = self.db.collection(collection).document(manifest_data['campaign_id'])
            doc_ref.set(manifest_data)
            
            logger.info(f"Manifest saved to Firestore: {manifest_data['campaign_id']}")
            return doc_ref.id
            
        except FirebaseError as e:
            logger.error(f"Firestore save error: {e}")
            raise
    
    def update_manifest_status(self, campaign_id: str, status: str, collection: str = "campaigns") -> None:
        """Update manifest status in Firestore"""
        if not self.initialized:
            raise RuntimeError("Firebase not initialized")
        
        try:
            update_data = {
                'status': status,
                'last_status_update': firestore.SERVER_TIMESTAMP
            }
            
            self.db.collection(collection).document(campaign_id).update(update_data)
            logger.info(f"Manifest status updated: {campaign_id} -> {status}")
            
        except FirebaseError as e:
            logger.error(f"Firestore update error: {e}")
            raise
    
    def emit_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Emit event to Realtime Database"""
        if not self.initialized:
            raise RuntimeError("Firebase not initialized")
        
        try:
            event = {
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow().isoformat(),
                'processed': False
            }
            
            # Push to events collection
            event_ref = self.rtdb.child('events').push(event)
            logger.info(f"Event emitted: {event_type} -> {event_ref.key}")
            
        except FirebaseError as e:
            logger.error(f"Realtime Database error: {e}")
            raise
    
    def get_pending_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending events from Realtime Database"""
        if not self.initialized:
            raise RuntimeError("Firebase not initialized")
        
        try:
            events_ref = self.rtdb.child('events')
            query = events_ref.order_by_child('processed').equal_to(False).limit_to_first(limit)
            snapshot = query.get()
            
            events = []
            if snapshot:
                for key, value in snapshot.items():
                    event = value
                    event['id'] = key
                    events.append(event)
            
            return events
            
        except FirebaseError as e:
            logger.error(f"Error fetching events: {e}")
            return []
    
    def mark_event_processed(self, event_id: str) -> None:
        """Mark event as processed"""
        if not self.initialized:
            raise RuntimeError("Firebase not initialized")
        
        try:
            self.rtdb.child('events').child(event_id).update({'processed': True})
            logger.info(f"Event marked as processed: {event_id}")
            
        except FirebaseError as e:
            logger.error(f"Error marking event as processed: {e}")
            raise
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        if not self.initialized:
            return {'status': 'firebase_not_initialized'}
        
        try:
            health_ref = self.db.collection('system_health').document('current')
            doc = health_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return {'status': 'no_health_data'}
                
        except FirebaseError as e:
            logger.error(f"Error getting system health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup_old_events(self, days_old: int = 7) -> int:
        """Clean up old processed events"""
        if not self.initialized:
            return 0
        
        try:
            cutoff_date = datetime.utcnow().timestamp() - (days_old * 86400)
            events_ref = self.rtdb.child('events')
            snapshot = events_ref.get()
            
            deleted_count = 0
            if snapshot:
                for key, value in snapshot.items():
                    try:
                        event_time = datetime.fromisoformat(value['timestamp']).timestamp()
                        if value.get('processed') and event_time < cutoff_date:
                            events_ref.child(key).delete()
                            deleted_count += 1
                    except (KeyError, ValueError):
                        continue
            
            logger.info(f"Cleaned up {deleted_count} old events")
            return deleted_count
            
        except FirebaseError as e:
            logger.error(f"Error cleaning up events: {e}")
            return 0