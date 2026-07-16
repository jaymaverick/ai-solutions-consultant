---
sidebar_label: Ingestion First Architecture
sidebar_position: 2
project: Edge-AI Field Audit Engine
domain: Real Estate Risk Compliance
architecture: Ingestion-First / Multi-Modal Edge Inference
status: Part 2 - Ingestion-First Architecture
---
# Ingestion-First Architecture

The field operator is not a data entry clerk. Their job is to inspect and record. Not micromanage databases or fiddle with shoddy webforms.

In fact, the field operator shouldn't have to worry about what happens to the data after clicking "Send."

This is why we use an **Ingestion-First** framework. We decouple the physical field operator from the database structure entirely. 

Here's how.

1. The field client app captures data in its rawest, lowest-friction states: unstructured Finnish speech and rapid visual arrays.
2. It dumps it onto a hardened boundary. 
3. The system catches the payload.
4. Our backend automation handle the structural heavy lifting.

## System Topology Flowchart

The following architectural layout maps how field assets change states sequentially across our isolated zones: moving safely from an unpredictable mobile app collection space to a hardened production data asset.

![](../../static/img/Safetum%20System%20Topology.png)

## Architectural Walkthrough

1. **Asynchronous Decoupling (The Ingestion Boundary):** 
    
2. **Isolated Cognitive Pipeline (The Inference Layer):** 
    
3. **Strict Boundary Guardrails (The Structural Interface):** 
    
4. **Deterministic Exception Routing (Failsafe & HITL):** 

### 1. The Data Ingestion Boundary

The ingestion layer serves as a decoupled gateway. 

It catches a volatile binary data streams from the field application and sends a lightweight, highly structured event payload downstream. 

This all while releasing the field operator's network connection in under 200 milliseconds.

#### The FastAPI Multipart Gateway (API Endpoint)

Because the HTTP/1.1 standard dictates that file uploads must utilize `multipart/form-data`, standard `application/json` body payloads cannot be natively mixed with raw binary streams without explicit formatting guardrails.

To bypass this protocol limitation, the endpoint accepts text metadata via a stringified form field (`metadata_payload`) alongside an arbitrary array of files. It then manually deserializes and validates the string back into an internal Pydantic tracking model.

<details>

<summary>Show Python</summary>

```
import uuid
import json
from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel

app = FastAPI()

class IngestionMetadata(BaseModel):
    facility_uuid: str
    inspector_id: str

@app.post("/api/v1/compliance/ingest", status_code=202)
async def ingest_field_media(
    metadata_payload: str = Form(description="Stringified JSON matching IngestionMetadata schema"),
    files: List[UploadFile] = File(description="Array containing 1 .mp3/.wav audio file and up to 4 .jpg/.png images")
):
    # 1. Enforce strict schema validation on the incoming form metadata string
    try:
        meta_dict = json.loads(metadata_payload)
        metadata = IngestionMetadata(**meta_dict)
    except Exception:
        raise HTTPException(status_code=422, detail="Malformed metadata payload structure.")

    # 2. Initialize immutable tracking infrastructure
    session_uuid = str(uuid.uuid4())
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    
    # 3. Handoff to decoupled storage and event emission layers
    # (Detailed in the following sub-sections)
    return {
        "status": "ACCEPTED",
        "session_uuid": session_uuid,
        "timestamp_utc": timestamp_iso,
        "message": "Payload queued for background processing pipeline."
    }
```
</details>

#### Streamed File Persistence Architecture

Loading high-resolution multi-modal image buffers and audio memos straight into system memory creates a severe risk of Out-Of-Memory (OOM) fatal crashes when multiple field inspectors upload files concurrently.

To eliminate this vulnerability, the ingestion layer utilizes non-blocking asynchronous I/O to stream file chunks directly out of the incoming network buffer and into an air-gapped, S3-compatible Object Storage volume.

Files are structured using a strictly predictable, partitioned directory hierarchy:

`/storage/compliance-media/{facility_uuid}/{session_uuid}/{media_uuid}.{extension}`

- **Isolation:** If an audio file or an image is corrupted or malicious, it is sandboxed at rest inside object storage before any execution layer touches it.
    
- **Zero Memory Bloat:** Files are piped in tight 1MB allocation chunks (`await file.read(1024 * 1024)`), guaranteeing that a 100MB voice memo consumes exactly 1MB of runtime RAM during its write lifecycle.
    

#### Meta-UUID Generation & Ledger Event Payload

