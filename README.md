# Agnes Codex Skill

[中文](#中文) | [English](#english)

## 中文

Agnes Codex Skill 是一个用于在 Codex 中调用 Agnes AI API 的技能包。它支持通过 Agnes 的 OpenAI-Compatible API 进行模型连通性测试、图片生成和视频生成。

### 项目功能

- 调用 Agnes 聊天模型，验证 API Key、Base URL 和模型是否可用。
- 使用 `agnes-image-2.0-flash` 生成图片，并自动下载返回的图片文件。
- 使用 `agnes-video-v2.0` 创建视频任务，支持轮询任务状态并下载完成的视频。
- 支持自定义模型、尺寸、时长、种子、额外 JSON 参数等。
- 不保存 API Key，只从环境变量 `AGNES_API_KEY` 读取。

### 解决的问题

很多 Agent 或本地开发工具虽然支持 OpenAI-Compatible API，但图片、视频任务常常需要不同的端点、模型名称和轮询逻辑。这个 skill 把 Agnes 的常用调用方式封装成可复用脚本，让 Codex 可以更稳定地完成：

- 快速测试 Agnes key 是否有效。
- 快速确认账号可用模型。
- 从自然语言提示词生成图片。
- 创建视频任务并等待结果。
- 把生成结果保存到本地输出目录。

### 安装

1. 下载或克隆本仓库。
2. 将 `agnes` 文件夹复制到 Codex skills 目录：

Windows:

```powershell
Copy-Item -Recurse .\agnes "$env:USERPROFILE\.codex\skills\agnes"
```

macOS/Linux:

```bash
mkdir -p ~/.codex/skills
cp -R agnes ~/.codex/skills/agnes
```

3. 重启 Codex 或新开一个 Codex 线程。

### 配置 Agnes API Key

PowerShell:

```powershell
$env:AGNES_API_KEY = "你的 Agnes API Key"
```

macOS/Linux:

```bash
export AGNES_API_KEY="你的 Agnes API Key"
```

不要把 API Key 写进仓库、README、脚本或聊天记录。建议只通过环境变量传入。

### 如何获取 Agnes Key

1. 打开 Agnes AI 官网：[https://agnes-ai.com](https://agnes-ai.com)
2. 登录或注册账号。
3. 进入控制台、API、开发者或 Key 管理页面。
4. 创建新的 API Key。
5. 复制 key，并在本地通过 `AGNES_API_KEY` 环境变量使用。

如果你已经在聊天或公开页面暴露过 key，建议立刻在 Agnes 控制台删除或轮换旧 key。

### 使用方法

在 Codex 中直接调用：

```text
$agnes 用 Agnes 生成一张赛博朋克城市夜景图片
```

也可以直接运行脚本。

测试聊天模型：

```powershell
python .\agnes\scripts\agnes_generate.py chat --prompt "Say hello from Agnes" --model agnes-2.0-flash
```

生成图片：

```powershell
python .\agnes\scripts\agnes_generate.py image --prompt "一张电影感玻璃茶壶产品摄影" --model agnes-image-2.0-flash --download-dir outputs
```

生成视频：

```powershell
python .\agnes\scripts\agnes_generate.py video-create --prompt "月光下的湖面，薄雾缓慢移动，镜头缓慢推进" --model agnes-video-v2.0 --seconds 5 --poll --download-dir outputs
```

### 默认模型

- Chat: `agnes-2.0-flash`
- Image: `agnes-image-2.0-flash`
- Video: `agnes-video-v2.0`

可用模型可能会随 Agnes 账号权限变化。遇到 `model_not_found` 时，请先确认账号权限和模型列表。

---

## English

Agnes Codex Skill is a Codex skill package for calling the Agnes AI API. It supports model connectivity checks, image generation, and video generation through Agnes's OpenAI-compatible API.

### Features

- Call Agnes chat models to verify API key, base URL, and model availability.
- Generate images with `agnes-image-2.0-flash` and download returned image files automatically.
- Create video tasks with `agnes-video-v2.0`, poll task status, and download completed videos.
- Support custom models, size, duration, seed, and extra JSON parameters.
- Keep API keys out of files. The script reads credentials only from `AGNES_API_KEY`.

### What It Solves

Many local agents and developer tools support OpenAI-compatible APIs, but image and video generation often require separate endpoints, model names, and polling logic. This skill wraps common Agnes workflows into a reusable helper so Codex can reliably:

- Test whether an Agnes API key works.
- Confirm available models for an account.
- Generate images from natural language prompts.
- Create video generation tasks and wait for results.
- Save generated files into a local output directory.

### Installation

1. Download or clone this repository.
2. Copy the `agnes` folder into your Codex skills directory:

Windows:

```powershell
Copy-Item -Recurse .\agnes "$env:USERPROFILE\.codex\skills\agnes"
```

macOS/Linux:

```bash
mkdir -p ~/.codex/skills
cp -R agnes ~/.codex/skills/agnes
```

3. Restart Codex or open a new Codex thread.

### Configure Agnes API Key

PowerShell:

```powershell
$env:AGNES_API_KEY = "your Agnes API key"
```

macOS/Linux:

```bash
export AGNES_API_KEY="your Agnes API key"
```

Do not commit your API key to the repository, README, scripts, or chat logs. Use environment variables instead.

### How To Get An Agnes Key

1. Visit the Agnes AI website: [https://agnes-ai.com](https://agnes-ai.com)
2. Sign in or create an account.
3. Open the console, API, developer, or key management page.
4. Create a new API key.
5. Copy the key and use it locally through the `AGNES_API_KEY` environment variable.

If a key has ever been exposed in chat or a public page, revoke or rotate it in the Agnes console.

### Usage

Invoke the skill in Codex:

```text
$agnes Generate a cyberpunk city image with Agnes.
```

You can also run the helper script directly.

Test the chat model:

```powershell
python .\agnes\scripts\agnes_generate.py chat --prompt "Say hello from Agnes" --model agnes-2.0-flash
```

Generate an image:

```powershell
python .\agnes\scripts\agnes_generate.py image --prompt "A cinematic product photo of a glass teapot" --model agnes-image-2.0-flash --download-dir outputs
```

Generate a video:

```powershell
python .\agnes\scripts\agnes_generate.py video-create --prompt "Moonlit lake with drifting mist and a slow camera push-in" --model agnes-video-v2.0 --seconds 5 --poll --download-dir outputs
```

### Default Models

- Chat: `agnes-2.0-flash`
- Image: `agnes-image-2.0-flash`
- Video: `agnes-video-v2.0`

Available models may depend on your Agnes account permissions. If you see `model_not_found`, check your account access and model list first.
