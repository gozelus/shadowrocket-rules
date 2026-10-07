# 上游来源

基础为 Johnshall/Shadowrocket-ADBlock-Rules-Forever 的 `lazy_group.conf`，上游同步自 LOWERTOP/Shadowrocket。

- 固定提交：`2f31bf1f400277c149ae875eacfb0cc1ceb45439`
- 原文：https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/2f31bf1f400277c149ae875eacfb0cc1ceb45439/lazy_group.conf
- SHA-256：`56e3576a2fb8d0462383ddf4575822c7c018da3b09801377b97ea9909e816bab`

本地差异：16 条优先规则；默认及备用 DNS 经 PROXY 的 Cloudflare DoH；节点域名使用独立的阿里 DoH 引导解析；移除 Apple/iCloud 的系统 DNS 覆写；AI 仅保留 PROXY；规则策略名与分组名大小写一致；Apple/WeChat/Global/China 使用 Shadowrocket 格式；显式关闭 MITM。其余分流及地区组保留。

配置只在本仓库更新时改变，未安装自动跟随上游的定时任务；远程 RULE-SET 仍由原维护者更新。共享 Sentry/Datadog/Cloudflare 域名的分流会影响其他使用这些服务的应用。
