# PortalSahayak - Full stack distributed Automation engine

A worker-owned browser automation platform engineered to automate complex child health screening workflows on the Government of India’s RBSK portal.

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

## Core Engineering Highlights

1. **Worker-Owned Architecture**: Transitioned away from traditional shared browser states across API threads into isolated, independent Playwright runtimes that communicate via strict command and event boundaries.
2. **WebSocket Diagnostic Streams:** Designed a live communication pipeline using WebSockets to stream real-time task statuses and continuous background logs straight to the frontend UI layer.
3. **Production Deployment Pipeline:** Built fully containerized deployment configurations using Docker, backed by an automated CI/CD engine running validation testing suites within GitHub Actions.