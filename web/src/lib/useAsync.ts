import { useCallback, useEffect, useRef, useState } from 'react'
import { errorText } from '../api/client'

export interface AsyncState<T> {
  data: T | null
  error: string | null
  loading: boolean
  reload: () => void
  setData: (d: T | null) => void
}

/** Runs `load` on mount and whenever `deps` change. Ignores results from stale calls. */
export function useAsync<T>(load: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const callId = useRef(0)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(load, deps)

  const reload = useCallback(() => {
    const id = ++callId.current
    setLoading(true)
    setError(null)
    run()
      .then((d) => {
        if (id === callId.current) setData(d)
      })
      .catch((e) => {
        if (id === callId.current) setError(errorText(e))
      })
      .finally(() => {
        if (id === callId.current) setLoading(false)
      })
  }, [run])

  useEffect(reload, [reload])

  return { data, error, loading, reload, setData }
}
