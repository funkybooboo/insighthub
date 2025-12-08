# Tutorial 3: Research Papers - Search Method Deep Dive

Project: Analyze research abstracts with searching
Time: 20 minutes

## What You'll Build

- Create workspace for research papers
- Upload 2 paper abstracts
- Compare search strengths and limitations
- See how searching finds related concepts
- Test queries that work well vs poorly with searching

## Setup

Verify services running:

```bash
task health-check
```

## Step 1: Understanding This Tutorial

This tutorial shows you how the system finds information in documents. You'll see how it
finds answers even when you use different words, and also when it struggles with specific
facts and numbers.

## Step 2: Create Research Workspace

Create workspace for papers:

```bash
task cli -- workspace create
```

When prompted:

```
Workspace name: Research Papers
Workspace description: Academic papers and abstracts for analysis
```

Output:

```
Workspace created successfully
ID: 3
Name: Research Papers
Description: Academic papers and abstracts for analysis
Created: 2025-12-07T10:30:00
```

## Step 3: Create Sample Research Papers

Document 1 - Save as paper1-abstract.txt:

```
Deep Learning for Image Recognition

Abstract: Convolutional Neural Networks (CNNs) have revolutionized computer vision.
Modern architectures like ResNet and EfficientNet achieve superhuman performance on
image classification tasks. Transfer learning enables rapid adaptation to new domains.
We present a novel attention mechanism that improves accuracy by 3-5% on standard
benchmarks. The method uses residual connections to allow gradient flow through very
deep networks. Batch normalization accelerates training and improves convergence.
Our experiments show that models trained with our technique generalize better to
unseen data and require fewer parameters than baseline approaches.
```

Document 2 - Save as paper2-abstract.txt:

```
Natural Language Processing with Transformers

Abstract: Transformer models have become the foundation of modern NLP systems. These
models use self-attention mechanisms to capture relationships between words regardless
of distance. Unlike RNNs, transformers enable parallel processing of sequences. We
introduce a novel positional encoding scheme that reduces position bias in the model.
Experiments on machine translation, question answering, and sentiment analysis show
consistent improvements. The attention weights reveal which parts of the input the
model focuses on. Fine-tuning pretrained models on downstream tasks achieves strong
results with limited data. Token processing combined with position information create
rich representations for downstream processing.
```

## Step 4: Select Research Workspace

Activate the workspace:

```bash
task cli -- workspace select
```

Choose "Research Papers".

Output:

```
Workspace selected: Research Papers
```

## Step 5: Upload Research Papers

Upload both abstracts for searching:

```bash
task cli -- document add paper1-abstract.txt vector
```

Output:

```
Document added successfully
ID: doc_007
Name: paper1-abstract.txt
Type: vector
Processed tokens: 102
```

```bash
task cli -- document add paper2-abstract.txt vector
```

Output:

```
Document added successfully
ID: doc_008
Name: paper2-abstract.txt
Type: vector
Processed tokens: 98
```

Both papers indexed.

## Step 6: Create Analysis Chat

Create chat session for research analysis:

```bash
task cli -- chat create
```

When prompted:

```
Session name: Paper Analysis
Session description: Searching and concept analysis
```

Output:

```
Chat session created successfully
ID: session_005
Name: Paper Analysis
Workspace: Research Papers
```

## Step 7: When Search Works Well - Conceptual Matching

The search works best when looking for related concepts even if you use different words.

Query 1 - Concept similarity:

```bash
task cli -- chat message "What methods improve neural network training?"
```

Output:

```
Session: Paper Analysis
User: What methods improve neural network training?

Response:
Several techniques mentioned in the papers improve neural network training. Batch
normalization accelerates training and improves convergence. Residual connections
allow gradient flow through deep networks. Self-attention mechanisms capture
relationships in sequences. Transfer learning enables rapid adaptation by reusing
pretrained models on new tasks.

Sources:
- paper1-abstract.txt (match: 0.89)
- paper2-abstract.txt (match: 0.76)
```