Before the payload pointers are dropped onto the message queue, the ingestion boundary generates an immutable event ledger. Every single raw file name is stripped and renamed to a cryptographically secure `UUIDv4`. This decouples the file's physical identity from user machine names, mitigating file-path traversal injection vectors.

The resulting data packet dropped into the message queue looks like this:

<details>
<summary>Show JSON</summary>

```
{
  "event_id": "evt_8f3b219a-4c22-4a11-b019-9e8c334f55e1",
  "session_uuid": "99b7b621-72da-4b8c-9c71-04df86675bb2",
  "facility_uuid": "espoo-property-991A",
  "inspector_id": "insp_0884",
  "timestamp_utc": "2026-06-09T17:15:32.119Z",
  "media_manifest": {
    "audio_track": {
      "media_uuid": "aud_11bc82fa-0129-43d8-a81d-773aee22b102",
      "storage_path": "/storage/compliance-media/espoo-property-991A/99b7b621-72da-4b8c-9c71-04df86675bb2/aud_11bc82fa-0129-43d8-a81d-773aee22b102.mp3",
      "content_type": "audio/mp3"
    },
    "visual_frames": [
      {
        "media_uuid": "img_f78a2210-9bca-4eef-8dd9-1a3b11cde701",
        "storage_path": "/storage/compliance-media/espoo-property-991A/99b7b621-72da-4b8c-9c71-04df86675bb2/img_f78a2210-9bca-4eef-8dd9-1a3b11cde701.jpg",
        "content_type": "image/jpeg"
      }
    ]
  }
}
```
</details>
### 2. The n8n Webhook Gateway

n8n is an open-source workflow automation engine built for technical environments. 

Instead of hard-coding hundreds of lines of fragile glue code just to handle API routing, binary data unpacking, and error tracking, n8n gives us a visual, node-based Directed Acyclic Graph (DAG) canvas to map out system logic. 

In this pipeline, n8n acts as the central nervous system:

1. It catches the ledger event payload.
    
2. It handles the parallel extraction of audio streams and image buffers.
    
3. It maps model sequencing—routing transcripts to vision prompts sequentially.
    
4. It catches processing exceptions cleanly before they can disrupt relational storage.



:::tip
#### Self-Hosting (The Data Privacy Shield)

By self-hosting n8n inside a Docker container on isolated infrastructure (such as an air-gapped server or a secure local cloud node like atNorth), no data ever leaves our physical or legal control. 

The webhook URL points directly to our owned network perimeter. We gain the velocity of modern orchestration interfaces with a 100% airtight data privacy boundary.
:::
### 3. The Schema Validation Layer (The Data Contract)

The Pydantic data contract executes at **Stage 3** of the topology layout. It serves as our final deterministic checkpoint.

The n8n orchestrator collects the probabilistic string predictions generated by the local VLM, but before that text can get anywhere near our PostgreSQL database tables, it is passed to this script to be mathematically validated against our structural rules.

<details>

<summary>Show Python</summary>

```
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, confloat

class HazardCategory(str, Enum):
    ESCAPE_ROUTE_OBSTRUCTION = "Escape Route Obstruction"
    FIRE_DOOR_COMPROMISED = "Fire Door Compromised"
    SAFETY_SIGNAGE_MISSING = "Safety Signage Missing"
    EQUIPMENT_MAINTENANCE_LAPSE = "Equipment Maintenance Lapse"
    SHELTER_READINESS_DEFECT = "Shelter Readiness Defect"  # Väestönsuoja
    UNCLASSIFIED_HAZARD = "Unclassified Hazard"

class RemediationPriority(str, Enum):
    LOW = "LOW"          # Advisory / Administrative
    MEDIUM = "MEDIUM"    # Requires attention within 14 days
    CRITICAL = "CRITICAL"  # Immediate liability / High danger

class RiskAssessmentNote(BaseModel):
    """
    Schema for enforcing structured, validated extractions from unstructured
    field media regarding physical real estate property safety compliance.
    """
    
    # Meta tracking to match target corporate database records
    location_context: str = Field(
        description="The specific area of the property identified from the audio or image (e.g., 'Basement Corridor B', 'Stairwell 3')."
    )
    
    # Strict Enum validation forces the AI to pick from known database categories
    hazard_type: HazardCategory = Field(
        description="The matching category of the safety violation based on Finnish fire regulations."
    )
    
    # Precise extraction of the core physical problem
    descriptive_summary: str = Field(
        description="A concise, neutral, professional summary of the physical hazard. Do not include chatty filler text."
    )
    
    # Quantitative Risk Index bounding (forces a float between 0.0 and 1.0)
    severity_score: confloat(ge=0.0, le=1.0) = Field(
        description="Calculated risk severity. 0.0 represents nominal/advisory, 1.0 represents immediate physical danger or illegal non-compliance."
    )
    
    # Context-driven priority categorization
    priority_level: RemediationPriority = Field(
        description="The operational handling priority derived directly from the severity score and hazard context."
    )
    
    # Legislative Enrichment Mapping
    finnish_legal_reference: str = Field(
        description="The precise clause from Finnish law relevant to this hazard, specifically citing 'Pelastuslaki 379/2011' or relevant building codes."
    )
    
    # Dynamic lifecycle personalization variables
    client_action_trigger: str = Field(
        description="A direct, outcome-focused instruction tailored to the property manager explaining the exact fix required to achieve compliance."
    )

class RealEstateCompliancePayload(BaseModel):
    """The master wrapper payload emitted to the downstream persistence layer."""
    facility_uuid: str = Field(description="The validated tracking ID of the real estate asset.")
    timestamp_utc: str = Field(description="ISO-8601 formatted ingestion timestamp.")
    findings: List[RiskAssessmentNote] = Field(description="Array of validated compliance violations caught in the session.")
```

