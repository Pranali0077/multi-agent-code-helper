import { useState, useEffect } from "react";
import { checkHealth } from "../lib/api";

export function useHealth(intervalMs = 15000) {
  const [healthy, setHealthy] = useState<boolean>(true);

  useEffect(() => {
    let active = true;

    const poll = async () => {
      try {
        await checkHealth();
        if (active) setHealthy(true);
      } catch {
        if (active) setHealthy(false);
      }
    };

    poll();
    const timer = setInterval(poll, intervalMs);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [intervalMs]);

  return healthy;
}
