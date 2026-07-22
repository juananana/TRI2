# CC Switch 中转 API 基准报告

测试时间：2026-07-20（Asia/Shanghai）

## 结论

- Codex 首选：`bondai`，实际地址 `https://api.ebondai.com`。
- Claude Code 首选：`claude code`，实际地址同为 `https://api.ebondai.com`。
- 综合唯一推荐：`api.ebondai.com`。它是本次唯一同时通过 Codex 和 Claude Code 实际推理请求的站点。
- `ej2075` 暂作 Codex 备用。旧健康检查很快，但本次自动审核连续遇到 `/responses` 503，无法完成同口径能力测试。
- `lucoo` 和 `CUN.AI` 当前被 Cloudflare 403 拒绝；`api.bondai.cc` 的 Claude Messages 路径返回 404。

## 评分方法

综合分满分 100：可用性 35、回答质量与约束遵循 30、首字延迟 20、价格 15。

失败站点仍保留少量历史健康检查分，但不能把只验证 HTTP 连通的历史检查视为真实推理成功。`ej2075` 未完成同口径测试，因此其分数是保守的暂定分。

## Codex

| 排名 | 中转站 | 综合分 | 实测成功率 | 质量 | 首字中位数 | 结论 |
|---:|---|---:|---:|---:|---:|---|
| 1 | api.ebondai.com | 91 | 3/3 | 3/3 | 4.584 s | 最推荐；稳定、答案全对、价格低 |
| 2 | api.ej2075.com | 58* | 未完成 | 未完成 | 历史约 0.711 s | 快，但近期出现 503，仅作备用 |
| 3 | www.cun.ai | 10 | 0/3 | 0/3 | 无 | 三次均被 Cloudflare 403 拒绝 |
| 4 | apicc.lucoo.net | 8 | 0/3 | 0/3 | 无 | 三次均被 Cloudflare 403 拒绝 |

`api.ebondai.com` 返回模型名 `gpt-5.5`。三题涵盖 Python 状态推理、二分查错和约束排序，全部正确并遵守输出格式。

三次请求余额从 `$6.80316344` 降至 `$6.79945469`，实扣 `$0.00370875`，平均约 `$0.001236/次`。总 usage 为 13,357 input tokens、326 output tokens，其中 11,520 input tokens 标记为缓存命中。按 CC Switch 内置参考价估算约 `$0.02474`，实际扣款约为参考价的 15%。

## Claude Code

| 排名 | 中转站 | 综合分 | 实测成功率 | 严格格式得分 | 首字中位数 | 结论 |
|---:|---|---:|---:|---:|---:|---|
| 1 | api.ebondai.com | 82 | 3/3 | 2/3 | 4.476 s | 唯一可用；答案语义均正确，但一次多输出了解释 |
| 2 | api.bondai.cc | 5 | 0/3 | 0/3 | 无 | `/v1/messages` 三次均返回 404 |
| 3 | apicc.lucoo.net | 3 | 0/3 | 0/3 | 无 | 三次均被 Cloudflare 403 拒绝 |

`api.ebondai.com` 返回模型名 `claude-opus-4-7`。三题内容均答对；第三题要求只返回 JSON，它先输出了一段解释再给 JSON，因此严格工具调用场景扣分。其首字延迟在 2.826 至 7.446 秒之间，波动大于 Codex 路由。

Claude 账号没有可用的余额查询结果，无法直接测出三次请求的实际扣费。按 CC Switch 内置参考价计算，三次共约 `$0.0984`；这只是参考上限，不等于中转实际扣款。

## 建议配置

1. Codex 日常主力使用 `bondai / https://api.ebondai.com`。
2. Claude Code 使用当前名为 `claude code` 的 `https://api.ebondai.com` 配置。
3. Codex 将 `ej2075` 留作备用，不建议在近期 503 未消失前设为唯一主力。
4. 暂停 `lucoo` 和 `CUN.AI`，除非服务商解除 Cloudflare IP/地区限制。
5. `claude code copy / https://api.bondai.cc` 很可能是地址配置错误；若它本来也是 ebondai 账号，应改为服务商文档指定的 Messages API 根地址。

## 限制

- 每个可调用配置只测试了三个短请求，适合筛选，不等于长期稳定性压测。
- API 返回的模型名称只能证明路由声称使用该模型，不能独立证明底层模型未被替换。
- 本次执行环境的网络出口可能与用户其他设备不同；Cloudflare 403 结论适用于当前 Codex/CC Switch 使用路径。