</details>

### 4. Human-in-the-loop Failsafe Before Entering PostgreSQL

If an LLM drops tokens or fails deterministic Pydantic schema constraints, processing is suspended before touching relational tables. 

The record is flagged and automatically routed to an internal Human-in-the-Loop (HITL) Triage Dashboard, where a human reviewer can verify or adjust the entry with a single click before committing it to the production PostgreSQL Database.

## Evaluating LLM Model Choice

Evaluating an AI deployment strategy requires navigating significant architecture trade-offs. An enterprise solutions engineer must thoroughly assess model hosting topologies against security, cost, and optimization constraints before deploying code to production.

### Can a Local Vision Model Handle this Task?

**Yes, absolutely.** Modern, open-source Vision-Language Models (VLMs)—such as `Llama-3.2-Vision-11B` or `Qwen2-VL`—possess excellent localized visual comprehension.

Local inference engines natively support structured JSON token forcing through sampling constraints. By supplying our target data contract directly into the model's compilation parameters via tools like `Instructor`, the neural net limits its token selection strictly to valid schema grammar.

- **The Infrastructure Constraint:** Running local multi-modal inferencing at enterprise scale under a sub-5-second execution SLA demands dedicated on-premise compute. The architecture requires specialized graphics accelerators (such as an NVIDIA RTX 4090 or enterprise NVIDIA L4 node) to prevent the Redis event broker queue from saturating.

### Can We Leverage Public Cloud LLM Services?

**Technically yes, but it introduces a severe legal and operational trap.** Utilizing public frontier APIs (such as OpenAI's GPT-4o or Anthropic's Claude 3.5 Sonnet) delivers elite multi-modal accuracy out of the box. Their native JSON-forcing modes offer a 100% guarantee that data structures won't break formatting.

See [Future Strategy and Scale](Future%20Strategy%20and%20Scale.md) for cloud infrastructure expansion possibilities.

:::danger
### The Data Sovereignty Blocker

In a European real estate compliance landscape, a public cloud architecture introduces direct exposure to severe GDPR violations. Inspection photos are captured inside private residential complexes, storage hallways, and apartment basements. These raw media streams regularly capture tenant **Personally Identifiable Information (PII)**: faces, package labels, names on door plates, and vehicle registration markers.

Transmitting raw, unredacted visual imagery of citizen living spaces to US-governed cloud servers will trigger immediate data protection rejections from corporate enterprise legal teams.
:::

## The Model Prompt Template

This raw system context block is programmatically injected into the n8n Ollama node template, instructing the VLM how to interpret mixed contexts while explicitly forbidding conversational responses.

<details>

<summary>Show Prompt Template</summary>

