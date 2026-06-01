# Agnes API Reference

Agnes exposes an OpenAI-compatible API.

- Base URL: `https://apihub.agnes-ai.com/v1`
- Authentication: `Authorization: Bearer $AGNES_API_KEY`
- Model list: `GET /models`
- Chat completions: `POST /chat/completions`
- Image generation: `POST /images/generations`
- Video task creation: `POST /videos`
- Video task retrieval: `GET /videos/{id}`

## Tested Model IDs

- Chat: `agnes-2.0-flash`
- Image: `agnes-image-2.0-flash`
- Video: `agnes-video-v2.0`

## Chat Request

```bash
curl https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-2.0-flash",
    "messages": [
      {"role": "user", "content": "Say hello from Agnes"}
    ]
  }'
```

## Image Request

```bash
curl https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-image-2.0-flash",
    "prompt": "A cinematic product photo of a glass teapot on a walnut table",
    "size": "1024x1024"
  }'
```

## Video Request

```bash
curl https://apihub.agnes-ai.com/v1/videos \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agnes-video-v2.0",
    "prompt": "Slow push-in on a moonlit lake, mist moving over the water",
    "seconds": "5"
  }'
```

Then retrieve the task:

```bash
curl https://apihub.agnes-ai.com/v1/videos/<task-id> \
  -H "Authorization: Bearer $AGNES_API_KEY"
```

The exact model names and optional parameters can change. If a request fails with a model or parameter error, call `GET /models` and adjust the payload.
