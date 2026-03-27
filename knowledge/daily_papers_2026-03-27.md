# Hugging Face Daily Papers 2026-03-27

## 今日偏好相关

- 更贴近你当前偏好的有 3 篇：`Intern-S1-Pro`（超大规模 MoE / 科学多模态）、`MACRO`（多参考图像生成，偏 diffusion 生态）、`MSA`（超长上下文 memory）。
- 今天没有特别直接的 `diffusion language model` 论文，但 `MACRO` 和 `Vega` 都属于“生成模型作为监督或核心模块”的路线，值得跟进。

## Intern-S1-Pro: Scientific Multimodal Foundation Model at Trillion Scale

- arXiv: `2603.25040`
- 本地 note: `knowledge/summary_intern_s1_pro_scientific_multimodal_foundation_model_at_trillion_scale.md`
- 摘要总结：这是一篇 1T 参数科学多模态基础模型报告，目标是把通用多模态能力和科学专用能力合到同一个系统里。论文不只是做参数堆叠，还强调通过 expert expansion 和 grouped routing 把超大规模 MoE 训练做稳，并配合 6T token 的科学多模态续训数据来提升 chemistry、materials、life science、earth science 等垂类能力。
- 核心 insight：这篇最值得看的点不是“又一个更大的模型”，而是它把“Specializable Generalist”讲得很明确，即先保住通用模型能力，再用架构和数据把科学专长做深。如果你关心 MoE，这篇值得跟，因为 grouped routing + expert expansion 是它能上到 trillion scale 的关键工程点。

## MACRO: Advancing Multi-Reference Image Generation with Structured Long-Context Data

- arXiv: `2603.25319`
- 本地 note: `knowledge/summary_macro_advancing_multi_reference_image_generation_with_structured_long_context_data.md`
- 摘要总结：这篇论文认为多参考图像生成长期做不好的主要原因不是模型不会“想”，而是训练数据缺少真正的长上下文多参考监督。作者构建了 `MACRO` 数据集，含 400K 样本、每个样本最多 10 张参考图，覆盖 Customization、Illustration、Spatial、Temporal 四类任务；同时给出 4K 样本的 `MacroBench` 来评估不同参考数和任务维度下的生成一致性。
- 核心 insight：这篇的信号很强，瓶颈主要在 data，而不只是 architecture。实验里，用 `MACRO` 微调后的 Bagel 在多参考生成上明显提升，平均分做到 5.71，开源里只输闭源的 Nano Banana Pro 和 GPT-Image-1.5，而且在 Spatial 上甚至能超过 Nano Banana Pro；另外 “think-before-generation” 和 collage proxy 这两种直觉型技巧都不如直接补高质量多参考数据有效。

## SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks

- arXiv: `2603.24755`
- 本地 note: `knowledge/summary_slopcodebench_benchmarking_how_coding_agents_degrade_over_long_horizon_iterative_tasks.md`
- 摘要总结：这篇 benchmark 不是测 coding agent 一次性写出能跑代码，而是看它在多轮迭代开发里会不会把代码库越改越“烂”。作者设计了 20 个长程迭代任务，对 11 个模型进行评测，重点考察扩展性退化、代码臃肿和结构侵蚀。
- 核心 insight：结果很直接，没有任何 agent 能端到端完成所有迭代任务，而且 90% 轨迹里代码会越来越 verbose，80% 会出现结构 erosion。对做 agent evaluation 的人来说，这篇很重要，因为它指出“测试通过”不等于“代码还可维护”。

## MSA: Memory Sparse Attention for Efficient End-to-End Memory Model Scaling to 100M Tokens

- arXiv: `2603.23516`
- 本地 note: `knowledge/summary_msa_memory_sparse_attention_for_efficient_end_to_end_memory_model_scaling_to_100m_tokens.md`
- 摘要总结：这篇工作试图把 memory capacity 和 reasoning 能力解耦，用稀疏注意力、document-wise RoPE、KV cache 压缩和 memory parallel，把 end-to-end memory model 的规模拉到 100M tokens。它在九个 long-context QA benchmark 和 RULER NIAH 上都做了评测。
- 核心 insight：论文最强的点不是单一指标，而是 scaling 稳定性。作者报告模型从 16K 扩到 100M tokens 只出现约 8.8% 的性能退化，并在 1M-token 的 NIAH 里保持 94.84% 准确率。对长上下文研究来说，这篇比单纯做 window extension 更像是在做“memory operating system”。

## Voxtral TTS

- arXiv: `2603.25551`
- 本地 note: `knowledge/summary_voxtral_tts.md`
- 摘要总结：Mistral 这篇 TTS 论文用 hybrid 架构把语义和声学 token 分开处理，语义 token 用 autoregressive 生成，声学 token 用 flow matching 生成，并配套一个自研的 `Voxtral Codec`。模型只需要 3 秒参考音频就能做零样本 voice cloning。
- 核心 insight：这篇值得注意的地方是“AR 管语义，FM 管声学”的拆分非常实用，兼顾自然度、表达力和推理延迟。作者的人评里，Voxtral TTS 在多语言 voice cloning 上对 ElevenLabs Flash v2.5 的总体胜率是 68.4%，说明 flow matching 在语音侧已经进入很强的实用区间。

## Less Gaussians, Texture More: 4K Feed-Forward Textured Splatting

- arXiv: `2603.25745`
- 本地 note: `knowledge/summary_less_gaussians_texture_more_4k_feed_forward_textured_splatting.md`
- 摘要总结：这篇针对 feed-forward 3D Gaussian Splatting 在高分辨率下 primitive 数量随分辨率平方增长的问题，提出 `LGTM`，核心思路是少放 Gaussian、多依赖 texture 表达，从而把 4K synthesis 做成可行。
- 核心 insight：它的主要贡献不是更复杂的渲染器，而是把高分辨率表达从“堆更多点”改成“点负责几何，纹理负责细节”，这是一个更可扩展的 factorization。对高分辨率 3DGS 来说，这是很自然但也很关键的一步。

## Vega: Learning to Drive with Natural Language Instructions

- arXiv: `2603.25741`
- 本地 note: `knowledge/summary_vega_learning_to_drive_with_natural_language_instructions.md`
- 摘要总结：这篇工作想把自动驾驶从 imitation driving 推到 instruction-based driving。作者先构建了 `InstructScene`，包含约 100K 条带自然语言驾驶指令的场景和轨迹；再提出 `Vega`，用 AR 处理视觉和语言，用 diffusion 生成未来图像与动作轨迹，在一个统一的 vision-language-world-action 框架里联合训练。
- 核心 insight：最重要的点是 future image prediction 在这里不是附加任务，而是 dense supervision，负责把高维视觉语言条件和低维 action 之间的监督信号补足。论文实验显示，直接训 VLA 规划头效果很差，但加上 future frame prediction 后，NAVSIM v2 可做到 86.9 EPDMS，而且 best-of-N 后达到 SOTA。
