# D：通过结论的逐步执行证据审计

本 PR 只增加独立评估工具、测试、开发样例和复现证据，不修改 agent/ 或自动接入生产门禁。基于团队共同开发基线 `4cabc9faf01c859a0d5ee45110c1c624df94e544`；不是正式冻结版。

## 技术问题和方法

当测试报告 passed=true 时，冻结计划中的操作与观察是否完整记录，步骤、参数、准备／检查阶段和结果是否一致？工具读取每轮 replay.json，逐步核对动作，重算所支持的断言比较，并核验计划与当轮源码指纹。失败项保持非通过，不把未执行尾部补成成功；没有浏览器清单标为未验证。

在有完整通过项的记录副本上，分别删除输入、删除观察、保留通过标记但把动作设为失败、重复动作、修改动作参数。对比旧门禁与独立审计。副本不改变游戏、原计划、原记录或原成绩，不计为真实模型错误。

## 入口与复现（仓库根目录）

先按项目 README 安装 Python 3.10+ 和 requirements.txt。本轮实际为 Python 3.14.3、Playwright 1.63.0、Chromium 153.0.8010.12（Darwin arm64）。Windows 可将 python 替换为自己的虚拟环境解释器路径。

### 零 API、零浏览器：复现随包真实记录审计

```sh
python -B -m evals.step_evidence_replay --output reports/d_published_reaudit_new
```

输出必须为不存在的新目录。入口读取 docs/d_step_evidence/flash-evidence.json，逐项校验原文件哈希后恢复六份精选原文件，在新目录生成审计。证据只用作评估，不是生成器读取的游戏模板。没有原始 API 正文、密钥或正式 S1—S5 答案。

预期：1 份清单；6 项记录支持通过；计划／当轮游戏指纹一致；5 种受控异常检出。部分原轨迹文件（API 正文、截图等）未公开，因此复制件的文件总清单短于本机完整原报告；不要求整份 AUDIT.json 逐字相同。

### 零 API：审计其他已有运行

```sh
python -B -m evals.step_evidence audit runs/EXISTING_RUN/run --output reports/d_audit_new
```

这只读取给定运行，不生成游戏、不启动浏览器、不改写原成绩。原运行需 summary.json 和 traces/attempts/*/evidence/replay.json；当轮 game/ 应与 evidence/ 同级。输出不能覆盖既有目录。

### 校准与回归

```sh
python -B -m unittest discover -s tests -p 'test_step_evidence*.py' -v
```

三项真实浏览器校准默认跳过，启用 MVP_BROWSER_TESTS=1 并安装 Playwright Chromium 后再运行同一命令。使用已安装 Edge 时按项目说明设置 PLAYWRIGHT_CHANNEL=msedge。浏览器校准使用合成夹具，零模型 API，不是新的自主生成样本。最新本轮提交验证见 d_step_evidence/pr-validation.json。提交期间 main 合入 C 的聚焦修复后，另在 main c414c91＋D 文件的隔离组合上复核了 23 项相关测试（含浏览器）和 334 项默认回归（284 通过、50 跳过）；这不等于正式候选冻结。

### 可选真实生成（会调用 API，不是复现已有记录的必要步骤）

```sh
python -B -m evals.step_evidence live --output runs/d_live_new --max-calls 3 --max-rounds 3 --max-seconds 360
```

该开发试跑入口明确限制为 OpenRouter，读取本地忽略的 .env：LLM_API_KEY、LLM_BASE_URL=https://openrouter.ai/api/v1、自己的 LLM_MODEL。非 DeepSeek 服务的 LLM_THINKING 通常留空，JSON 输出与模型能力保持一致。成功历史模型为 google/gemini-2.5-flash，不代表老师最终模型。不要提交 .env 或密钥。

调用、轮数和时间上限不等于金额上限；格式与传输重试占调用预算。不会自动重开第二次实验。当前 PR 准备与验证不增加真实模型调用。

## 证据与结论

真实生成历史和受控副本结果见 [结果说明](d_step_evidence/FLASH_RESULT.md)，精选原文件见 [证据索引](d_step_evidence/README.md)，三次运行的脱敏历史见 flash-runs-summary.json。

一次成功生成的自然记录为 6 场景、46 步、32 条观察，审计完整一致；原状态 automated_passed_manual_pending，不是完整验收。五类副本异常均被审计识别，旧门禁仍接受副本通过标记；这揭示可补强的独立核对边界，不证明正常执行器实际伪造过记录。

局限：单个简单开发题、一次成功生成；未触发自然修复循环。记录一致不认证浏览器物理事件，不防恶意执行器伪造，不证明预期规则或完整玩法正确。审计应与独立验收并列使用。C 已在组内反馈复核；该 PR 仍待 GitHub 非作者审查及 A 的集成决定，暂不修改共享生产门禁。
