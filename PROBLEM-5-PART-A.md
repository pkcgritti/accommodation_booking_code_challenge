# ML Add-on (Problem #5) — Part A
---
## System description (Q1)

Built and operated a mobile-optimized facial-clustering pipeline for iOS,
consisting of: Face Detection → Landmark Detection → Face Alignment → Face
Embedding → Clustering clustering. The system organized user photo libraries
entirely on-device, with accuracy comparable to ArcFace-ResNet50 but at ~50% of
the compute cost.

---
## My exact role and ownership (Q2)

Owned the full ML lifecycle as the Machine Learning Engineer & MLOps lead,
including architecture design, PyTorch training, Bayesian hyperparameter search
(W&B), and preparation of deployment artifacts in ONNX and, for the
face-embedding model, CoreML with integer quantization. I also handled mobile
integration constraints, ensuring the pipeline executed efficiently on-device
using the Apple GPU when available, or falling back to CPU when the runtime
elected not to use the GPU, while maintaining stable performance across the
supported iOS hardware range

---
## Traffic characteristics (Q3)

The system typically processed hundreds to thousands of photos per user
session, running in parallel batches of 8–16 images. Average per-image cost had
to remain <30–50ms per stage. Concurrency was mostly intra-session: heavy
bursts during first-time album organization, followed by smaller incremental
runs on new photos.

---
## Infrastructure / compute (Q4)

Training was distributed across multiple environments: a local RTX 4090, the
Apple GPU on macOS, cloud A100 instances, and rented 3080/3090/4080/4090 GPUs
via Vast.ai for large-scale sweeps. Inference followed the deployment strategy
described in Q2, using ONNX and CoreML-integer-optimized models running on the
Apple GPU when available or falling back to CPU. Memory constraints on iOS
required careful control of intermediate tensors, and the batching strategy
remained the same: all stages except the MTCNN-based face detector were fully
parallelized in small batches for stable on-device performance.

---
## Key bottlenecks / production incidents (Q5)

The initial bottleneck was the face embedder, whose original architecture was
too heavy for real-time iOS execution. After I redesigned and trained a
significantly smaller, optimized embedding model (ONNX/CoreML-int8), the
embedding stage became fast enough that the face detector then emerged as the
dominant latency source. From that point, the remaining bottlenecks were
addressed by batch-parallelizing all downstream stages (alignment, embedding,
clustering) and optimizing incremental clustering approach for very large
albums, resulting in a fully smooth, stutter-free pipeline across supported
devices.

---
## Observability & monitoring (Q6)

We used Weights & Biases for experiment tracking and as our model repository;
drift monitoring was unnecessary because the data universe was static. For
production observability, we built internal metric-logging tools using Mixpanel
and BigQuery to track per-stage latency, request volume, number of clusters,
average intra-cluster distance, and other structural indicators of pipeline
behavior. Because the system relied on one-shot learning + unsupervised
clustering, we had no live ground-truth accuracy signal; instead, we maintained
an internal curated dataset for periodic offline evaluation of clustering
quality and regression testing.

---
## What I would do differently (Q7)

• Replace the MTCNN-style detector we used initially with a
  RetinaFace/FPN-based model to enable full batch parallelization and remove
  the sequential bottleneck.
• Implement a fully incremental clustering algorithm (e.g., HDBSCAN-streaming
  or a centroid-merge strategy) to eliminate large recomputations.

---

