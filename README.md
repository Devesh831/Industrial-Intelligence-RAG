# Data Science Internship Assignment

The project combines cyclone sensor analysis (`Task1`) and a local PDF question-answering prototype (`Task2`). The local submission includes the final presentation and derived analyses. Supplied files and data-derived outputs are private and excluded from Git; obtain authorized input files before running the public code.

Create a Python environment, install `pip install -r requirements.txt`, then follow `Task1/README.md` and `Task2/prototype/README.md`. The first task uses a five-minute grid, proxy shutdown rule, K-means, state-specific Isolation Forests and chronological 12-step forecast evaluation. The second indexes PDF pages using MiniLM embeddings and Chroma, and generates responses with FLAN-T5-small. The scripts use free tools and make no API calls to paid models; model weights are downloaded on first use.

The shutdown labels, event hypotheses and citations require human verification. The small generation model may produce poor or unsupported answers; the RAG prototype is not a safety-critical operational system. Tests exercise event segmentation and retrieval guardrails, but do not replace labeled operational validation.
