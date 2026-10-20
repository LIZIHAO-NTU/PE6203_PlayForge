# D 公开复现证据

这些都是开发实验，不是正式 S1—S5。

| 文件 | 用途 |
|---|---|
| FLASH_RESULT.md | 自然运行、受控副本与局限，分别说明 |
| flash-runs-summary.json | DeepSeek 超时、Flash-Lite 格式失败、Flash 成功的脱敏历史；不覆盖失败 |
| flash-evidence.json | 成功运行的原始元数据及六份精选原文件，包含 UTF-8 文本与逐文件 SHA-256 |
| pr-validation.json | 本轮 PR 的相关测试、离线复现和零新增模型调用记录 |
| pr-validation.log | 本轮相关验证日志，个人绝对路径已替换 |

flash-evidence.json 中的文件由原始运行按字节核对后收录：summary.json、最终 game/ 两文件、当轮 traces/attempts/01/game/ 两文件、evidence/replay.json。原始运行标识为 d_step_pilot_20261020_03_flash。

审计工具与需求指纹记录在 original_experiment 中；历史工作树列表保留原样，不意味着所有历史未跟踪文档都纳入本 PR。样例游戏代码属于真实生成证据，不会进入正常生成消息。

原始模型请求响应、API key、.env、完整浏览器截图及正式独立验收未纳入公开文件。不会把缺失正文的指纹当作正文已公开。完整本机证据另行留档，审查者无需模型 API 即可复算精选记录的审计结论。

从仓库根目录：

```sh
python -B -m evals.step_evidence_replay --output reports/d_public_reaudit_new
```

每次使用新输出目录。新工具只校验文件与记录，不在生成路径中调用；日志一致不证明真实规则正确，也不能独立认证恶意伪造的日志。
