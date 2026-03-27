# MACRO: Advancing Multi-Reference Image Generation with Structured Long-Context Data

- arXiv: `2603.25319`
- Source URL: <https://www.arxiv.org/src/2603.25319>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.25319.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.25319`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.25319/main.tex`
- Authors: Zhekai Chen, Yuqing Wang, Manyuan Zhang, Xihui Liu

## 摘要总结

这篇文章关注的是多参考图像生成在参考图一多起来就明显退化的问题。作者认为主要瓶颈不是模型本身，而是数据分布太偏向单参考或少参考场景，因此提出 `MACRO` 数据集，包含 400K 样本、每个样本最多 10 张参考图，覆盖 Customization、Illustration、Spatial、Temporal 四类任务，并专门为长上下文多参考生成提供监督。

## 核心 Insight

这篇最强的结论是：多参考生成的瓶颈首先是 structured long-context data。用 `MACRO` 微调后，Bagel 在作者提出的 `MacroBench` 上把平均分拉到 5.71，开源里只落后于两个闭源模型；同时，跨任务联合训练明显优于单任务训练，而 “think-before-generation” 和 collage 这些直觉技巧反而不如直接补对数据和 token selection 来得有效。
