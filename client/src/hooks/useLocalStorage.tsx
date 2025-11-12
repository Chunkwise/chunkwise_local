import { useEffect, useState } from "react";
import type { State } from "../reducers/workflowReducer";

export function useLocalStorage(key: string, initial: State) {
  const [state, setState] = useState(() => {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : initial;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState] as const;
}
