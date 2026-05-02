# PBPK 生理药代动力学建模

## 概念

生理药代动力学（Physiologically-Based Pharmacokinetics, PBPK）模型通过整合：
- **生理参数**：器官体积、血流量、通透性
- **药物参数**：分配系数、代谢速率、酶/转运体动力学

来预测药物在全身各组织中的浓度-时间曲线。

## 建模流程

1. **文献检索**：收集生理参数和药物的体外数据
2. **模型构建**：在 SimCYP, GastroPlus, PK-Sim 等平台搭建生理模型
3. **参数优化**：用临床数据验证模型
4. **场景模拟**：儿科外推、DDI、特殊人群等
5. **监管提交**：按 FDA PBPK 指南整理报告

## 软件工具

| 平台 | 厂商 | 特点 |
|------|------|------|
| SimCYP | Certara | 全球最广泛用于制药监管申报 |
| GastroPlus | Simulations Plus | 口服制剂吸收建模强 |
| PK-Sim | Open Systems Pharmacology | 开源友好，器官级生理模型 |
| MoBot | MDIC | 社区驱动，入门友好 |

## 最新文献

> 本节内容由 tools/update_blog.py 自动更新

[→ 查看全部 PBPK 文献](../articles/index.md)