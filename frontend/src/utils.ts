import { AxiosError } from "axios"
import type { ApiError } from "./client"

function extractErrorMessage(err: ApiError | AxiosError | Error): string {
  if (err instanceof AxiosError) {
    if (err.code === "ECONNABORTED") {
      return "Request timed out. Is the API running and reachable?"
    }
    if (!err.response) {
      return "Cannot reach the API. Start the backend on http://localhost:8000 and ensure PostgreSQL is running."
    }
    return err.message
  }

  if ("body" in err && err.body !== undefined) {
    const raw = (err as ApiError).body as { detail?: unknown }
    const d = raw?.detail
    if (Array.isArray(d) && d.length > 0) {
      return String((d[0] as { msg?: string }).msg ?? "Something went wrong.")
    }
    if (typeof d === "string") {
      return d
    }
  }

  return err.message || "Something went wrong."
}

export const handleError = function (
  this: (msg: string) => void,
  err: ApiError | AxiosError | Error,
) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
