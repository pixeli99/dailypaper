# Fast-WAM: Do World Action Models Need Test-time Future Imagination?

- arXiv: `2603.16666`
- Source URL: <https://www.arxiv.org/src/2603.16666>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.16666.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.16666`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.16666/main.tex`
- Read basis: TeX source, not PDF
- Read date: `2026-03-25`
- Local repo context: `/Users/pixeli/paper_WU` 当前只有 `knowledge/` 笔记，没有现成代码或实验管线可直接映射

## Thesis

这篇文章讨论的不是“怎样把 WAM 做得更重”，而是反过来问一个更基础的问题：

`World Action Model` 的收益，到底主要来自

- 训练时加入了视频建模目标；
- 还是推理时真的去“想象未来视频”。

作者的核心结论是：

很多 WAM 的价值主要来自训练阶段的视频共训练，让模型学到更好的物理和交互表征；而测试时显式生成未来视频，并不是性能提升的主要来源。

基于这个判断，作者提出 `Fast-WAM`：

- 训练时保留视频建模；
- 推理时不再生成未来视频；
- 直接从当前观测的 latent world representation 预测动作。

这样做把 WAM 的接口变得更像普通 policy / VLA，但又保留了 world modeling 带来的表征优势。

## Method

### 1. 问题重写

传统 WAM 常写成：

`p(a | o, l) = ∫ p(v | o, l) p(a | o, l, v) dv`

也就是先预测未来视觉，再根据这个“未来”出动作。

Fast-WAM 的做法是把这个流程改成：

`p(a | o, l) = p(a | z(o, l))`

其中 `z(o, l)` 是由视频骨干网络编码出来的 world representation，但它在测试时不是通过未来视频采样得到，而是通过一次前向传播直接得到。

### 2. 模型结构

Fast-WAM 用的是基于 `Wan2.2-5B` 的视频 `DiT` 作为 world backbone，并复用它的：

- 视频 `VAE`
- 文本编码器 `T5`
- 视频扩散主干

在此基础上再加一个动作专家 `DiT`，整体组织成 `Mixture-of-Transformer (MoT)`：

- 视频分支负责 world modeling；
- 动作分支负责动作 chunk 生成；
- 两者共享 attention 机制，但通过精心设计的 attention mask 控制信息流。

输入 token 分三类：

- 第一帧观测的 clean latent tokens
- 未来视频帧的 noisy latent tokens，仅训练时存在
- 动作 tokens

关键设计点是：

- 动作 token 可以看当前观测 anchor；
- 动作 token 不能看未来视频 token；
- 第一帧 anchor 本身不被其他 token 反向污染。

这保证了训练时视频目标能塑造 backbone，但不会让动作分支在训练里偷看未来信息。

### 3. 训练与推理

训练目标是 joint flow matching：

- `L_act` 用于动作 chunk
- `L_vid` 用于未来视频 latent
- 总损失是 `L = L_act + λ L_vid`

推理时的变化非常直接：

- 删掉未来视频分支
- 只保留第一帧 clean latent
- 视频 backbone 单次前向得到 latent world features
- 动作 expert 再做动作生成

所以 Fast-WAM 避免了 imagine-then-execute WAM 常见的迭代视频去噪过程。

### 4. 受控对照变体

为了回答“收益究竟来自哪里”，作者做了三个强相关变体：

- `Fast-WAM`
  训练有视频共训练，测试不想象未来
- `Fast-WAM-Joint`
  动作和未来视频一起去噪，对应 joint-generation 风格 WAM
- `Fast-WAM-IDM`
  先生成未来视频，再根据视频预测动作，对应 video-then-action 风格 WAM
- `Fast-WAM w.o. video co-train`
  架构和推理流程不变，但训练时拿掉视频目标

这个对照是论文最关键的地方，因为它把“训练时视频目标”和“测试时未来想象”拆开了。

## Evidence

### 1. 仿真基准

在 `RoboTwin 2.0` 上：

- `Fast-WAM`: `91.8%`
- `Fast-WAM-Joint`: `90.6%`
- `Fast-WAM-IDM`: `91.3%`
- `Fast-WAM w.o. video co-train`: `83.8%`

这里最重要的不是 Fast-WAM 是否绝对第一，而是：

- 不做测试时 future imagination，性能几乎没掉；
- 但去掉训练时视频共训练，掉了接近 `8` 个点。

在 `LIBERO` 上也是同样趋势：

- `Fast-WAM`: `97.6%`
- `Fast-WAM-Joint`: `98.5%`
- `Fast-WAM-IDM`: `98.0%`
- `Fast-WAM w.o. video co-train`: `93.5%`

也就是说，测试时是否真的生成未来视频，影响小于训练时有没有视频建模目标。

### 2. 真实机器人结果

作者还做了真实世界的毛巾折叠任务。

论文文字里给出的重点结论是：

- 在 Fast-WAM 家族里，几种带视频共训练的方法整体表现接近；
- 去掉视频共训练后，成功率直接掉到 `10%`；
- Fast-WAM 的推理延迟只有 `190 ms`；
- `Fast-WAM-IDM` 延迟达到 `810 ms`。

因此这篇文章的经验结论很明确：

- 视频共训练对真实任务很重要；
- 测试时显式未来想象的额外收益有限；
- 但它带来的延迟代价非常真实。

## Limitations

这篇文章也有几处需要保留判断。

- 它主要是在已有 WAM 范式上做设计消融和归因分析，不是提出一个全新的 embodied learning 原理。
- 论文大量依赖 `Wan2.2-5B` 这一强视频生成骨干，所以结论有一定 backbone 依赖性。
- 实验重点是“是否需要 test-time imagination”，不是系统探索更轻量 backbone、不同数据规模、不同动作表示的完整设计空间。
- 真实世界评测只展示了一个代表性长时程任务，泛化范围仍有限。
- 作者自己也承认，后续需要研究更大规模预训练数据和模型 scaling 对这一结论的影响。

## Relevance to this repo

当前 `/Users/pixeli/paper_WU` 只有论文笔记，没有机器人代码、训练框架或评测脚本，因此我没法把 Fast-WAM 直接映射到现有模块。

但如果这个仓库后续是打算积累 embodied / world model 阅读笔记，这篇文章的价值很明确：

- 它提供了一个很好的判断标准：不要默认“会想象未来”就一定更好；
- 评估 WAM 时，要把“训练目标收益”和“推理流程收益”分开看；
- 对实际部署，延迟和控制闭环速度可能比额外一点想象能力更重要。

## Concrete ideas to try here

如果你后面要把这篇论文转成实现方向，我会优先保留这几个实验问题：

- 先做一个 ablation 框架，明确比较
  `video co-train + no imagination`
  对比
  `video co-train + imagination`
  以及
  `no video co-train`
- 优先测 latency / control frequency，而不是只看最终 success rate
- 如果 backbone 很强，先验证视频目标是否主要在训练期提供表征增益，而不是默认推理期 rollout 必不可少
- 对真实任务特别关注长时程闭环操作，因为论文里最强信号就是“视频共训练提高数据效率，但 test-time imagination 很贵”

## Open questions

- 如果 backbone 不是强视频生成模型，这个结论还能否成立？
- 在更复杂的需要显式规划或多步前瞻的任务里，test-time imagination 会不会重新变得重要？
- 如果把视频目标换成更便宜的时序表征学习目标，能否保留 Fast-WAM 的收益但进一步降低训练成本？
- 这篇工作没有深入回答：视频共训练到底学到了什么类型的 world representation，为什么它能显著提升动作学习？
