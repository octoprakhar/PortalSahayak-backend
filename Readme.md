This is the backend of my PortalSahayak app for RBSK.

## Important points
1. Before I was using table row index to find the column name but then I changed the method to column_map + health status, to check which student to enter in Existing child without data.

```python
readme_content = """# Architecture Overview: Decoupled Playwright Worker Pattern

## Problem Statement

The previous architecture shared Playwright browser, page, and context objects directly across multiple concurrent FastAPI request handlers. This architectural coupling caused severe operational vulnerabilities:

* **Thread Affinity Errors:** Playwright objects are tightly bound to the thread loop that initialized them. Concurrent access across multi-threaded FastAPI workers violated these loop boundaries.
* **Greenlet Switching Exceptions:** Async concurrency under ASGI servers led to illegal greenlet interleaving and coroutine state corruption when mutating shared browser contexts.
* **Complex Lifecycle Management:** Determining when to safely dispose of contexts or pages without disrupting active parallel requests became unmanageable.
* **Tight Component Coupling:** API routes were directly dependent on the underlying Playwright execution runtime, complicating testing, scaling, and error isolation.

---

## Solution: Actor-Inspired Worker Architecture

To resolve these concurrency and state issues, the system transitioned to a decoupled, event-driven architecture using an **Actor-inspired worker pattern**. 

Instead of exposing runtime objects to the API, every job lifecycle is strictly confined to an isolated execution unit.


```

```text
File written successfully.


```

┌─────────────────────────────────────────────────────────┐
│                     Isolated Job                        │
│ ┌───────────────┐ ┌───────────────┐ ┌─────────────────┐ │
│ │ Worker Thread │ │  Mailbox (Q)  │ │ Workflow State  │ │
│ └───────────────┘ └───────────────┘ └─────────────────┘ │
│ ┌───────────────┐ ┌───────────────┐ ┌─────────────────┐ │
│ │    Browser    │ │    Context    │ │      Page       │ │
│ └───────────────┘ └───────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────┘

```

Each provisioned job exclusively owns its entire environment:
* **Dedicated Worker Thread:** Guarantees total thread affinity and isolates synchronous blockages.
* **Private Mailbox:** A message queue processing incoming instructions sequentially.
* **Dedicated Playwright Suite:** An isolated Browser, Context, and Page instance per job, eliminating greenlet cross-contamination.
* **Workflow State Engine:** Keeps track of the execution step metrics internally.

Communication across system layers occurs strictly via immutable **Commands** and **Events** rather than memory-sharing or object-passing.

---

## Data & Communication Flow

### 1. Command Flow (Ingress)
API endpoints receive requests, validate inputs, and dispatch instructions to the designated worker's mailbox without blocking.


```

[ API Request ]
│
▼
[ Command ]
│
▼
[ Worker Mailbox ]
│
▼
[ Worker Thread ]
│
▼
[ Workflow Execution ]

```

### 2. Event Flow (Egress)
Workers communicate state changes, execution milestones, and errors asynchronously outward using a decoupled messaging layer.


```

```
[ Worker ]
    │
    ▼

```

[ WorkerEvent ]
│
▼
[ EventBus ]
│
├───► [ WebSocket Listener ]   (Real-time frontend streaming)
├───► [ Cleanup Listener ]     (Resource reclamation / Takedown)
├───► [ Persistence Listener ] (Database state mutations)
└───► [ Metrics Listener ]     (Telemetry & SLIs/KPIs)

```

---

## Architectural Design Patterns

This decoupled framework relies on four core software engineering design patterns:

### 🎭 Actor-Inspired Architecture
State is never shared or mutated globally. Each job acts as an autonomous unit (actor) that fully seals its private state (Playwright elements) and communicates exclusively via message passing.

### 📥 Producer-Consumer Pattern
API routers serve as the *Producers*, translating incoming HTTP requests into asynchronous commands. The backend worker threads serve as the *Consumers*, continuously pulling commands from their respective mailboxes and processing them in sequence.

### 📢 Publish-Subscribe Pattern
Workers remain agnostic of the broader system context; they publish execution events to a centralized `EventBus` without knowing which or how many consumers exist. Listeners register independently to react to specific events (e.g., UI syncing, auditing, or logging).

### 🔒 Single Ownership Principle
Playwright runtime objects (Browser, Context, Page) are allocated to, mutated by, and collected by exactly **one** worker thread. This eliminates cross-thread pollution and makes resource lifecycles deterministic.
"""

with open("readme.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("File written successfully.")



```

Your Markdown file is ready


Here is the formatted text for your `readme.md` file. It features professional formatting, architectural ASCII diagrams, clear visual hierarchies, and crisp summaries of your patterns.

```markdown
# Architecture Overview: Decoupled Playwright Worker Pattern

## Problem Statement

The previous architecture shared Playwright browser, page, and context objects directly across multiple concurrent FastAPI request handlers. This architectural coupling caused severe operational vulnerabilities:

* **Thread Affinity Errors:** Playwright objects are tightly bound to the thread loop that initialized them. Concurrent access across multi-threaded FastAPI workers violated these loop boundaries.
* **Greenlet Switching Exceptions:** Async concurrency under ASGI servers led to illegal greenlet interleaving and coroutine state corruption when mutating shared browser contexts.
* **Complex Lifecycle Management:** Determining when to safely dispose of contexts or pages without disrupting active parallel requests became unmanageable.
* **Tight Component Coupling:** API routes were directly dependent on the underlying Playwright execution runtime, complicating testing, scaling, and error isolation.

---

## Solution: Actor-Inspired Worker Architecture

To resolve these concurrency and state issues, the system transitioned to a decoupled, event-driven architecture using an **Actor-inspired worker pattern**. 

Instead of exposing runtime objects to the API, every job lifecycle is strictly confined to an isolated execution unit.


```

