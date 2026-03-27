# MSA: Memory Sparse Attention for Efficient End-to-End Memory Model Scaling to 100M Tokens

- arXiv: `2603.23516`
- Source URL: <https://www.arxiv.org/src/2603.23516>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.23516.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.23516`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.23516/neurips_2024.tex`
- Authors: Yu Chen, Runkai Chen, Sheng Yi, Xinda Zhao, Xiaohong Li, Jianjin Zhang, Jun Sun, Chuanrui Hu, Yunyun Han, Lidong Bing, Yafeng Deng, Tianqiao Chen

## 摘要总结

Long-term memory is a cornerstone of human intelligence. Enabling AI to process lifetime-scale information, reaching hundreds of millions of tokens, remains a long-standing pursuit in the field. Due to the constraints of full-attention architectures, the effective context length of large language models (LLMs) is typically limited to 1M tokens.

## 核心 Insight

We introduce MSA, a scalable sparse‑attention framework augmented with document‑wise RoPE and KV‑cache compression that extends end‑to‑end modeling to lifetime‑scale contexts, paired with Memory Parallel for fast 100M tokens processing and Memory Interleave for robust multi‑hop reasoning across distributed memory segments. On long‑context QA and Needle‑in‑a‑Haystack benchmarks, MSA surpasses mainstream state‑of‑the‑art general‑purpose LLMs while preserving retrieval fidelity and reasoning depth, with KV‑cache compression further reducing memory footprint and latency.
