# Shadowrocket 配置（2.2.92）

在 [Johnshall 的社区懒人配置](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 上补充 Claude 分流和 DNS 隐私设置，保留 Google、Twitter、YouTube、Telegram 等原有规则。版本 `0.0.0.1`，来源与差异见 [UPSTREAM.md](UPSTREAM.md)，变更见 [更新记录](CHANGELOG.md)。没有附带节点、账号、密码或证书。

## 导入

先保留手机上原来的配置，以便切回。完整配置地址：

```
https://gozelus.github.io/shadowrocket-rules/claude-guard-2.2.92.conf
```

1. 首页选择你已有的一个可用节点，打开连接。若下载超时，暂时把首页「全局路由」设为「代理」，再重试；下载和编译结束后恢复「配置」。
2. 底部「配置」→ 右上角「+」→ 粘贴上面的 URL →「下载」。不需要寻找另一个叫“从 URL 下载”的子菜单。
3. 点击下载的 `claude-guard-2.2.92.conf` →「使用配置」。等待远程规则集加载完成。本文件仍引用社区 RULE-SET，需要手机能够通过现有节点访问 GitHub raw。
4. 首页「全局路由」设为「配置」，保持连接开启。下载成功不等于已经选用，确认该配置有选中标记。

备用完整配置地址（内容相同）：

```
https://raw.githubusercontent.com/gozelus/shadowrocket-rules/main/claude-guard-2.2.92.conf
```

不要从“下载配置”入口导入 `claude.list`：它只是规则集。旧的 jsDelivr `@main` 地址存在旧版本缓存，本次不使用。

## 必须检查的设置

以下路径参考上游配置维护者的 [使用手册](https://github.com/LOWERTOP/Shadowrocket)，针对 2.2.92 整理；手机显示不同则以实际界面核对，不能把文档当成手机已验收。

| 位置 | 操作 |
|---|---|
| 首页 → 节点列表 | 选择一个具体节点。Claude 使用期间保持它不变。|
| 配置 → 当前文件右侧 ⓘ → 代理分组 → AI | 应只有 `PROXY`，即跟随首页当前节点，不选择地区自动测速组。关闭“测试并选择最快服务器”。|
| 设置 → 按需求连接 | 开「始终开启」，关「睡眠时断开」；不依赖访问 Claude 域名才触发连接。|
| 设置 → UDP | 开「禁用 STUN」。它可能影响 WebRTC 通话，通话异常时单独排查。|
| 设置 → 隧道 | 开「强制路由」和「包括所有网络」。本地网络、APNs、蜂窝服务的子项先保持原状；本地设备、通知和通话也要做回归检查。|
| 首页 → 全局路由 | 正常使用选「配置」；确认场景、自动切换或回退没有改变当前节点/路由模式。|
| 配置 → 当前文件右侧 ⓘ → HTTPS 解密 | 保持关闭，本配置不需要安装 CA 证书。|

“始终开启”用于自动恢复连接，不等同于经过验证的系统级断网保护。“包括所有网络”也存在系统服务例外；手动关闭 VPN 后，本配置不能继续保护应用流量。

## 本次实际修改

- 16 条优先规则指向 AI，包括已列出的 Claude/Anthropic 域名，以及 Cloudflare 验证、Statsig、Sentry、Datadog 等共享服务域名。共享服务分流也会影响其他应用。
- AI 组仅保留手动 `PROXY`，不再包含地区自动测速组。其他社区分流组保留。
- 默认和备用 DNS 都使用经默认节点转发的 Cloudflare DoH；备用 DNS 不留空，也不回退 `system`。移除 Apple/iCloud 的系统 DNS 覆写。
- `proxy-dns-server` 单独用阿里 DoH 解析**代理节点自身的域名**，避免“先连代理才能解析代理地址”的循环。这是明确的引导解析例外，不能称为所有 DNS 都出境。
- 保留 `udp-policy-not-supported-behaviour = REJECT`，不支持 UDP 的节点不会因此回退直连；保留 IPv6 支持，必须在实际蜂窝网络验收。
- 策略名与分组名大小写统一；将混用的 QuantumultX 列表改为同维护者的 Shadowrocket 格式；显式关闭 MITM。

规则在自上而下匹配；`FINAL,PROXY` 只处理此前没有命中的请求，不覆盖前面的 DIRECT 规则。这些设置不能证明封号原因，也不保证账号不受限制。

## 手机验收

1. 数据 → 代理 → 开启日志记录；数据 → DNS 查看 DNS 记录。不要启用 HTTPS 解密。
2. 先连 Wi-Fi，打开 Claude 做一次普通请求；在代理日志中检查 Claude/Anthropic 和相关遥测连接的策略及实际节点。
3. 关 Wi-Fi 改用蜂窝网络，再重复一次。分别查看出口 IP，并在 Safari 做 DNS/WebRTC 检测；Mac 的测试结果不能替代手机。
4. 锁屏后唤醒、Wi-Fi/蜂窝切换，再确认连接与日志。区分“节点失效但 VPN 仍开着”和“手动关闭 VPN”，后者不属于本配置能兜住的场景。
5. 若规则集下载失败、DNS 回到系统解析、Claude 连接出现 DIRECT，或节点意外变化，暂不标记验收完成。提供相关一条日志即可，勿发送节点订阅链接、凭证或完整敏感日志。

本仓库已做静态配置校验；手机导入、规则编译、DNS 路径与断连行为仍须实机验证。

## 更新与回退

点击配置文件 →「更新配置」拉取新版。该动作会覆盖对文件的本地修改。需回退时，重新选用此前保留的配置；全局设置（始终开启、隧道、STUN）不会随配置切换自动恢复。

配置本身没有自动同步上游的任务；远程 RULE-SET 由原作者维护。维护者修改后运行 `python3 scripts/verify.py`，通过后再发布。
