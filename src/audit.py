"""Audit logging with privacy controls and tamper-evidence."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import hashlib
from pathlib import Path

from src.models import AuditEvent


class AuditLogger:
    """
    Append-only audit log with privacy controls and tamper-evident chain.
    Provides full traceability of all system decisions and actions.
    """
    
    def __init__(self, user_id: str, log_dir: Optional[str] = None):
        self.user_id = user_id
        
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path("audit_logs") / user_id
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file path
        self.log_file = self.log_dir / "audit.jsonl"
        
        # In-memory cache
        self.event_cache: List[AuditEvent] = []
        
        # Chain state for tamper-evidence
        self.chain_state = {
            "last_hash": self._compute_genesis_hash(),
            "event_count": 0
        }
        
        # Load existing logs if any
        self._load_existing_logs()
    
    def log_event(
        self,
        event_type: str,
        entity_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        privacy_level: str = "private"
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (plan, task, action, approval, etc.)
            entity_id: ID of the entity being audited
            action: Action performed
            details: Additional details
            privacy_level: "private", "shared", or "public"
        
        Returns:
            Created AuditEvent
        """
        event = AuditEvent(
            user_id=self.user_id,
            event_type=event_type,
            entity_id=entity_id,
            action=action,
            details=details or {},
            privacy_level=privacy_level
        )
        
        # Compute hash linking to previous event (blockchain-style)
        event_data = self._serialize_event(event)
        current_hash = self._compute_hash(
            self.chain_state["last_hash"] + event_data
        )
        
        # Add hash to event details
        event.details["_chain_hash"] = current_hash
        event.details["_prev_hash"] = self.chain_state["last_hash"]
        event.details["_sequence"] = self.chain_state["event_count"]
        
        # Update chain state
        self.chain_state["last_hash"] = current_hash
        self.chain_state["event_count"] += 1
        
        # Append to log
        self._append_to_log(event)
        
        # Add to cache
        self.event_cache.append(event)
        
        return event
    
    def query_events(
        self,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        privacy_level: Optional[str] = None
    ) -> List[AuditEvent]:
        """
        Query audit events with filters.
        
        Args:
            event_type: Filter by event type
            entity_id: Filter by entity ID
            start_time: Filter events after this time
            end_time: Filter events before this time
            privacy_level: Filter by privacy level
        
        Returns:
            List of matching AuditEvents
        """
        results = []
        
        for event in self.event_cache:
            # Apply filters
            if event_type and event.event_type != event_type:
                continue
            
            if entity_id and event.entity_id != entity_id:
                continue
            
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            if privacy_level and event.privacy_level != privacy_level:
                continue
            
            results.append(event)
        
        return results
    
    def get_event_chain(self, entity_id: str) -> List[AuditEvent]:
        """
        Get full audit chain for a specific entity.
        
        Args:
            entity_id: The entity to trace
        
        Returns:
            Chronological list of all events for this entity
        """
        events = self.query_events(entity_id=entity_id)
        events.sort(key=lambda e: e.timestamp)
        return events
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the audit chain.
        
        Returns:
            Verification result with status and details
        """
        result = {
            "valid": True,
            "total_events": len(self.event_cache),
            "verified_at": datetime.now().isoformat(),
            "errors": []
        }
        
        # Re-compute hashes and verify chain
        expected_hash = self._compute_genesis_hash()
        
        for i, event in enumerate(self.event_cache):
            prev_hash = event.details.get("_prev_hash")
            event_hash = event.details.get("_chain_hash")
            sequence = event.details.get("_sequence")
            
            # Verify previous hash matches
            if prev_hash != expected_hash:
                result["valid"] = False
                result["errors"].append({
                    "event_id": event.id,
                    "sequence": i,
                    "error": "Hash chain broken",
                    "expected_prev": expected_hash,
                    "actual_prev": prev_hash
                })
            
            # Verify sequence
            if sequence != i:
                result["valid"] = False
                result["errors"].append({
                    "event_id": event.id,
                    "error": "Sequence mismatch",
                    "expected": i,
                    "actual": sequence
                })
            
            # Compute expected hash for this event
            event_data = self._serialize_event(event, include_hash=False)
            expected_hash = self._compute_hash(prev_hash + event_data)
            
            if event_hash != expected_hash:
                result["valid"] = False
                result["errors"].append({
                    "event_id": event.id,
                    "sequence": i,
                    "error": "Event hash mismatch",
                    "expected": expected_hash,
                    "actual": event_hash
                })
            else:
                expected_hash = event_hash
        
        return result
    
    def export_audit_trail(
        self,
        entity_id: Optional[str] = None,
        include_private: bool = True
    ) -> Dict[str, Any]:
        """
        Export audit trail for external review or archival.
        
        Args:
            entity_id: Optional filter for specific entity
            include_private: Whether to include private events
        
        Returns:
            Exportable audit trail data
        """
        if entity_id:
            events = self.get_event_chain(entity_id)
        else:
            events = self.event_cache
        
        # Filter by privacy if needed
        if not include_private:
            events = [e for e in events if e.privacy_level != "private"]
        
        return {
            "user_id": self.user_id,
            "exported_at": datetime.now().isoformat(),
            "total_events": len(events),
            "chain_integrity": self.verify_chain_integrity(),
            "events": [
                {
                    "id": e.id,
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "entity_id": e.entity_id,
                    "action": e.action,
                    "details": {
                        k: v for k, v in e.details.items()
                        if not k.startswith("_")  # Exclude internal chain data
                    } if not include_private else e.details,
                    "privacy_level": e.privacy_level
                }
                for e in events
            ]
        }
    
    def _serialize_event(
        self,
        event: AuditEvent,
        include_hash: bool = False
    ) -> str:
        """Serialize event for hashing."""
        data = {
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "event_type": event.event_type,
            "entity_id": event.entity_id,
            "action": event.action,
            "privacy_level": event.privacy_level
        }
        
        # Add non-hash details
        for k, v in event.details.items():
            if include_hash or not k.startswith("_"):
                data[k] = v
        
        return json.dumps(data, sort_keys=True)
    
    def _compute_hash(self, data: str) -> str:
        """Compute SHA256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _compute_genesis_hash(self) -> str:
        """Compute hash for genesis event."""
        genesis_data = f"genesis_{self.user_id}"
        return self._compute_hash(genesis_data)
    
    def _append_to_log(self, event: AuditEvent) -> None:
        """Append event to persistent log file."""
        with open(self.log_file, "a") as f:
            event_json = json.dumps({
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id,
                "event_type": event.event_type,
                "entity_id": event.entity_id,
                "action": event.action,
                "details": event.details,
                "privacy_level": event.privacy_level
            })
            f.write(event_json + "\n")
    
    def _load_existing_logs(self) -> None:
        """Load existing logs from file."""
        if not self.log_file.exists():
            return
        
        with open(self.log_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                event = AuditEvent(
                    id=data["id"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    user_id=data["user_id"],
                    event_type=data["event_type"],
                    entity_id=data["entity_id"],
                    action=data["action"],
                    details=data["details"],
                    privacy_level=data["privacy_level"]
                )
                
                self.event_cache.append(event)
                
                # Update chain state
                if "_chain_hash" in event.details:
                    self.chain_state["last_hash"] = event.details["_chain_hash"]
                if "_sequence" in event.details:
                    self.chain_state["event_count"] = event.details["_sequence"] + 1
