# shadowrocket-rules

自用小火箭（Shadowrocket）配置，重点保证 **Claude/Anthropic 全链路走同一代理出口**，避免因直连或出口不一致被误判地区、触发风控。

## 一键导入（推荐）

小火箭 → 底部「配置」→ 右上角「+」→「从 URL 下载…」→ 粘贴：

```
https://cdn.jsdelivr.net/gh/gozelus/shadowrocket-rules@main/claude-guard.conf
```

（如果上面这个下载失败，备用 GitHub 直连：`https://raw.githubusercontent.com/gozelus/shadowrocket-rules/main/claude-guard.conf`）

下载完成后：在「配置」页点击 `claude-guard.conf` → 弹出菜单选「**使用配置**」。

这个 conf 做了什么：

- Claude/Anthropic 全部官方域名、官网统计、Cloudflare 人机验证、Statsig 功能开关、Sentry/Datadog 遥测 → 全部 PROXY
- `GEOIP,CN,DIRECT`：国内流量直连
- `FINAL,PROXY`：其余全部走代理——Anthropic 以后上新域名也不会裸奔
- 不含任何节点和策略组：`PROXY` = 你在**首页选中的那个节点**，选定后请不要切换

只想要规则、不想换配置的，也可以单独订阅规则文件 `claude.list`（配置 → 编辑配置 → 规则 → 右上角 + → 类型选 RULE-SET，填入 raw 链接，行为选 PROXY）。

## 导入后的设置清单（按顺序做一遍）

1. **选固定节点**：「首页」节点列表里点击你要长期用的那条节点（出现 ✓）。以后不要来回换，频繁换 IP 是最大风控信号。
2. **全局路由 = 配置**：「首页」顶部「全局路由」→ 选「配置」。不要用「代理」（全局），更不要用「直连」。
3. **确认规则生效**：「配置」→ 点 conf 右侧 ⓘ →「编辑配置」→「规则」，应能看到 17 条 Claude 相关规则排在 `GEOIP,CN` 之前。
4. **VPN 常开，消灭空窗**：iOS「设置」→ 通用 → VPN 与设备管理 → 点 Shadowrocket 右侧 ⓘ → 打开「按需连接」，把 Wi-Fi 和蜂窝都设为始终连接（不同 iOS 版本入口可能是：设置 → VPN → ⓘ → 按需连接）。这步保证打开 Claude App 的瞬间 VPN 已在跑，不会产生直连空窗。
5. **蜂窝网络同样生效**：如果你配置过「场景」，确认 5G/蜂窝场景下用的也是这个 conf。
6. **更新配置**：以后我更新规则，你在「配置」页**左滑** `claude-guard.conf` →「更新」即可拉最新版。

## 验收（2 分钟）

1. 关掉 Wi-Fi 只用 5G，浏览器开 `ipinfo.io`，确认是日本（或你选定节点的）IP
2. 打开 Claude App 发条消息
3. 回小火箭 →「首页」→「最近请求」→ 过滤 "claude" / "anthropic"：每条都应命中 `claude-guard` 的规则走 PROXY，**不允许出现任何一条 DIRECT**
