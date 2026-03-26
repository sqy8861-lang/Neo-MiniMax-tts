# Neo-MiniMax-TTS 插件使用说明

## 功能概述

这是一个基于 MiniMax TTS API 的文本转语音插件，支持：
- 使用预设音色进行文本转语音
- 使用声音克隆后的自定义音色
- 手动触发语音消息发送
- 支持多种语音参数配置（语速、音量等）

## 安装

1. 确保插件已放置在 `plugins/neo_minimax_tts/` 目录下
2. 安装依赖：
   ```bash
   uv pip install aiohttp
   ```
   或直接在项目根目录运行：
   ```bash
   uv sync
   ```

## 配置

### 1. 创建配置文件

在项目根目录创建配置文件 `config/plugins/neo_minimax_tts/config.toml`：

```toml
[minimax]
# MiniMax API Key（必填）
api_key = "your-minimax-api-key"

# TTS 模型名称（可选，默认 speech-2.8-hd）
model = "speech-2.8-hd"

# 默认语音 ID（可选，默认 female-tianmei）
# 支持声音克隆后的 voice_id
voice_id = "female-tianmei"

# 语速（可选，0.5-2.0，默认 1.0）
speed = 1.0

# 音量（可选，0.1-1.0，默认 1.0）
volume = 1.0

[output]
# 音频文件保存目录（可选）
audio_dir = "data/neo_minimax_tts/audio"

# 音频格式（可选，mp3/wav/aac，默认 mp3）
audio_format = "mp3"

# 单次转换最大文本长度（可选，默认 500）
max_text_length = 500

[behavior]
# 发送后是否自动删除本地音频文件（可选，默认 false）
auto_delete = false

# 是否以语音消息形式发送（可选，默认 true）
send_as_record = true
```

### 2. 获取 MiniMax API Key

1. 访问 [MiniMax 开放平台](https://platform.minimaxi.com/)
2. 注册/登录账号
3. 在控制台中获取 API Key

## 声音克隆

### 上传音频（本地操作）

按照 MiniMax 官方文档的步骤，在本地上传音频进行声音克隆：

1. 访问 [MiniMax 音频中心](https://www.minimax.io/audio)
2. 选择「Create your Voice Clone」
3. 上传你的音频样本（建议 10 秒以上，清晰的人声）
4. 完成克隆后获取 voice_id

### 在插件中使用克隆音色

有两种方式使用声音克隆后的音色：

#### 方式 1：在配置文件中设置默认音色

修改 `config/plugins/neo_minimax_tts/config.toml`：

```toml
[minimax]
voice_id = "your-cloned-voice-id"  # 替换为你的克隆音色 ID
```

#### 方式 2：调用时指定音色

在 LLM 调用 `neo_minimax_tts` action 时，传入 `voice_id` 参数：

```
使用 neo_minimax_tts 功能，文本="你好，这是测试"，voice_id="your-cloned-voice-id"
```

## 测试

### 使用测试脚本

运行测试脚本验证 TTS 功能：

```bash
cd d:\agenet\Neo-MoFox-dev
python checkcode\test_tts.py
```

按照提示输入：
- MiniMax API Key
- Voice ID（可选）
- 测试文本（可选）

测试成功后，音频文件将保存到 `checkcode/tts_output/` 目录。

## 使用方式

### 在聊天中手动触发

当机器人回复你时，你可以要求它使用语音回复，例如：

> "用语音回复我"
> "把刚才的回复用语音说一遍"
> "用克隆的声音说：你好"

### Action 组件

插件提供了 `neo_minimax_tts` action，可被 LLM 调用：

- **名称**: `neo_minimax_tts`
- **参数**:
  - `text` (必填): 要转换为语音的文本
  - `voice_id` (可选): 语音 ID（覆盖配置文件，支持克隆音色）

## 常见音色列表

MiniMax 提供以下预设音色：

- `female-tianmei`: 女声 - 甜美
- `female-yujie`: 女声 - 御姐
- `female-chengshu`: 女声 - 成熟
- `male-qn-qingse`: 男声 - 青涩
- `male-qn-jingying`: 男声 - 精英
- `male-qn-badao`: 男声 - 霸道

## 注意事项

1. **API Key 安全**: 不要将包含真实 API Key 的配置文件提交到版本控制
2. **文本长度**: 单次转换文本长度建议控制在 500 字以内
3. **音频质量**: 声音克隆建议使用 10 秒以上、清晰无背景噪音的音频
4. **费用**: MiniMax TTS API 按使用量计费，请关注账户余额

## 故障排除

### API 调用失败

- 检查 API Key 是否正确
- 确认账户有足够的余额
- 查看日志中的详细错误信息

### 语音无法播放

- 确认音频格式支持（mp3/wav/aac）
- 检查文件是否完整下载
- 尝试使用不同的播放器

### 声音克隆不成功

- 确保音频样本清晰，无背景噪音
- 音频长度建议在 10-60 秒之间
- 使用单人、正常语速的录音
