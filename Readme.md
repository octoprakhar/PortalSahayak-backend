# PortalSahayak - Full stack distributed Automation engine

A worker-owned browser automation platform engineered to automate complex child health screening workflows on the Government of India’s RBSK portal.

## Why PortalSahayak?

PortalSahayak was built to reduce the manual effort involved in entering child
health screening data into the Government of India's RBSK portal.

The original workflow required healthcare workers to repeatedly search for
children, enter personal and health information, handle existing children,
apply screening rules, and manually verify the results through a browser-based
portal.

PortalSahayak automates this workflow while keeping the execution observable
through real-time status updates, logs, and final success/failure reports.

The system was designed around isolated worker-owned browser runtimes so that
long-running Playwright automation is not tied to the lifecycle of individual
FastAPI requests.

## System Architecture
```text
                       ┌──────────────┐                                    
                       │React Frontend│                                    
                       └─────┬────────┘                                    
                             │                                             
                      REST + WebSocket                                     
                             │                                             
                             │                                             
                      ┌──────▼────────┐                                    
                      │FastAPI Gateway│                                    
                      └─────┬─────────┘                                    
                            │                                              
                         Commands                                          
                            │                                              
                            │                                              
                    ┌───────▼──────────────────────┐                       
                    │  Worker Runtime              │                       
                    │                              │                       
                    │   Metadata Worker            │                       
                    │   Facility Worker            │                       
                    │   Screening Worker           │                       
                    │                              │                       
                    │  ┌──────────────┐            │                       
                    │  │Worker Mailbox│            │                       
                    │  └──────────────┘            │                       
                    │                              │                       
                    │  Playwright browser instance │                       
                    │                              │                       
                    └──────────┬───────────────────┘                       
                          ┌────▼─────┐                                     
      ┌───────────────────┼  Events  ┼──────────────────────────────┐      
      ▼                   └───────▼──┘                              ▼      
Websocket Listner           Persistance Listner                Reports/Logs
     │                              │                               │      
     ▼                              ▼                               ▼      
  Frontend                       Supabase                         Storage                 
```

## Core End-to-end Flow

```text

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                                          │
│                                                  CORE EXECUTION FLOW                                                                     │
│                                               ──────────────────────────                                                                 │
│                                                                                                                                          │
│                                                                                                                                          │
│          ┌───────────────────┐           ┌────────────────────────────┐              ┌───────────────────────────────────────┐           │
│          │  User Uploads CSV ┼──────────►│  FastApi Validates Schemas ┼─────────────►│ Job is saved in Supabase as 'Pending' │           │
│          └───────────────────┘           └────────────────────────────┘              └─────────────────────┬─────────────────┘           │
│                                                                                                            │                             │
│                          ┌────────────────────────┐              ┌───────────────────────────────┐         │                             │
│                          │ Websockets Stream logs │◄─────────────┼Independent Worker Picks Up Job│◄────────┘                             │
│                          └───────────┬────────────┘              └───────────────────────────────┘                                       │
│                                      │                                                                                                   │
│                                      ┼──────── 1.Initializes headless browser runtime instance                                           │
│                                      │                                                                                                   │
│                                      ┼──────── 2.Securely log in to government portal                                                    │
│                                      │                                                                                                   │
│                                      ┼──────── 3.Processes screening steps and run classification loops                                  │
│                                      │                                                                                                   │
│                                      │                                                                                                   │
│                          ┌───────────▼─────────────────────┐                     ┌────────────────────────────────────────────┐          │
│                          │Job Status updated to 'Completed'┼────────────────────►│Generates final success report and pdf logs │          │
│                          └─────────────────────────────────┘                     └────────────────────────────────────────────┘          │
│                                                                                                                                          │
│                                                                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

```

## Features

- Automated child health screening workflow using Playwright.
- Worker-owned browser runtimes for isolated automation execution.
- Multi-worker architecture for registration metadata, facility data,
  institution selection, and screening workflows.
- REST APIs for job and user management.
- Supports processing both new children and existing children without
  previously recorded screening data.
- Real-time job status and execution logs through WebSockets.
- Automatic success and failure report generation.
- Persistent job, user, report, and execution data using PostgreSQL/Supabase.
- Cloud storage for uploaded files, generated reports, and logs.
- Dockerized application for reproducible deployment.
- Automated Docker image build and deployment pipeline using GitHub Actions.

