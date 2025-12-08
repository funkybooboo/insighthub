# Tutorial 2: Company Docs Assistant

Project: Multi-document workspace for company information
Time: 20 minutes

## What You'll Build

- Create a company documentation workspace
- Upload 3 policy documents
- Create multiple chat sessions for different topics
- Search across all documents simultaneously

## Setup

Services should still be running from Tutorial 1. Verify:

```bash
task health-check
```

## Step 1: Create Company Workspace

Create a new workspace for company documentation.

```bash
task cli -- workspace create
```

When prompted:

```
Workspace name: Company Policies
Workspace description: HR, IT, and operations policies
```

Output:

```
Workspace created successfully
ID: 2
Name: Company Policies
Description: HR, IT, and operations policies
Created: 2025-12-07T10:15:00
```

## Step 2: Create Sample Policy Documents

Create three company policy documents.

Document 1 - Save as hr-policy.txt:

```
HR Policy Handbook

Remote Work Policy: Employees can work remotely up to 3 days per week. Remote work
requests require manager approval. Core hours are 10am to 3pm in your local timezone.
All remote workers must have a stable internet connection and a dedicated workspace.
VPN is required for accessing company systems.

Vacation Policy: Employees receive 20 days of paid vacation per year. Vacation must
be requested at least 2 weeks in advance. Maximum 10 consecutive days without approval
from director level. Unused vacation does not roll over to the next year.
```

Document 2 - Save as it-policy.txt:

```
IT Security Policy

Password Requirements: All passwords must be at least 12 characters including uppercase,
lowercase, numbers, and special characters. Passwords must be changed every 90 days.
Do not write passwords down or share them with anyone.

Software Installation: Only approved software can be installed on company computers.
Submit requests through the IT portal. Personal software is prohibited. All software
must have valid licenses. IT will periodically audit installed software.

Data Security: Sensitive data must be encrypted at rest and in transit. Customer data
cannot be stored locally. All data transfers require VPN. USB drives are prohibited.
Backup data weekly to company servers.
```

Document 3 - Save as operations-policy.txt:

```
Operations Policy

Office Hours: Main office open Monday through Friday 8am to 6pm. Conference rooms
available 24/7 with booking system. All equipment must be returned before leaving.
Cleaning service runs every night after 7pm.

Equipment Requisition: Submit requests through procurement portal. Budget approval
required for items over $500. Quotes needed for items over $1000. Delivery typically
takes 5-10 business days.

Meeting Rooms: Book rooms through calendar system. Cancel if plans change. Rooms
allocated by team. Video conference equipment setup requires 24 hours notice.
Technical support available during business hours.
```

## Step 3: Select Company Workspace

Activate the company workspace:

```bash
task cli -- workspace select
```

Choose "Company Policies".

Output:

```
Workspace selected: Company Policies
```

## Step 4: Upload All Policy Documents

Upload each policy document for searching.

Upload HR policy:

```bash
task cli -- document add hr-policy.txt vector
```

Output:

```
Document added successfully
ID: doc_004
Name: hr-policy.txt
Type: vector
Processed tokens: 89
```

Upload IT policy:

```bash
task cli -- document add it-policy.txt vector
```

Output:

```
Document added successfully
ID: doc_005
Name: it-policy.txt
Type: vector
Processed tokens: 95
```

Upload Operations policy:

```bash
task cli -- document add operations-policy.txt vector
```

Output:

```
Document added successfully
ID: doc_006
Name: operations-policy.txt
Type: vector
Processed tokens: 87
```

All three policy documents are now uploaded and searchable.

## Step 5: Create HR Chat Session

Create a dedicated chat for HR-related questions.

```bash
task cli -- chat create
```

When prompted:

```
Session name: HR Questions
Session description: Questions about HR policies and benefits
```

Output:

```
Chat session created successfully
ID: session_002
Name: HR Questions
Workspace: Company Policies
```

## Step 6: Create IT Chat Session

Create a dedicated chat for IT-related questions.

```bash
task cli -- chat create
```

When prompted:

```
Session name: IT Support
Session description: Questions about IT policies and security
```

Output:

```
Chat session created successfully
ID: session_003
Name: IT Support
Workspace: Company Policies
```

## Step 7: Create Operations Chat Session

Create a dedicated chat for operations questions.

```bash
task cli -- chat create
```

When prompted:

```
Session name: Operations
Session description: Questions about office and equipment
```

Output:

```
Chat session created successfully
ID: session_004
Name: Operations
Workspace: Company Policies
```

Three chat sessions now available.

## Step 8: Use HR Session

Switch to the HR chat and ask a question.

First select the HR session:

```bash
task cli -- chat select
```

Choose "HR Questions".

Ask a question:

```bash
task cli -- chat message "What is the vacation policy?"
```

Output:

```
Session: HR Questions
User: What is the vacation policy?

Response:
According to company policy, employees receive 20 days of paid vacation per year.
Vacation requests must be submitted at least 2 weeks in advance. You can take a
maximum of 10 consecutive days without director-level approval. Unused vacation
does not carry over to the next year.

Sources:
- hr-policy.txt (match: 0.94)
```

The system found the matching HR policy document.

## Step 9: Use IT Session

Switch to IT support:

```bash
task cli -- chat select
```

Choose "IT Support".

Ask a security question:

```bash
task cli -- chat message "What are password requirements?"
```

Output:

```
Session: IT Support
User: What are password requirements?

Response:
Passwords must be at least 12 characters long and include uppercase letters, lowercase
letters, numbers, and special characters. Passwords must be changed every 90 days.
Never write passwords down or share them with anyone.

Sources:
- it-policy.txt (match: 0.96)
```

The system found the right policy from your documents.

## Step 10: Use Operations Session

Switch to operations:

```bash
task cli -- chat select
```

Choose "Operations".

Ask about equipment:

```bash
task cli -- chat message "How do I request new office equipment?"
```

Output:

```
Session: Operations
User: How do I request new office equipment?

Response:
Submit equipment requests through the procurement portal. Items over $500 require
budget approval. For items over $1000, you need to provide quotes. Delivery typically
takes 5-10 business days.

Sources:
- operations-policy.txt (match: 0.92)
```

Each session searches your documents and finds answers.

## Step 11: Cross-Document Query

Switch back to HR and ask a question spanning multiple documents:

```bash
task cli -- chat select
```

Choose "HR Questions".

```bash
task cli -- chat message "Can I work remotely and what equipment do I need?"
```

Output:

```
Session: HR Questions
User: Can I work remotely and what equipment do I need?

Response:
Yes, employees can work remotely up to 3 days per week with manager approval.
Remote workers need a stable internet connection, dedicated workspace, and VPN
access. For specific equipment needs, contact operations through the procurement
portal.

Sources:
- hr-policy.txt (match: 0.87)
- operations-policy.txt (match: 0.71)
```

The system found information from multiple documents to answer your question.

## Testing

Verify all documents are in the workspace:

```bash
task cli -- document list
```

Expected output shows all 6 documents (3 from tutorial 1, 3 from tutorial 2).

Test cross-session queries:

```bash
task cli -- chat select
```

Choose any session and ask questions. The system automatically finds relevant
documents across all your policies.

## What You Learned

- Creating multi-document workspaces
- Organizing documents by category
- Using multiple chat sessions for different topics
- Searching across all documents at once
- How the system finds answers in policy documents
