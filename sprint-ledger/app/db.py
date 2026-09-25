# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firestore database client and operations for Sprint Ledger.

IMPORTANT: The GCP project ID is hardcoded as a string because Agent Platform's
runtime returns the numeric project number for google.auth.default() and
GOOGLE_CLOUD_PROJECT, which causes Firestore (default) database lookups to fail.
"""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded project ID string as required for Agent Platform compatibility
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-1625fe9e416b"
HACKATHONS_COLLECTION = "hackathons"


def get_firestore_client() -> firestore.Client:
    """Returns an authenticated Firestore client using the hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_hackathons_from_db(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all tracked hackathons, optionally filtered by status."""
    db = get_firestore_client()
    query = db.collection(HACKATHONS_COLLECTION)
    if status:
        query = query.where("status", "==", status)
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_hackathon_from_db(hackathon_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single hackathon document by ID or name slug."""
    db = get_firestore_client()
    doc_ref = db.collection(HACKATHONS_COLLECTION).document(hackathon_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Fallback: search by name
    docs = (
        db.collection(HACKATHONS_COLLECTION)
        .where("name", "==", hackathon_id)
        .limit(1)
        .stream()
    )
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        return data
    return None


def save_hackathon_to_db(data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves or updates a hackathon document in Firestore."""
    db = get_firestore_client()
    hackathon_id = data.get("id")
    if not hackathon_id:
        name = data.get("name", "hackathon")
        hackathon_id = name.lower().replace(" ", "-").replace("/", "-")
        data["id"] = hackathon_id

    doc_ref = db.collection(HACKATHONS_COLLECTION).document(hackathon_id)
    doc_ref.set(data, merge=True)
    return data


def update_checklist_item_in_db(
    hackathon_id: str, item_index: int, done: bool
) -> Optional[Dict[str, Any]]:
    """Toggles or updates the done status of a checklist item by index."""
    db = get_firestore_client()
    doc_ref = db.collection(HACKATHONS_COLLECTION).document(hackathon_id)
    doc = doc_ref.get()
    if not doc.exists:
        # Check by name
        docs = (
            db.collection(HACKATHONS_COLLECTION)
            .where("name", "==", hackathon_id)
            .limit(1)
            .stream()
        )
        found_doc = None
        for d in docs:
            found_doc = d
            break
        if not found_doc:
            return None
        doc_ref = found_doc.reference
        data = found_doc.to_dict()
    else:
        data = doc.to_dict()

    checklist = data.get("checklist_items", [])
    if 0 <= item_index < len(checklist):
        checklist[item_index]["done"] = done
        doc_ref.update({"checklist_items": checklist})
        data["checklist_items"] = checklist
        data["id"] = doc_ref.id
        return data
    return None


def delete_hackathon_from_db(hackathon_id: str) -> bool:
    """Deletes a hackathon document from Firestore by ID or name slug."""
    db = get_firestore_client()
    doc_ref = db.collection(HACKATHONS_COLLECTION).document(hackathon_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return True

    # Fallback: search by name
    docs = (
        db.collection(HACKATHONS_COLLECTION)
        .where("name", "==", hackathon_id)
        .limit(1)
        .stream()
    )
    for d in docs:
        d.reference.delete()
        return True
    return False
