# Vega: Learning to Drive with Natural Language Instructions

- arXiv: `2603.25741`
- Source URL: <https://www.arxiv.org/src/2603.25741>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.25741.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.25741`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.25741/main.tex`
- Authors: Sicheng Zuo, Yuxuan Li, Wenzhao Zheng, Zheng Zhu, Jie Zhou, Jiwen Lu

## 摘要总结

这篇论文试图把自动驾驶从“模仿驾驶”推进到“可听指令驾驶”。作者构建了 `InstructScene`，包含约 100K 条带自然语言指令的驾驶场景和轨迹，并提出统一的 `Vega` 模型，用 autoregressive 模块处理视觉与语言，用 diffusion 模块生成未来图像和动作轨迹。

## 核心 Insight

这篇的关键不只是“把语言塞进驾驶模型”，而是把 future image prediction 当成 dense supervision 来补足 action supervision 太稀疏的问题。论文实验表明，直接训练 VLA 规划头在 instruction-following 上很差，但加入未来帧预测后，模型能更好地学习指令、动作和视觉后果之间的因果关系，并在 NAVSIM v2 上做到接近或达到 SOTA。
