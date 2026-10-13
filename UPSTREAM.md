# 来源与转换边界

最初 0.0.0.1 基于 Johnshall/Shadowrocket-ADBlock-Rules-Forever 的 lazy_group.conf，固定提交 2f31bf1f400277c149ae875eacfb0cc1ceb45439，文件 SHA-256 为 56e3576a2fb8d0462383ddf4575822c7c018da3b09801377b97ea9909e816bab。配置格式与部分参数沿用该来源；参见仓库 LICENSE。

0.0.0.2 重写分流，不再引用那套服务列表。rules/*.list 从用户当前 Mihomo 已使用的 geosite.dat、geoip.dat 提取，仅选择 CN/private/apple/microsoft/github/github-copilot 分类数据，不读取代理凭据、日志或浏览记录。输入文件与输出文件哈希见 rules/manifest.json。快照不是自动更新；不宣称来源版本与网络上最新数据库一致。

Protobuf 格式：
https://github.com/v2fly/v2ray-core/blob/master/app/router/routercommon/common.proto

参考语法及 UI 说明（社区维护，非 Shadowrocket 官方保证）：
https://github.com/LOWERTOP/Shadowrocket

- PROTOCOL 只嵌套在逻辑规则中；IPv4、IPv6 各一条全地址 UDP 拒绝。
- 节点 A 的“代理通过”选择 B，路径为客户端 → B → A → 网站。
- close-if-proxy-chain-missing 只控制代理链中转丢失，不等于关闭 VPN 后的系统级防直连。
- private 的一条正则无法确认等价语法，明确省略并记录，不用猜测的规则替代。

所有规则数据保持原有上游权利；本仓库的配置改写和说明继续遵循既有 CC BY-SA 4.0 许可。

GitHub/Copilot 显式例外还参考以下服务方端点说明：
https://docs.github.com/en/copilot/reference/copilot-allowlist-reference
https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-requirements

GitHub 的 default.exp-tas.com 是共享实验服务，因此该域名全部走代理。Microsoft Copilot 仅补充 copilot.microsoft.com、copilot.cloud.microsoft、m365copilot.com；不把所有微软认证或 Microsoft 365 域名都代理。
