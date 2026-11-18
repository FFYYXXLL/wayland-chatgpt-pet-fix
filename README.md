# ChatGPT Desktop 桌宠 Wayland 修复

针对 **Umbriel + ChatGPT Desktop 26.1111.21308（Linux Owl 运行时）** 的本地补丁。保留内置桌宠、动画、语音和编辑按钮。给桌宠独立窗口标题和透明悬浮规则，按工作区坐标拖动，并将按钮及其展开过程覆盖的范围加入 Wayland 输入区域。透明背景允许点击下层应用。

在 Arch Linux、Umbriel 和 2× 缩放的单显示器上使用。窗口适配仅在 Umbriel Wayland 会话启用。其他桌面环境、多显示器和其他客户端版本尚未验证。

## 安装

需要 Python 3 和 Node.js。完整退出 ChatGPT Desktop，在本仓库目录运行。以下命令使用 Arch 软件包的安装目录，生成补丁需要约 750 MiB 可用空间。

```sh
set -e
resources=/usr/lib/chatgpt/resources
python3 patch.py "$resources/app.asar" ./pet-patched.asar
sudo ln "$resources/app.asar" "$resources/app.asar.before-wayland-pet"
sudo install -m 644 ./pet-patched.asar "$resources/app.asar.wayland-new"
sudo mv -T "$resources/app.asar.wayland-new" "$resources/app.asar"
```

将 `pet-rule.toml` 中的规则放在 `~/.config/umbriel/config.toml` 的通用窗口规则之后。如果已有匹配桌宠标题的旧规则，请替换该段。运行 `umbriel config validate`，成功后重新打开客户端和桌宠。可用 `umbriel windows` 检查桌宠标题是否为 `Codex Pet Overlay`。

## 恢复

完整退出客户端。若仍是安装补丁时的同一软件包版本，运行以下命令，再撤销添加的桌宠规则并重开客户端。

```sh
sudo mv -T /usr/lib/chatgpt/resources/app.asar.before-wayland-pet /usr/lib/chatgpt/resources/app.asar
```

软件包升级可能覆盖补丁。升级后应使用对应软件包的原版文件，避免恢复旧版本归档。仓库仅包含补丁生成器、悬停逻辑和窗口规则。
