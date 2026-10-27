import type { Message } from "../types";

export function formatExportMarkdown(messages: Message[]): string {
  let output = "# Code Helper — Sample Questions\n\n";

  let pairIndex = 1;
  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    if (msg.role === "user") {
      const nextMsg = messages[i + 1];
      const answerMsg = nextMsg && nextMsg.role === "assistant" ? nextMsg : null;

      output += `## ${pairIndex}. ${msg.text}\n\n`;
      if (answerMsg) {
        output += `**Answered by:** \`${answerMsg.agent || "coordinator"}\`\n\n`;
        output += `${answerMsg.text || "(No response)"}\n\n`;

        if (answerMsg.trace && answerMsg.trace.length > 0) {
          const toolCalls = answerMsg.trace
            .filter((t) => t.kind === "tool_call")
            .map((t) => (t as { kind: "tool_call"; name: string }).name);

          if (toolCalls.length > 0) {
            output += `**Tools called:** ${Array.from(new Set(toolCalls)).map((name) => `\`${name}\``).join(", ")}\n\n`;
          }
        }
      } else {
        output += "(Pending or unanswered)\n\n";
      }

      pairIndex++;
    }
  }

  return output.trimEnd() + "\n";
}

export function downloadMarkdown(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
