# ChatGPT Desktop 桌宠 Wayland 修复

为 Umbriel 上的 ChatGPT Desktop 内置桌宠修复透明窗口模糊、拖动和点击穿透。鼠标停在编辑或语音按钮上时保持展开。云端宠物素材刷新时保留上一张图片，等新图片解码完成后切换。

在 Arch Linux、Umbriel、单显示器 2× 缩放环境使用。26.1111.21308 上已有桌宠交互反馈，26.1111.71025 上已验证补丁构建、安装和重复执行。新版交互、多显示器和空闲后素材切换的实际效果尚未完整验证。

## Arch Linux 持久安装

需要 pacman 安装的 `chatgpt-desktop`、Python 3、Node.js 和 util-linux（`flock`）。完整退出客户端，在仓库目录执行以下命令。如果此前手动打过补丁且尚未安装钩子，先通过包管理器重装当前版本，恢复原版归档。

```sh
set -e
lib=/usr/local/lib/wayland-chatgpt-pet-fix
sudo install -d "$lib" /etc/pacman.d/hooks
sudo install -m 644 patch.py hover.js sprite-refresh.js "$lib/"
sudo install -m 755 apply-installed "$lib/"
sudo install -m 644 95-wayland-chatgpt-pet.hook /etc/pacman.d/hooks/
sudo "$lib/apply-installed"
```

将 `pet-rule.toml` 的内容放在 `~/.config/umbriel/config.toml` 的通用窗口规则之后。如果已有同名桌宠规则，请替换旧段。运行 `umbriel config validate`，成功后打开客户端和桌宠。运行 `umbriel windows` 可查看窗口标题 `Codex Pet Overlay`。

pacman 安装或升级客户端后会触发钩子，yay 和 paru 调用 pacman 安装软件包时同样生效。补丁按代码特征查找目标，遇到不兼容的更新会报错并保留新版本的原始归档。运行中的客户端需完整退出并重新打开才能加载改动。

## 卸载

完整退出客户端，删除钩子，然后通过包管理器重装当前版本的 `chatgpt-desktop`，并从 Umbriel 配置中移除桌宠规则。

```sh
sudo rm -f /etc/pacman.d/hooks/95-wayland-chatgpt-pet.hook
```

如需离线恢复，可先运行 `sha256sum --check /var/lib/wayland-chatgpt-pet-fix/installed.sha256`。仅当校验通过时，才用同目录的 `original.asar` 恢复 `/usr/lib/chatgpt/resources/app.asar`。