## Worker Architecture

PortalSahayak follows a worker-owned architecture where each worker owns its
execution lifecycle and Playwright browser runtime.

The API layer does not directly manipulate Playwright objects. Instead, it
creates workers and communicates with them through commands and events.

```text
                             ┌───────────────┐                                   
                             │  FastApi Api  │                                   
                             └───────┬───────┘                                   
                                     │                                           
                                  Commands                                       
                                     │                                           
                            ┌────────▼──────────┐                                
                            │   Worker Factory  │                                
        ┌───────────────────┴─────────┬─────────┴─────────────────────┐          
        │                             │                               │          
 ┌──────▼─────────┐            ┌──────▼──────────┐             ┌──────▼─────────┐
 │ Metadata Worker│            │ Facility Worker │             │Screening Worker│
 └─────┬──────────┘            └───────┬─────────┘             └──────┬─────────┘
       │                               │                              │          
   ┌───▼──────┐                   ┌────▼─────┐                   ┌────▼─────┐    
   │Playwright│                   │Playwright│                   │Playwright│    
   │ Runtime  │                   │ Runtime  │                   │ Runtime  │    
   └───┬──────┘                   └──┬───────┘                   └───┬──────┘    
       │                             │                               │           
       └─────────────────────────  Events ───────────────────────────┘           
                                     │                                           
                                ┌────▼──────┐                                    
     ┌──────────────────────────┼ Event Bus ┼───────────────────┐                
     │                          └──┬────────┘                   │                
     │                             │                            │                
 ┌───▼─────┐                  ┌────▼──────┐                ┌────▼─────────┐      
 │Websocket│                  │Persistence│                │Other Listners│      
 │Listner  │                  │ Listner   │                └──────────────┘      
 └───┬─────┘                  └─────┬─────┘                                      
┌────▼─────┐                   ┌────▼───────────┐                                
│ Frontend │                   │Database/storage│                                
└──────────┘                   └────────────────┘                                
```

### Why worker ownership?

Playwright browser, context, and page objects are owned exclusively by the
worker that created them.

FastAPI requests communicate with workers through commands instead of sharing
browser objects across request threads.

Workers publish events when important execution state changes. Independent
listeners consume these events for persistence, WebSocket updates, logging,
and other side effects.

This separates browser automation from API request handling and makes the
long-running execution lifecycle explicit.

## Persistence Architecture

Persistence is separated from the workers through event-driven listeners and
repository abstractions.

Workers do not directly perform database or storage operations for their
execution results. Instead, they emit domain events which are consumed by the
persistence layer.

```text
              ┌───────────────────┐                               
              │      Worker       │                               
              │   ScreeningWorker │                               
              └───────┬───────────┘                               
                      │                                           
                    Events                                        
                      │                                           
                ┌─────▼─────────────┐                             
                │ PersistanceListner│                             
      ┌─────────┴───────────┬───────┴─────────────────┐           
      │                     │                         │           
┌─────▼────────┐       ┌────▼────────┐          ┌─────▼──────────┐
│UserRepository│       │JobRepository│          │ReportRepository│
└┬─────────────┘       └──┬──────────┘          └───────┬────────┘
 │                        │                             │         
 │    ┌───────────────────▼───────────┐                 │         
 │    │         Supabase / PostgreSQL │                 │         
 └───►│                               │                 │         
      │   User                        ◄─────────────────┘         
      │   Screening_Job               │                           
      └───────────────────────┬───────┘                           
                              │                                   
                              │                                   
                         ┌────▼─────┐                             
                         │Supabase  │                             
                         │Storage   │                             
                         │          │                             
                         │Report    │                             
                         │Logs      │                             
                         │Uploads   │                             
                         └──────────┘                             
```

## Report And Logging

### Report

Each completed job produces separate success and failure reports containing information such as:

* Child details and screening type
* Original and final health measurements
* Detected diseases
* Processing stage
* Validation errors
* Failure reason and system messages

Reports are generated by a dedicated **ReportCreator**, converted into CSV files, and uploaded to persistent object storage. Report metadata and storage paths are persisted separately through the **ReportRepository**.

