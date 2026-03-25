import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useCallback, useMemo, useState } from "react"
import { toast } from "sonner"
import { FreelancerExcludePanel } from "@/components/Payments/FreelancerExcludePanel"
import { PaymentDateRangeBar } from "@/components/Payments/PaymentDateRangeBar"
import { PaymentReviewDialog } from "@/components/Payments/PaymentReviewDialog"
import {
  fetchWorklogDetail,
  fetchWorklogs,
  postPaymentConfirm,
  postPaymentPreview,
} from "@/components/Payments/paymentDashboardApi"
import { WorklogDetailSheet } from "@/components/Payments/WorklogDetailSheet"
import {
  WorklogEarningsTable,
  type WorklogRow,
} from "@/components/Payments/WorklogEarningsTable"
import { Button } from "@/components/ui/button"

function utcDateString(d: Date): string {
  return d.toISOString().slice(0, 10)
}

function defaultUtcRange(): { from: string; to: string } {
  const to = new Date()
  const from = new Date(to)
  from.setUTCDate(from.getUTCDate() - 30)
  return { from: utcDateString(from), to: utcDateString(to) }
}

export default function PaymentDashboard() {
  const queryClient = useQueryClient()
  const [rangeInput, setRangeInput] = useState(defaultUtcRange)
  const [applied, setApplied] = useState(defaultUtcRange)
  const [excludedWorklogIds, setExcludedWorklogIds] = useState<Set<string>>(
    () => new Set(),
  )
  const [excludedFreelancerIds, setExcludedFreelancerIds] = useState<
    Set<string>
  >(() => new Set())
  const [sheetOpen, setSheetOpen] = useState(false)
  const [sheetId, setSheetId] = useState<string | null>(null)
  const [reviewOpen, setReviewOpen] = useState(false)

  const worklogsQuery = useQuery({
    queryKey: ["worklogs", applied.from, applied.to],
    queryFn: async () => {
      try {
        return await fetchWorklogs(applied.from, applied.to)
      } catch (e) {
        console.error(e)
        throw new Error("Failed to load worklogs.")
      }
    },
  })

  const detailQuery = useQuery({
    queryKey: ["worklog-detail", sheetId, applied.from, applied.to],
    enabled: Boolean(sheetOpen && sheetId),
    queryFn: async () => {
      try {
        return await fetchWorklogDetail(
          sheetId as string,
          applied.from,
          applied.to,
        )
      } catch (e) {
        console.error(e)
        throw new Error("Failed to load worklog detail.")
      }
    },
  })

  const exWlKey = useMemo(
    () => [...excludedWorklogIds].sort().join(","),
    [excludedWorklogIds],
  )
  const exFlKey = useMemo(
    () => [...excludedFreelancerIds].sort().join(","),
    [excludedFreelancerIds],
  )

  const previewQuery = useQuery({
    queryKey: ["payment-preview", applied.from, applied.to, exWlKey, exFlKey],
    enabled: reviewOpen,
    queryFn: async () => {
      try {
        return await postPaymentPreview({
          date_from: applied.from,
          date_to: applied.to,
          excluded_worklog_ids: [...excludedWorklogIds],
          excluded_freelancer_ids: [...excludedFreelancerIds],
        })
      } catch (e) {
        console.error(e)
        throw new Error("Failed to load payment preview.")
      }
    },
  })

  const confirmMutation = useMutation({
    mutationFn: async () => {
      return postPaymentConfirm({
        date_from: applied.from,
        date_to: applied.to,
        excluded_worklog_ids: [...excludedWorklogIds],
        excluded_freelancer_ids: [...excludedFreelancerIds],
      })
    },
    onSuccess: (data: any) => {
      toast.success(
        `Payment batch ${String(data.batch_id)} recorded for ${String(data.worklog_count)} worklogs.`,
      )
      setReviewOpen(false)
      queryClient.invalidateQueries({ queryKey: ["worklogs"] })
    },
    onError: (e) => {
      console.error(e)
      toast.error("Payment confirmation failed.")
    },
  })

  const rows: WorklogRow[] = useMemo(() => {
    const raw = worklogsQuery.data?.data
    if (!Array.isArray(raw)) {
      return []
    }
    return raw.map((r: any) => ({
      id: String(r.id),
      freelancer_id: String(r.freelancer_id),
      task_title: String(r.task_title),
      freelancer_email: String(r.freelancer_email),
      period_hours: Number(r.period_hours),
      period_earned: Number(r.period_earned),
      status: String(r.status),
      time_entry_count: Number(r.time_entry_count),
    }))
  }, [worklogsQuery.data])

  const freelancers = useMemo(() => {
    const m = new Map<string, string>()
    for (const r of rows) {
      m.set(r.freelancer_id, r.freelancer_email)
    }
    return [...m.entries()].map(([id, email]) => ({ id, email }))
  }, [rows])

  const toggleWorklog = useCallback((id: string, excluded: boolean) => {
    setExcludedWorklogIds((prev) => {
      const next = new Set(prev)
      if (excluded) {
        next.add(id)
      } else {
        next.delete(id)
      }
      return next
    })
  }, [])

  const toggleFreelancer = useCallback((id: string, excluded: boolean) => {
    setExcludedFreelancerIds((prev) => {
      const next = new Set(prev)
      if (excluded) {
        next.add(id)
      } else {
        next.delete(id)
      }
      return next
    })
  }, [])

  const openDetail = useCallback((id: string) => {
    setSheetId(id)
    setSheetOpen(true)
  }, [])

  const worklogsError =
    worklogsQuery.error instanceof Error
      ? worklogsQuery.error.message
      : worklogsQuery.error
        ? "Failed to load worklogs."
        : null

  const detailErr =
    detailQuery.error instanceof Error
      ? detailQuery.error.message
      : detailQuery.error
        ? "Failed to load detail."
        : null

  const previewErr =
    previewQuery.error instanceof Error
      ? previewQuery.error.message
      : previewQuery.error
        ? "Failed to load preview."
        : null

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Worklog payments</h1>
        <p className="text-muted-foreground">
          Filter by payment period, inspect time entries, exclude rows or
          freelancers, then confirm a batch.
        </p>
      </div>

      <PaymentDateRangeBar
        value={rangeInput}
        onChange={setRangeInput}
        onApply={() => setApplied({ ...rangeInput })}
        isLoading={worklogsQuery.isFetching}
      />

      {worklogsError ? (
        <p className="text-sm text-destructive">{worklogsError}</p>
      ) : null}

      {worklogsQuery.isPending ? (
        <p className="text-sm text-muted-foreground">Loading worklogs…</p>
      ) : null}

      <FreelancerExcludePanel
        freelancers={freelancers}
        excludedFreelancerIds={excludedFreelancerIds}
        onToggleFreelancer={toggleFreelancer}
        worklogTabHint="Use the Exclude column in the table to omit individual worklogs from the payment batch."
      />

      <WorklogEarningsTable
        rows={rows}
        excludedWorklogIds={excludedWorklogIds}
        onToggleWorklog={toggleWorklog}
        onRowOpen={openDetail}
      />

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          onClick={() => setReviewOpen(true)}
          disabled={worklogsQuery.isLoading || Boolean(worklogsError)}
        >
          Review payment
        </Button>
      </div>

      <WorklogDetailSheet
        open={sheetOpen}
        onOpenChange={(o) => {
          setSheetOpen(o)
          if (!o) {
            setSheetId(null)
          }
        }}
        detail={detailQuery.data ?? null}
        isLoading={detailQuery.isFetching}
        error={detailErr}
      />

      <PaymentReviewDialog
        open={reviewOpen}
        onOpenChange={setReviewOpen}
        preview={previewQuery.data ?? null}
        previewLoading={previewQuery.isFetching}
        previewError={previewErr}
        onConfirm={() => confirmMutation.mutate()}
        confirmLoading={confirmMutation.isPending}
      />
    </div>
  )
}
