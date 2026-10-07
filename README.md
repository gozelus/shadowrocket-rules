# shadowrocket-rules

自用小火箭（Shadowrocket）分流规则，重点保证 **Claude/Anthropic 全链路走同一代理出口**，避免因直连或出口不一致被误判地区、触发风控。

## 规则列表

### claude.list

```
https://raw.githubusercontent.com/gozelus/shadowrocket-rules/main/claude.list
```

覆盖内容（基于 blackmatrix7/ios_rule_script 与 v2fly/domain-list-community，补全了它们缺失的部分）：

| 类别 | 内容 |
|---|---|
| 官方域名 | anthropic.com / claude.ai / claude.com / claudeusercontent.com / claudemcpclient.com / claudemcpcontent.com / clau.de / claude.dev / 官网 CDN |
| 官网统计 | cdn.usefathom.com |
| 人机验证 | challenges.cloudflare.com（必须与主流量同出口，否则验证循环） |
| 功能开关 | api.statsig.com / events.statsigapi.net / featuregates.org |
| 遥测 | sentry.io / 全部 datadog 机房（DOMAIN-KEYWORD） |

## 导入方法（iPhone 小火箭）

1. 小火箭 → 底部「配置」→ 右上角「+」→「从 URL 下载」→ 粘贴上面的 raw 链接
2. 下载后长按该规则 → 行为选择「**代理**」，策略组/节点选择你**固定使用的那一个**（不要选自动切换）
3. 规则顺序：确保本规则排在去广告规则**上方**

## 小火箭防泄露设置清单

按重要性排序：

1. **FINAL 兜底 = 代理**：配置 → 当前 conf → 滑到底部，`FINAL` 必须指向代理/你的固定策略组，**不能是 DIRECT**。这是防止"新域名没收录就直连"的最后保险。
2. **规则顺序**：GeoIP,CN 在 FINAL 之前是正常配置；Claude 显式规则必须排在 GeoIP 和广告规则之前（本规则导入后检查位置）。
3. **固定节点**：选定一个节点后长期不切换。频繁换 IP/换国家比"IP 在哪个国家"更容易触发风控。
4. **全局路由用「配置」模式**：不要用「代理」全局模式（国内 App 全走海外会触发别的风控），也不要用「直连」。
5. **按需连接保持 VPN 常开**：iOS 设置 → 通用 → VPN 与设备管理 → Shadowrocket → 开启「按需连接」中的蜂窝+Wi-Fi 始终连接，避免打开 Claude App 的瞬间 VPN 未就绪产生直连空窗。
6. **DNS**：保持默认即可。开启代理后域名在远端解析；不要随意改成国内 DNS-over-HTTPS。
7. **场景（Scene）**：如果配过 Wi-Fi/蜂窝不同场景，确认蜂窝网络下规则同样生效（手机端最容易在 5G 下裸奔）。
8. **自动更新规则**：配置 → 订阅的规则 → 开启自动更新（建议每天）。
9. **验证方法**：小火箭首页 →「最近请求」→ 过滤 "claude" / "anthropic"，逐条确认命中的是本规则而非 GeoIP/FINAL，且出口节点与电脑端一致。

## 维护

发现 Anthropic 新域名或新的遥测端点，直接提 commit 补充到 `claude.list` 即可，手机端会自动更新。
