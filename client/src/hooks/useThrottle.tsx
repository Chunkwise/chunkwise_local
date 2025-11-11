import { useEffect, useRef } from "react";

/**
 * Hook that returns a throttled version of a value.
 * Updates at most once per delay period.
 */
export function useThrottle<T>(value: T, delay: number): T {
  const throttledValue = useRef<T>(value);
  const lastUpdated = useRef<number>(Date.now());

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdated.current;

    if (timeSinceLastUpdate >= delay) {
      throttledValue.current = value;
      lastUpdated.current = now;
    } else {
      const timeoutId = setTimeout(() => {
        throttledValue.current = value;
        lastUpdated.current = Date.now();
      }, delay - timeSinceLastUpdate);

      return () => clearTimeout(timeoutId);
    }
  }, [value, delay]);

  return throttledValue.current;
}
