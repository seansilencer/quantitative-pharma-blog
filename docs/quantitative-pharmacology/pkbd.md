# PK/PD 关联分析

## 概念

PK/PD 建模链接药物暴露（Pharmacokinetics）与药效响应（Pharmacodynamics），建立定量关系，为给药方案优化提供依据。

## 经典模型

### Emax 模型
$$E = E_0 + \frac{E_{max} \cdot C}{EC_{50} + C}$$

适用于：浓度-效应呈平滑饱和曲线的关系（如多数小分子药物）

### Sigmoid Emax
$$E = E_0 + \frac{E_{max} \cdot C^γ}{EC_{50}^γ + C^γ}$$

适用于：陡峭的浓度-效应曲线（如抗肿瘤药物细胞杀伤）

### 间接响应模型
适用于：效应通过内源性物质调控的疾病（如炎症、血糖调节）

## 临床应用

- **抗菌药物**：PK/PD 靶值（fAUC/MIC, fCmax/MIC）指导给药
- **抗肿瘤**：AUC/IC50 与 ORR/DOR 关联建模
- **免疫治疗**：暴露量-毒性/疗效关系

[→ 查看全部 PK/PD 文献](/articles/index.html)