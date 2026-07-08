import { useEffect, useState } from "react";

export function usePersistedTasks<T>(
  initialValue: T,
  key = "gantt-tasks"
) {
  const [value, setValue] = useState<T>(() => {
    const saved = localStorage.getItem(key);

    if (!saved) {
      return initialValue;
    }

    try {
      return JSON.parse(saved);
    } catch {
      return initialValue;
    }
  });


  useEffect(() => {
    localStorage.setItem(
      key,
      JSON.stringify(value)
    );
  }, [key, value]);


  return [
    value,
    setValue
  ] as const;
}