```
SYSTEM: You are an elite real estate risk assessment and structural safety automation engine. Your objective is to cross-reference unstructured field media inputs against Finnish property safety legislation (Pelastuslaki 379/2011).

CONTEXT INPUTS:
- Field Audio Transcript: "{{ $json.whisper_transcript }}"
- Inspection Media: [Attached Image Arrays]

OPERATIONAL EXAMPLES & MANDATES:
1. If the audio transcript mentions a "blocked path" or "clutter" and images show items in a stairwell or corridor, categorize strictly as "ESCAPE_ROUTE_OBSTRUCTION".
2. Match findings to explicit legislative text. For route obstructions, explicitly cite "Pelastuslaki 379/2011, 10 §" (Duty to maintain escape routes).
3. Evaluate risk severity: If an exit is completely blocked (e.g., bicycles blocking a basement fire exit), assign a severity_score >= 0.85 and set priority_level to "CRITICAL".

OUTPUT INSTRUCTION:
You must output a single, raw JSON string matching the expected structural schema. 
Do not wrap your response in markdown backticks (```json). Do not include introductory text, conversational filler, or summary conclusions. Begin your response directly with the open bracket "{".
```
</details>


## The AI Quality Assurance & Evaluation Framework

Unlike deterministic legacy codebases, non-deterministic neural networks cannot be validated using basic unit tests. 

To guarantee the local Vision-Language Model does not hallucinate false legal assertions or drift in its categorical logic over time, the system implements a non-production evaluation and regression pipeline built using programmatic test harnesses (e.g., `DeepEval`).

<details>

<summary>Show Evaluation Framework</summary>

```
                                    +-----------------------+
                                    |  VLM Prompt/Weights   |
                                    |     Modifications     |
                                    +-----------+-----------+
                                                |
                                                v
+-----------------------+           +-----------+-----------+
|  The Golden Dataset   |           |    Execution Engine   |
| (100 Verified Assets) +---------->+  (Local Model Loop)   |
+-----------------------+           +-----------+-----------+
                                                |
                                                v
                                    +-----------+-----------+
                                    |    Evaluation Gate    |
                                    | (DeepEval Harness)    |
                                    +-----------+-----------+
                                                |
                               +----------------+----------------+
                               |                                 |
                               v                                 v
                     [Schema Adherence]                 [Semantic F1-Score]
                        Target: 100%                       Target: >= 0.91
                               |                                 |
                     +---------+---------+             +---------+---------+
                     |                   |             |                   |
                     v                   v             v                   v
                  [ FAIL ]            [ PASS ]      [ FAIL ]            [ PASS ]
                     |                   |             |                   |
                     v                   |             v                   |
             (Block Deployment)          +----->(Allow Production CI/CD Merge)
```
</details>
### The Golden Dataset

The evaluation pipeline relies on a locked benchmarking suite consisting of **100 historical, hand-verified inspection media assets** (50 raw Finnish audio files, 50 high-resolution hazard images). Each asset is mapped to an immutable, human-certified "Ground Truth" JSON target record that accurately references the true structural violations and legal clauses.

### The Regression Testing Gate

Prior to any production deployment, CI/CD pipeline merge, prompt modification, or local model weight update, the orchestration framework automatically feeds the Golden Dataset through the inference engine. The output payload strings are systematically evaluated against two core metrics:

- **Schema Adherence Score:** The structure must achieve a **100% pass rate**. Any malformed JSON strings, missing brackets, or unmapped enum attributes cause an immediate build failure.
    
- **Semantic F1-Score:** The accuracy of the hazard type classification and legislative mapping must maintain a threshold of **$\ge 0.91$** against the Ground Truth dataset. If the model shifts its interpretation of a hazard incorrectly, the deployment is blocked automatically, preventing logic regressions from reaching production tables.
    

## Ingestion Border Security (Defensive Edge Hardening)

Exposing a multipart/form-data endpoint to receive arbitrary file binaries creates an immediate attack vector for database flooding, remote code execution (RCE) attempts, and malicious server memory saturation. 

To safeguard the private network perimeter, the FastAPI gateway implements three explicit defensive security filters:

- **Token-Based Cryptographic Authentication:** The API perimeter enforces strict authentication checks on all incoming requests. The system parses and verifies cryptographically signed `Bearer JWT` (JSON Web Tokens) or pre-shared enterprise API keys injected directly into the HTTP header. Requests from unauthenticated clients are rejected at the edge before data buffers are opened.
    
- **Payload Bound Clamping (DoS Mitigation):** To prevent malicious Denial-of-Service attacks designed to exhaust disk and RAM allocations via massive file payloads, the FastAPI application layer checks the incoming `Content-Length` header. The gateway actively drops the connection if any single file stream buffer exceeds a rigid **15MB ceiling**.
    
- **Magic-Byte MIME-Type Whitelisting:** Attackers frequently attempt to disguise malicious scripts by spoofing basic file extensions (e.g., renaming an executable script to `evidence.jpg`). To mitigate this vector, the ingestion boundary bypasses basic string extension checks and evaluates the binary file's **magic-byte signatures** directly inside the buffer. The pipeline immediately drops any payload whose underlying structure fails to map to a verified whitelist: `audio/mpeg`, `audio/wav`, or `image/jpeg`.