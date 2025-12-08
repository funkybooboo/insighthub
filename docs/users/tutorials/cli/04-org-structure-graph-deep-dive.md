# Tutorial 4: Org Structure - Search Method Deep Dive

Project: Map organizational relationships with searching
Time: 20 minutes

## What You'll Build

- Create workspace for organizational data
- Upload organizational structure document
- Use structured search to find relationships
- Compare structured search vs concept search on same data
- Query hierarchies and connections

## Setup

Verify services running:

```bash
task health-check
```

## Step 1: Understanding This Tutorial

This tutorial shows a different way to search: instead of finding related concepts, this
method finds exact relationships. You'll see how it excels at hierarchy
and connection questions.

## Step 2: Create Organization Workspace

Create workspace for org structure:

```bash
task cli -- workspace create
```

When prompted:

```
Workspace name: Organization Structure
Workspace description: Company hierarchy and team relationships
```

Output:

```
Workspace created successfully
ID: 4
Name: Organization Structure
Description: Company hierarchy and team relationships
Created: 2025-12-07T10:45:00
```

## Step 3: Create Sample Organization Data

Save as org-structure.txt:

```
Company Organization Structure

Executive Leadership:
Alice Johnson - CEO, reports directly to Board
Alice Johnson manages: Bob Chen (VP Engineering), Carol Smith (VP Sales), Dan Wilson (VP Operations)

Engineering Department:
Bob Chen - VP Engineering, reports to Alice Johnson
Bob Chen manages: Elena Rodriguez (Engineering Manager), Frank Lee (Engineering Manager)
Elena Rodriguez manages: Grace Park (Senior Engineer), Hank Davis (Senior Engineer)
Frank Lee manages: Ivy Chen (Senior Engineer), Jack Wilson (Senior Engineer)

Sales Department:
Carol Smith - VP Sales, reports to Alice Johnson
Carol Smith manages: Kelly Johnson (Sales Manager), Liam Murphy (Sales Manager)
Kelly Johnson manages: Monica Brown (Sales Rep), Nathan Blake (Sales Rep)
Liam Murphy manages: Oliver Chen (Sales Rep), Patricia Davis (Sales Rep)

Operations Department:
Dan Wilson - VP Operations, reports to Alice Johnson
Dan Wilson manages: Quinn Smith (Operations Manager), Rachel Garcia (Operations Manager)
Quinn Smith manages: Samuel Johnson (Operations Coordinator), Teresa Wilson (Operations Coordinator)
Rachel Garcia manages: Ulysses Martinez (Operations Coordinator), Victoria Lee (Operations Coordinator)

Cross-Functional Teams:
Product Strategy Team: includes Bob Chen (Engineering), Carol Smith (Sales), Dan Wilson (Operations)
Quality Assurance Team: includes Elena Rodriguez, Frank Lee, Grace Park, Hank Davis
Customer Success Team: includes Kelly Johnson, Liam Murphy, Quinn Smith, Rachel Garcia
```

## Step 4: Select Organization Workspace

Activate the workspace:

```bash
task cli -- workspace select
```

Choose "Organization Structure".

Output:

```
Workspace selected: Organization Structure
```

## Step 5: Upload Organization Data

Upload as a structured search to find relationships:

```bash
task cli -- document add org-structure.txt graph
```

Output:

```
Document added successfully
ID: doc_009
Name: org-structure.txt
Type: graph
Processed entities: 24
Processed relationships: 31
Indexed: true
```

The document is now processed and ready to search for relationships and hierarchies.

## Step 6: Create Organization Chat

Create chat for querying the org structure:

```bash
task cli -- chat create
```

When prompted:

```
Session name: Org Queries
Session description: Find people, teams, and reporting relationships
```

Output:

```
Chat session created successfully
ID: session_006
Name: Org Queries
Workspace: Organization Structure
```

## Step 7: Finding Direct Relationships

This search method excels at finding exact connections.

Query 1 - Direct report:

```bash
task cli -- chat message "Who does Bob Chen report to?"
```

Output:

```
Session: Org Queries
User: Who does Bob Chen report to?

Response:
Bob Chen (VP Engineering) reports directly to Alice Johnson (CEO).

Sources:
- org-structure.txt (direct match)
```

The search found the exact relationship immediately.

Query 2 - Direct manager:

```bash
task cli -- chat message "Who manages Elena Rodriguez?"
```

Output:

```
Session: Org Queries
User: Who manages Elena Rodriguez?

Response:
Elena Rodriguez is managed by Bob Chen, who is the VP Engineering.

Sources:
- org-structure.txt (direct match)
```

The direct relationship was found in the structure.

## Step 8: Finding Chains of Command

This search method can traverse multi-level hierarchies.

Query 3 - Chain of command:

```bash
task cli -- chat message "Who is Grace Park's manager and what is the chain up to CEO?"
```

Output:

```
Session: Org Queries
User: Who is Grace Park's manager and what is the chain up to CEO?

Response:
Grace Park is managed by Elena Rodriguez. Elena Rodriguez reports to Bob Chen.
Bob Chen reports to Alice Johnson (CEO). The full chain is:
Grace Park -> Elena Rodriguez -> Bob Chen -> Alice Johnson

Sources:
- org-structure.txt (hierarchy match)
```

The search traversed the entire hierarchy automatically.

Query 4 - All reports:

```bash
task cli -- chat message "Who reports directly to Carol Smith?"
```

Output:

```
Session: Org Queries
User: Who reports directly to Carol Smith?

Response:
Carol Smith (VP Sales) directly manages:
- Kelly Johnson (Sales Manager)
- Liam Murphy (Sales Manager)

Sources:
- org-structure.txt (direct match)
```

The search found all direct reports from the structure.

## Step 9: Finding Team Members

Query 5 - Team members:

```bash
task cli -- chat message "Who is on the Quality Assurance Team?"
```

Output:

```
Session: Org Queries
User: Who is on the Quality Assurance Team?

Response:
The Quality Assurance Team includes:
- Elena Rodriguez (Engineering Manager)
- Frank Lee (Engineering Manager)
- Grace Park (Senior Engineer)
- Hank Davis (Senior Engineer)

Sources:
- org-structure.txt (team match)
```

The search identified all team members from the structure.

## Step 10: Compare Structured Search vs Concept Search

Test the same data with concept search method to see differences.

Go back and upload the same document as concept search:

```bash
task cli -- document add org-structure.txt concept
```

Output:

```
Document added successfully
ID: doc_010
Name: org-structure.txt (concept)
Type: concept
Processed tokens: 156
Indexed: true
```

Create a concept search chat:

```bash
task cli -- chat create
```

When prompted:

```
Session name: Concept Search Org
Session description: Search org data with concept matching
```

Select the concept search session:

```bash
task cli -- chat select
```

Choose "Concept Search Org".

Ask the same question about reporting:

```bash
task cli -- chat message "Who does Bob Chen report to?"
```

Output:

```
Session: Concept Search Org
User: Who does Bob Chen report to?

Response:
The document contains organizational information about Bob Chen's role as VP
Engineering with responsibilities for managing engineering teams. Alice Johnson
appears to be a senior executive role in the structure based on available
context and placement in the document.

Sources:
- org-structure.txt (match: 0.67)
```

This search method found an answer but with lower confidence. It had to infer from
the general context rather than using exact relationships.

Ask about team membership with concept search:

```bash
task cli -- chat message "Who is on the Quality Assurance Team?"
```

Output:

```
Session: Concept Search Org
User: Who is on the Quality Assurance Team?

Response:
The document mentions a Quality Assurance Team with references to several engineers
and managers. Elena Rodriguez, Frank Lee, Grace Park, and Hank Davis are mentioned
in connection with quality and engineering work.

Sources:
- org-structure.txt (match: 0.72)
```

This search method found the right answer but by inferring from context.

## Step 11: What Structured Search Does Well

Go back to structured search session:

```bash
task cli -- chat select
```

Choose "Org Queries".

Query multi-level relationships:

```bash
task cli -- chat message "What is the full management chain from Monica Brown to CEO?"
```

Output:

```
Session: Org Queries
User: What is the full management chain from Monica Brown to CEO?

Response:
Monica Brown -> Kelly Johnson -> Carol Smith -> Alice Johnson

Chain structure:
- Monica Brown is managed by Kelly Johnson
- Kelly Johnson is managed by Carol Smith
- Carol Smith is managed by Alice Johnson (CEO)

Sources:
- org-structure.txt (hierarchy match)
```

The search traverses hierarchies perfectly by following relationships.

## Step 12: What Structured Search Struggles With

Query about general descriptions:

```bash
task cli -- chat message "What does the Engineering Department do?"
```

Output:

```
Session: Org Queries
User: What does the Engineering Department do?

Response:
The Engineering Department is a structural unit containing several teams and roles.
Primary members include Bob Chen (VP), Elena Rodriguez, Frank Lee, and their direct
reports. The search knows the structure but has limited context about what they do.

Sources:
- org-structure.txt (structure match)
```

This search method knows the structure and people but struggles with descriptive
information without explicit details.

## Testing

Try these queries to see how this search method works:

- Query relationships: who manages whom, who reports to whom - works perfectly.
- Query hierarchies: chains of command, full reporting chains - finds them correctly.
- Query team membership: who is on specific teams - lists all members accurately.
- Try same queries with the other search method to see the differences.

## What You Learned

- How structured search finds exact relationships
- Searching excels at hierarchical and organizational questions
- It finds exact relationships and chains of command perfectly
- It can follow multiple levels of hierarchy
- It struggles with general descriptions and open-ended questions
- Different search methods work better for different types of questions
- When to use structured search vs concept-based search
- How to choose the right search method for your data
