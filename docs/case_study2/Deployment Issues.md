---
sidebar_label: Deployment Issues
sidebar_position: 5
---
# Deployment Hickups and Issues

I keep saying I'm not a developer. And it shows.

Deploying this thing locally wasn't smooth, to say the least. Here are some major issues I ran into with my RTX 4080 16GB.

### Resource Starvation (OOM Errors)

Running both a Multimodal VLM (like LLaVA via Ollama) and an ASR engine (Whisper) locally is extremely compute-heavy.

- **The Issue:** I tried to load both models into memory simultaneously. Even on a machine with 16GB of VRAM (GPU memory) and 48GB of RAM, I had random OOM errors on Ollama.
    
- **The Fix:** The immediate fix was to use smaller quantized LLM models and the "base" or "small" versions of Whisper. But ultimately I had to make sure n8n ran these processes in sequence rather than parallel. I also gave up on Ollama and moved directly to using llama_server.cpp, which seems to be more efficient on resource management.
    

### **2. Docker Networking Headaches**

Running these services in separate Docker containers was a huge milestone for me. But getting separate containers to to talk to each other in Linux wasn't as easy.

- **The Issue:** By default, an n8n container cannot reach an Ollama instance running on your host machine via `localhost:11434` because `localhost` inside the container refers to the container itself.
    
- **The Fix:** I used Docker's internal networking (`host.docker.internal`) in the n8n HTTP request nodes to route traffic out of the container and onto the local machine. Honestly I'm not sure if this is the best solution.
    

### **3. Timeouts and Long Polling**

Local AI inference is relatively slow compared to cloud APIs. This can probably be optimized if you know what you're doing.

Which I don't.

- **The Issue:** n8n HTTP Request nodes have default timeout limits. If the local Ollama instance takes 45 seconds to analyze a complex image and n8n's node times out at 30 seconds, the workflow will fail even though Ollama is successfully doing its job in the background.
    
- **The Fix:** Explicitly increase the timeout settings in your n8n nodes that call the Ollama and Whisper APIs.
    

### **4. Audio Formatting and Codec Mismatches**

Mobile apps (from Phase 1) often record audio in highly compressed, proprietary, or variable-bitrate formats (like `.m4a`, `.aac`, or `.amr`).

- **The Issue:** Whisper generally prefers standard formats like `.wav` (specifically 16kHz) or standard `.mp3`. If you feed it a weird mobile audio codec directly from MinIO, it might spit out gibberish or fail completely.
    
- **The Fix:** I had to add a small preprocessing step in the n8n workflow, utilizing `ffmpeg` within a script node, to normalize the audio files into a standard format before passing them to Whisper.
    

### **5. Image Payload Bloat**

To get images from MinIO into Ollama via n8n, you generally have to convert them to Base64 strings.

- **The Issue:** High-resolution photos from modern smartphones create massive Base64 strings. Passing multiple 10MB Base64 strings through n8n's working memory can cause the orchestrator to severely lag or crash.
    
- **The Fix:** Optimize output from the mobile phone app. Or a safer solution would be to implement an image resizing/compression step at the FastAPI ingestion gateway (Phase 2) so that Ollama only receives images optimized for AI vision (e.g., max 1024x1024 pixels). VLMs downsample images anyway, so sending a 4K image is just wasting memory.
    

As we see, my demos are prototypes at best. But while it's clunky at best, it can handle most errors and edge scenarios without breaking. A professional developer with more experience in these frameworks will be able to avoid most of these issues.