┌─────────────────────────────────────────────────────────┐
│                     Isolated Job                        │
│ ┌───────────────┐ ┌───────────────┐ ┌─────────────────┐ │
│ │ Worker Thread │ │  Mailbox (Q)  │ │ Workflow State  │ │
│ └───────────────┘ └───────────────┘ └─────────────────┘ │
│ ┌───────────────┐ ┌───────────────┐ ┌─────────────────┐ │
│ │    Browser    │ │    Context    │ │      Page       │ │
│ └───────────────┘ └───────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────┘

```

Each provisioned job exclusively owns its entire environment:
* **Dedicated Worker Thread:** Guarantees total thread affinity and isolates synchronous blockages.
* **Private Mailbox:** A message queue processing incoming instructions sequentially.
* **Dedicated Playwright Suite:** An isolated Browser, Context, and Page instance per job, eliminating greenlet cross-contamination.
* **Workflow State Engine:** Keeps track of the execution step metrics internally.

Communication across system layers occurs strictly via immutable **Commands** and **Events** rather than memory-sharing or object-passing.

---

## Data & Communication Flow

### 1. Command Flow (Ingress)
API endpoints receive requests, validate inputs, and dispatch instructions to the designated worker's mailbox without blocking.


```

[ API Request ]
│
▼
[ Command ]
│
▼
[ Worker Mailbox ]
│
▼
[ Worker Thread ]
│
▼
[ Workflow Execution ]

```

### 2. Event Flow (Egress)
Workers communicate state changes, execution milestones, and errors asynchronously outward using a decoupled messaging layer.


```

```
[ Worker ]
    │
    ▼

```

[ WorkerEvent ]
│
▼
[ EventBus ]
│
├───► [ WebSocket Listener ]   (Real-time frontend streaming)
├───► [ Cleanup Listener ]     (Resource reclamation / Takedown)
├───► [ Persistence Listener ] (Database state mutations)
└───► [ Metrics Listener ]     (Telemetry & SLIs/KPIs)

```

---

## Architectural Design Patterns

This decoupled framework relies on four core software engineering design patterns:

### 🎭 Actor-Inspired Architecture
State is never shared or mutated globally. Each job acts as an autonomous unit (actor) that fully seals its private state (Playwright elements) and communicates exclusively via message passing.

### 📥 Producer-Consumer Pattern
API routers serve as the *Producers*, translating incoming HTTP requests into asynchronous commands. The backend worker threads serve as the *Consumers*, continuously pulling commands from their respective mailboxes and processing them in sequence.

### 📢 Publish-Subscribe Pattern
Workers remain agnostic of the broader system context; they publish execution events to a centralized `EventBus` without knowing which or how many consumers exist. Listeners register independently to react to specific events (e.g., UI syncing, auditing, or logging).

### 🔒 Single Ownership Principle
Playwright runtime objects (Browser, Context, Page) are allocated to, mutated by, and collected by exactly **one** worker thread. This eliminates cross-thread pollution and makes resource lifecycles deterministic.

```

- Introduced Worker actor model with dedicated mailbox
- Added command-driven workflow execution
- Added per-worker EventBus and WorkerEvent system
- Implemented EventListener abstraction
- Added PersistenceListener for status and log persistence
- Added CleanupListener for worker lifecycle cleanup
- Decoupled RuntimeManager from JobManager
- Introduced WorkerContext and MetadataProvider abstraction
- Removed direct runtime-persistence coupling
- Established producer-consumer architecture between API and workers
- Verified success and failure flows through event-driven listeners

# Disease Subdomain

## Why this exists

The government portal automatically assigns diseases based on entered values.
Some diseases are incorrect and must be removed.
Some diseases are managed with quotas and validation rules.
The system must also support adding diseases later.

Because disease behavior is complex, a dedicated disease subdomain was introduced.

---

## Current architecture

DiseaseDefinition
DiseaseDetector
DiseaseManipulator
DiseaseRule
DiseaseRuleRepository
DiseaseContext
DiseaseCountManager
DiseaseRemovalStrategy
CheckboxRemovalStrategy
ValueRemovalStrategy
DiseaseRemovalStrategyRepository
DiseaseManager

---

## Responsibilities

### DiseaseDetector

Reads diseases currently present on the portal.

### DiseaseManipulator

Performs UI actions:
- check disease
- uncheck disease
- set height
- set weight
- set head circumference
- set Hb

### DiseaseRule

Determines whether a managed disease is allowed.

Examples:

- SAM
- Severe Stunting
- Mild Anaemia
- Moderate Anaemia
- Skin Conditions
- Dental Conditions

### DiseaseContext

Provides rules with:

- child data
- current counts
- max counts

### DiseaseCountManager

Tracks current and maximum counts of managed diseases.

### Removal Strategies

#### Checkbox removal

Used when diseases can be removed directly.

#### Value removal

Used when disease disappears only after changing measurements.

Current implementation:

- SAM removal

---

## DiseaseManager

Main orchestrator.

Flow:

1. Detect diseases.
2. Ignore user-selected diseases.
3. Remove incorrect portal-selected diseases.
4. Validate managed diseases through rules.
5. Remove invalid managed diseases.
6. Update managed disease counts.

---

## Tested scenarios

- Healthy child.
- Wrong checkbox diseases.
- SAM removal.
- Managed disease validation.

---

## Design goals

- Separation of concerns.
- Open for new diseases.
- Open for new strategies.
- Support future disease addition.
- Avoid giant if-else blocks.