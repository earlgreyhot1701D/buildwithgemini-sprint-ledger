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

"""Seed script to populate Firestore with sample hackathons for Sprint Ledger.

IMPORTANT: Uses the hardcoded project ID string for compatibility with Agent Platform.
"""

from google.cloud import firestore

# Hardcoded project ID string as required
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-1625fe9e416b"
HACKATHONS_COLLECTION = "hackathons"

SAMPLE_HACKATHONS = [
    {
        "id": "build-with-gemini",
        "name": "Build with Gemini World Tour",
        "url": "https://cszhu.github.io/build-with-gemini/",
        "deadline_raw": "October 15, 2026 at 11:59 PM PT",
        "deadline_source_quote": "Submissions must be received by October 15, 2026 at 11:59 PM PT to be eligible for prizes.",
        "timezone": "America/Los_Angeles",
        "deadline_utc": "2026-10-16T06:59:00Z",
        "ship_by_date": "2026-10-14",
        "days_remaining": 20,
        "status": "active",
        "cover_image_url": "https://raw.githubusercontent.com/cszhu/build-with-gemini/main/assets/build-with-gemini-banner.png",
        "checklist_items": [
            {"text": "Public GitHub repository with Apache 2.0 / MIT license", "done": True},
            {"text": "Architecture diagram in README.md", "done": True},
            {"text": "Working 3-minute video demo link", "done": False},
            {"text": "Live deployed URL on Cloud Run or Agent Platform", "done": True},
            {"text": "Fill out Google Form submission", "done": False},
        ],
    },
    {
        "id": "ai-partner-catalyst",
        "name": "Google Cloud AI Partner Catalyst",
        "url": "https://devpost.com/hackathons/google-ai-partner-catalyst",
        "deadline_raw": "November 2, 2026 at 5:00 PM EST",
        "deadline_source_quote": "All project submissions must be completed before 5:00 PM EST on November 2, 2026.",
        "timezone": "America/New_York",
        "deadline_utc": "2026-11-02T22:00:00Z",
        "ship_by_date": "2026-11-01",
        "days_remaining": 38,
        "status": "active",
        "cover_image_url": None,
        "checklist_items": [
            {"text": "Use Vertex AI Agent Platform or Gemini models", "done": True},
            {"text": "Include pitch deck PDF (max 10 slides)", "done": False},
            {"text": "Provide test credentials for judges", "done": False},
        ],
    },
    {
        "id": "open-agents-hack",
        "name": "Global Open Agents Challenge",
        "url": "https://openagents.dev/challenge",
        "deadline_raw": "December 1, 2026 at 23:59 UTC",
        "deadline_source_quote": "Submission window closes December 1, 2026 at 23:59 UTC strictly.",
        "timezone": "UTC",
        "deadline_utc": "2026-12-01T23:59:00Z",
        "ship_by_date": "2026-11-30",
        "days_remaining": 67,
        "status": "active",
        "cover_image_url": None,
        "checklist_items": [
            {"text": "A2A protocol compliant agent card endpoint", "done": False},
            {"text": "Automated evaluation dataset with LLM-as-a-judge score > 80%", "done": False},
            {"text": "Open source code on GitHub", "done": False},
        ],
    },
]


def seed():
    print(f"Connecting to Firestore with project ID: {FIRESTORE_PROJECT_ID}...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    batch = db.batch()

    for item in SAMPLE_HACKATHONS:
        doc_ref = db.collection(HACKATHONS_COLLECTION).document(item["id"])
        batch.set(doc_ref, item)
        print(f"  Queued: {item['name']} (ID: {item['id']})")

    batch.commit()
    print("✅ Firestore successfully seeded with sample hackathons!")


if __name__ == "__main__":
    seed()
