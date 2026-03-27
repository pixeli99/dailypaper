# Less Gaussians, Texture More: 4K Feed-Forward Textured Splatting

- arXiv: `2603.25745`
- Source URL: <https://www.arxiv.org/src/2603.25745>
- Cached archive: `/Users/pixeli/.cache/nanochat/knowledge/2603.25745.tar.gz`
- Extracted source: `/Users/pixeli/.cache/nanochat/knowledge/2603.25745`
- Entrypoint: `/Users/pixeli/.cache/nanochat/knowledge/2603.25745/main.tex`
- Authors: Yixing Lao, Xuyang Bai, Xiaoyang Wu, Nuoyuan Yan, Zixin Luo, Tian Fang, Jean-Daniel Nahmias, Yanghai Tsin, Shiwei Li, Hengshuang Zhao

## 摘要总结

这篇工作指出 feed-forward 3D Gaussian Splatting 在分辨率升高时会因为 primitive 数量近似平方增长而失去可扩展性，因此 4K 合成几乎不可做。作者提出 `LGTM`，思路是减少 Gaussian 数量，把更多高频细节转移到 texture 表达上，从而突破高分辨率瓶颈。

## 核心 Insight

这篇最值得记住的不是具体模块名，而是表达分工的变化：Gaussian 负责几何和粗结构，texture 负责细节。这样可以在不线性堆 primitive 的前提下把分辨率继续往上推，对想做高分辨率实时 3D 表达的人来说，这是比“再加更多 splats”更健康的方向。
