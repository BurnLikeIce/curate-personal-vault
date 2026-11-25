# curate-personal-vault

An Agent Skill for turning project work into useful notes and preserving recoverable versions of personal work in a user-selected Obsidian vault.

这份技能帮你把项目决策、验收经验、个人贡献和代表作沉淀到自己的 Obsidian 知识库。GitHub 仓库里放技能说明和归档脚本，每位使用者在自己的电脑上配置知识库。Codex、Cursor 和 GitHub Copilot 可以使用同一份本地库。

## 安装

下载或克隆本仓库，把含有 [SKILL.md](SKILL.md) 和 [scripts](scripts/) 的 `curate-personal-vault` 文件夹放入助手支持的技能位置。下面是可用的本地个人技能位置。

| 助手 | 个人技能目录 |
| --- | --- |
| Codex | `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` |

Cursor 和 Copilot 的加载方式见 [Cursor Agent Skills](https://cursor.com/docs/skills) 和 [GitHub Copilot Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)。

给助手的本地个人规则加上一句话，把示例路径改成你的实际位置：

> 我的 Obsidian 知识库位于 <知识库绝对路径>。我明确要求整理，或在已授权的项目工作中遇到值得长期保留的经验和个人作品时，使用 curate-personal-vault 更新这份库。

第一次用时可以点名技能，例如“用 curate-personal-vault 整理这次项目里的关键决定，附上交接入口”。需要直接写入的助手应能访问该目录。换电脑后更新这条本地规则里的路径。

## 归档一个作品版本

笔记整理直接读写 Markdown。可选的作品归档脚本使用 Python 3 标准库，安装技能时无需额外装依赖。从技能目录运行：

```powershell
python scripts/archive_version.py save --vault "D:/Notes/MyVault" --project "示例项目" --version v1 "成品.zip" "源码.zip"
python scripts/archive_version.py verify "D:/Notes/MyVault/作品/示例项目/v1"
```

脚本默认保存到 `作品/<项目>/<版本>/`。已有库想沿用 `Works` 时，可以在保存时加 `--works-dir Works`，核对路径也用 `Works`。重复保存同样的版本及内容会复用已校验的文件，遇到同版本的不同内容会提示确认新版本。
