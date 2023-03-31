# API 文档

初步 demo 版本

## 后端业务核心流程

```mermaid
graph TD
A(用户上传PDF) --> B[后端将PDF上传至GCS]
B --> C{是否上传成功}
C --> |是| D[后端调用 Google Vision API, 识别PDF中的文字]
C --> |否| E[后端返回错误信息: 上传失败，请重试]
D --> {是否识别成功}
D --> |是| F[后端将PDF识别结果存入数据库]
D --> |否| G[后端返回错误信息: 您的PDF无法识别]
F --> H[后端返回成功信息: 上传成功。 给前端返回 PDF 的 file_id]
```