The search found both papers by understanding meaning, not just matching exact words.

Query 2 - Related concepts:

```bash
task cli -- chat message "How can we process data in parallel?"
```

Output:

```
Session: Paper Analysis
User: How can we process data in parallel?

Response:
Transformer models enable parallel processing of sequences, unlike RNNs which
process sequentially. The attention mechanism allows each position to directly
interact with all other positions without sequential dependencies. This parallel
processing capability is one of the key advantages of transformer architectures
for NLP tasks.

Sources:
- paper2-abstract.txt (match: 0.83)
```

The search found relevant information even without exact phrase matching.

Query 3 - Cross-domain concepts:

```bash
task cli -- chat message "How do representation methods help organize information?"
```

Output:

```
Session: Paper Analysis
User: How do representation methods help organize information?

Response:
Text and images are converted into processed information. Token processing in
transformers combines with positional information to create rich representations.
Image processing in CNNs capture hierarchical features. These processed representations
enable downstream processing and comparison of how similar items are.

Sources:
- paper1-abstract.txt (match: 0.79)
- paper2-abstract.txt (match: 0.81)
```

The search found both papers because they both discuss this concept.

## Step 8: When Search Struggles - Exact Facts and Numbers

The search has limitations when looking for specific numbers or exact details.

Query 4 - Exact number:

```bash
task cli -- chat message "What is the exact percentage improvement?"
```

Output:

```
Session: Paper Analysis
User: What is the exact percentage improvement?

Response:
The papers mention that a novel attention mechanism improves accuracy by 3-5% on
standard benchmarks. However, the search may miss other specific metrics not
explicitly matching this query.

Sources:
- paper1-abstract.txt (match: 0.71)
```

The search found an answer but with lower confidence when looking for specific numbers.

Query 5 - Unusual wording:

```bash
task cli -- chat message "What specifically do RNNs do that transformers do not?"
```

Output:

```
Session: Paper Analysis
User: What specifically do RNNs do that transformers do not?

Response:
The documents mention that transformers enable parallel processing of sequences,
unlike RNNs which process sequentially. This is the main structural difference
highlighted in the materials.

Sources:
- paper2-abstract.txt (match: 0.68)
```

The search found an answer but with lower confidence when questions are worded differently.

## Step 9: Search Works Well For - Conceptual Topics

```bash
task cli -- chat message "Explain attention mechanisms"
```

Output:

```
Session: Paper Analysis
User: Explain attention mechanisms

Response:
Attention mechanisms are central to modern deep learning. Self-attention in transformers
captures relationships between all positions in a sequence regardless of distance.
Attention weights reveal which input parts the model focuses on. A novel attention
mechanism is also presented for improving CNN accuracy. Attention enables models to
dynamically weight the importance of different inputs.

Sources:
- paper2-abstract.txt (match: 0.92)
- paper1-abstract.txt (match: 0.71)
```

Strong matches because attention is discussed in both papers.

## Step 10: Search Works Poorly For - Specific Details

```bash
task cli -- chat message "How many benchmark datasets were tested?"
```

Output:

```
Session: Paper Analysis
User: How many benchmark datasets were tested?

Response:
The documents mention experiments on various tasks including image classification,
machine translation, question answering, and sentiment analysis. However, the exact
number of datasets tested is not clearly specified in these abstracts.

Sources:
- paper2-abstract.txt (match: 0.55)
```

Low confidence because the search looks for concepts, not specific details.

## Testing

Try asking questions to see these patterns:

- Ask about methods and techniques - you'll get high confidence matches.
- Ask about specific numbers - you'll get lower confidence or miss details.
- Ask about related concepts with different words - it works well.
- Ask for obscure specific facts - the search may struggle.

## What You Learned

- Searching works best for finding related concepts and ideas
- Searching finds answers even when you use different words
- Searching struggles with exact numbers and specific facts
- Different questions get different confidence scores
- When searching works well and when it struggles
- How to ask questions effectively to get good results