```text
      Worker Execution                 
        │                              
        ┼───── Successfull Child Result
        │                              
        └───── Failed Child Result     
                  │                    
                  │                    
          ┌───────▼──────┐             
    ┌─────┼ ReportCreator┼──────┐      
    │     └──────────────┘      │      
    ▼                           ▼      
success.csv               failure.csv  
  │                             │      
  │                             │      
  └──────► Object Storage ◄─────┘      
                 │                     
                 ▼                     
          Job_report DB                
```

### Logging

Execution logs are produced throughout the worker lifecycle and streamed to the client through WebSockets. Logs are also persisted so that a completed or failed job can be inspected after execution. The logging system is designed around worker events rather than direct coupling between the automation workflow and the persistence layer.

## Tech Stack

### Backend
* Python
* FastAPI — HTTP API and application lifecycle
* Playwright — browser automation
* Pandas — input data processing
* WebSockets — real-time worker updates

### Architecture & Persistence
* PostgreSQL / Supabase — application data and job metadata
* Supabase Storage — reports, uploaded files and persistent job artifacts
* Repository abstractions for separating persistence from application logic
* Worker-based command/event architecture for background execution

### Frontend
* React
* WebSocket client for real-time job updates

### Infrastructure
* Docker — containerization
* GitHub Actions — CI/CD
* Docker Hub — container image registry
* Render — deployment

## Deployment

PortalSahayak is containerized using Docker so that the application and its browser automation dependencies can run in a reproducible environment.The project uses GitHub Actions to automatically build and publish the Docker image when changes are pushed to the **main** branch.

```text
     Developer            
        │                 
        │                 
        ▼                 
  GitHub Repository       
        │                 
        ▼                 
   Github Action          
   │                      
   ┼─── Build Docker Image
   │                      
   └─── Push Image        
          │               
          ▼               
    Docker Hub            
         │                
         ▼                
      Render              
         │                
         ▼                
Running PortalSahayak API 
```
The production container runs a headless Chromium instance through Playwright and exposes the FastAPI application through Uvicorn.

> **Note**: The current deployment is intended as a lightweight production/V1 deployment. Worker scaling, distributed queues, and multi-browser orchestration are future considerations.

## Project Structure

```text
 PortalSahayak-backend/               
│                                     
├────  all_model/                     
│      │                              
│      ├─  ApplicationServices.py     
│      ├─  WorkerEvent.py             
│      ├─  WorkerCotext.py            
│      └─  ....                       
│                                     
│                                     
├───── database/                      
│      │                              
│      ├─  model/                     
│      ├─  repository/                
│      ├─  Database.py                
│      └── storage/                   
│                                     
│                                     
├──────repository/                    
│      │                              
│      ├── UserRepository.py          
│      ├── JobRepository.py           
│      └── ReportRepository.py        
│                                     
│                                     
├───── worker/                        
│      │                              
│      ├─  WorkerAbstract.py          
│      ├─  ScreeningWorker.py         
│      ├─  UserMetadataWorker.py      
│      └─  ......                     
│                                     
│                                     
├───── event_listner/                 
│       │                             
│       ├─ WebsocketListner.py        
│       ├─ PersistenceListner.py      
│       ├─ CleanupListner.py          
│       └─ .....                      
│                                     
│                                     
├───── bridge/                        
│       │                             
│       └─ WorkerEventBridge.py       
│                                     
│                                     
├──────services/                      
│       │                             
│       ├─ RuntimeManager.py          
│       ├─ ReportCreator.py           
│       └─ .....                      
│                                     
│                                     
├──────workflow/                      
│      │                              
│      ├─  ScreeningWorker.py         
│      ├── ExistingChildWithoutData.py
│      └── ......                     
│                                     
│                                     
├───── disease/                       
│      │                              
│      ├─  factory/                   
│      └───.....                      
│                                     
│                                     
├───── router/                        
│      │                              
│      └── routes.py                  
│                                     
│                                     
├───── tests/                         
│                                     
│                                     
├────  Dockerfile                     
├──────requirements.txt               
├───── main.py                        
└───── README.md                      
```

>The project is organized around clear ownership boundaries. Workers own browser execution, repositories handle persistence, workflows contain domain execution logic, listeners react to worker events, and the API layer coordinates requests without directly controlling Playwright runtime state.