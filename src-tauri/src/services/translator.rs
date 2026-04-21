use futures::StreamExt;
use serde_json::Value;
use tauri::Emitter;

pub fn format_prompt(
    template: &str,
    source_language: &str,
    target_language: &str,
    text: &str,
) -> String {
    template
        .replace("{source_language}", source_language)
        .replace("{target_language}", target_language)
        .replace("{selected_text}", text)
}

/// Parse one SSE data line, returning the content delta if present.
pub fn parse_sse_line(line: &str) -> Option<String> {
    let data = line.strip_prefix("data: ")?;
    if data == "[DONE]" {
        return None;
    }
    let json: Value = serde_json::from_str(data).ok()?;
    json["choices"][0]["delta"]["content"]
        .as_str()
        .map(|s| s.to_string())
}

/// Stream a translation from an OpenAI-compatible API, emitting chunks via Tauri events.
/// Returns the full accumulated translation on success.
pub async fn translate_stream(
    text: &str,
    prompt_template: &str,
    source_language: &str,
    target_language: &str,
    api_key: &str,
    base_url: &str,
    model: &str,
    app_handle: &tauri::AppHandle,
) -> Result<String, String> {
    let prompt = format_prompt(prompt_template, source_language, target_language, text);

    let body = serde_json::json!({
        "model": model,
        "messages": [
            { "role": "user", "content": prompt }
        ],
        "stream": true
    });

    let url = format!(
        "{}/chat/completions",
        base_url.trim_end_matches('/')
    );

    let client = reqwest::Client::builder()
        .connect_timeout(std::time::Duration::from_secs(10))
        .timeout(std::time::Duration::from_secs(60))
        .build()
        .map_err(|e| format!("Failed to create HTTP client: {}", e))?;
    let response = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", api_key))
        .header("Content-Type", "application/json")
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("Network error: {}", e))?;

    if !response.status().is_success() {
        let status = response.status();
        let body_text = response.text().await.unwrap_or_default();
        return Err(format!("API error ({}): {}", status, body_text));
    }

    let mut stream = response.bytes_stream();
    let mut accumulated = String::new();
    let mut buffer = String::new();

    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| format!("Stream error: {}", e))?;
        buffer.push_str(&String::from_utf8_lossy(&chunk));

        while let Some(line_end) = buffer.find('\n') {
            let line = buffer[..line_end].trim().to_string();
            buffer = buffer[line_end + 1..].to_string();

            if line.is_empty() {
                continue;
            }

            if let Some(content) = parse_sse_line(&line) {
                accumulated.push_str(&content);
                let _ = app_handle.emit("translation:chunk", &accumulated);
            }
        }
    }

    let _ = app_handle.emit("translation:complete", &accumulated);
    Ok(accumulated)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_prompt() {
        let result = format_prompt(
            "Translate from {source_language} to {target_language}: {selected_text}",
            "英语",
            "中文",
            "hello world",
        );
        assert_eq!(result, "Translate from 英语 to 中文: hello world");
    }

    #[test]
    fn test_format_prompt_default_template() {
        let result = format_prompt(
            crate::types::DEFAULT_PROMPT,
            "English",
            "中文",
            "test input",
        );
        assert!(result.contains("English"));
        assert!(result.contains("中文"));
        assert!(result.contains("test input"));
    }

    #[test]
    fn test_parse_sse_line_content() {
        let line = r#"data: {"choices":[{"delta":{"content":"Hello"}}]}"#;
        assert_eq!(parse_sse_line(line), Some("Hello".into()));
    }

    #[test]
    fn test_parse_sse_line_done() {
        assert_eq!(parse_sse_line("data: [DONE]"), None);
    }

    #[test]
    fn test_parse_sse_line_no_content() {
        let line = r#"data: {"choices":[{"delta":{}}]}"#;
        assert_eq!(parse_sse_line(line), None);
    }

    #[test]
    fn test_parse_sse_line_not_data() {
        assert_eq!(parse_sse_line("event: ping"), None);
    }
}
