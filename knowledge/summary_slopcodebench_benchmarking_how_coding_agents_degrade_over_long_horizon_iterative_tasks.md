# SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks

- arXiv: `2603.24755`
- Source URL: <https://www.arxiv.org/src/2603.24755>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.24755.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.24755`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.24755/main.tex`
- Authors: Gabriel Orlanski, Devjeet Roy, Alexander Yun, Changho Shin, Alex Gu, Albert Ge, Dyah Adila, Frederic Sala, Aws Albarghouthi

## 摘要总结

Software development is iterative, yet agentic coding benchmarks overwhelmingly evaluate single-shot solutions against complete specifications. Code can pass the test suite but become progressively harder to extend. Recent iterative benchmarks attempt to close this gap, but constrain the agent's design decisions too tightly to faithfully measure how code quality shapes future extensions.

## 核心 Insight

Across 11 models and 20 iterative problems, no agent solves a problem end-to-end. Verbosity rises in 90% of trajectories, erosion appears in 80%, and both trends diverge sharply from well-maintained human repositories over time. 这篇 benchmark 的价值在于把“能不能一次写对”换成了“能不能持续演化而不把代码库改坏”。
