import axios from "axios"

function apiRoot(): string {
  return import.meta.env.VITE_API_URL
}

function headers(): Record<string, string> {
  const t = localStorage.getItem("access_token") || ""
  const h: Record<string, string> = {}
  if (t) {
    h.Authorization = `Bearer ${t}`
  }
  return h
}

export async function fetchWorklogs(
  dateFrom: string,
  dateTo: string,
): Promise<any> {
  const { data } = await axios.get(`${apiRoot()}/api/v1/worklogs/`, {
    params: { date_from: dateFrom, date_to: dateTo },
    headers: headers(),
  })
  return data
}

export async function fetchWorklogDetail(
  worklogId: string,
  dateFrom: string,
  dateTo: string,
): Promise<any> {
  const { data } = await axios.get(
    `${apiRoot()}/api/v1/worklogs/${worklogId}`,
    {
      params: { date_from: dateFrom, date_to: dateTo },
      headers: headers(),
    },
  )
  return data
}

export async function postPaymentPreview(body: {
  date_from: string
  date_to: string
  excluded_worklog_ids: string[]
  excluded_freelancer_ids: string[]
}): Promise<any> {
  const { data } = await axios.post(
    `${apiRoot()}/api/v1/payments/preview`,
    body,
    { headers: headers() },
  )
  return data
}

export async function postPaymentConfirm(body: {
  date_from: string
  date_to: string
  excluded_worklog_ids: string[]
  excluded_freelancer_ids: string[]
}): Promise<any> {
  const { data } = await axios.post(
    `${apiRoot()}/api/v1/payments/confirm`,
    body,
    { headers: headers() },
  )
  return data
}
