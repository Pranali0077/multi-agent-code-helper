export type TraceStep =
  | { kind: "route"; from: string; to: string }
  | { kind: "tool_call"; agent: string; name: string; args: unknown }
  | { kind: "tool_result"; agent: string; name: string; preview: string };

export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  agent?: string;
  trace?: TraceStep[];
  error?: string;
};

export type AgentInfo = {
  name: string;
  label: string;
  role: string;
  color: "slate" | "blue" | "green" | "purple" | "amber";
  description: string;
  example?: string;
};
