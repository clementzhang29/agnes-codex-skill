---
name: agnes
description: Generate images and videos through the Agnes OpenAI-compatible API. Use when the user asks Codex to create, edit, or automate chat validation, image generation, or video generation with Agnes models, Agnes API keys, Agnes APIHub endpoints, or the $agnes skill.
---

# Agnes

Use Agnes through the OpenAI-compatible API at `https://apihub.agnes-ai.com/v1`.

Known model IDs from the tested Agnes account:

- Chat: `agnes-2.0-flash`
- Image: `agnes-image-2.0-flash`
- Video: `agnes-video-v2.0`

## Safety

- Never hardcode or print API keys. Read the key from `AGNES_API_KEY`.
- If a user provides a key in chat, recommend rotating it and ask them to set the rotated key as an environment variable.
- Store generated media in the user's requested output directory. If none is given, use the current task's `outputs/` directory when available.
- Follow active policy instructions before creating images or videos involving real people, copyrighted characters, logos, or sensitive content.

## Quick Start

Set the key for the current shell session:

```powershell
$env:AGNES_API_KEY = "<your-agnes-key>"
```

Run from this skill folder:

```powershell
python .\scripts\agnes_generate.py chat --prompt "Say hello from Agnes" --model agnes-2.0-flash
python .\scripts\agnes_generate.py image --prompt "A cinematic product photo of a glass teapot on a walnut table" --model agnes-image-2.0-flash --download-dir outputs
python .\scripts\agnes_generate.py video-create --prompt "Slow push-in on a moonlit lake, mist moving over the water" --model agnes-video-v2.0 --poll --download-dir outputs
```

On macOS/Linux:

```bash
export AGNES_API_KEY="<your-agnes-key>"
python scripts/agnes_generate.py chat --prompt "Say hello from Agnes" --model agnes-2.0-flash
```

## Workflow

1. Clarify the desired task: chat/model validation, image generation, or video generation.
2. Choose a model. Prefer `agnes-2.0-flash`, `agnes-image-2.0-flash`, or `agnes-video-v2.0` unless the user provides another model.
3. Set `AGNES_API_KEY` for the current shell session if it is missing.
4. Run `scripts/agnes_generate.py`.
5. Return the saved media path and a short note about the model/settings used.

## Commands

Use `chat` for `POST /chat/completions`:

```powershell
python .\scripts\agnes_generate.py chat --prompt "Reply with one short sentence." --model agnes-2.0-flash
```

Use `image` for `POST /images/generations`:

```powershell
python .\scripts\agnes_generate.py image --prompt "A neon city street after rain" --model agnes-image-2.0-flash --download-dir outputs
```

Use `video-create` for `POST /videos`; add `--poll` to wait for completion:

```powershell
python .\scripts\agnes_generate.py video-create --prompt "Moonlit lake with slow camera push-in" --model agnes-video-v2.0 --seconds 5 --poll --download-dir outputs
```

Use `video-get <id>` to fetch a previously created video task.

## Troubleshooting

- `AGNES_API_KEY is not set`: set the environment variable in the current terminal.
- `model_not_found`: call `/models` or use one of the known model IDs above.
- `401` or `403`: verify the key, billing, model access, and Base URL.
- `404`: confirm the endpoint and model name against the Agnes docs.
- Long-running video tasks: poll with a longer timeout, or return the task id to the user so they can resume later with `video-get`.

Read `references/api.md` for raw endpoint examples.
