import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type PaymentReviewDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  preview: any | null
  previewLoading: boolean
  previewError: string | null
  onConfirm: () => void
  confirmLoading: boolean
}

export function PaymentReviewDialog({
  open,
  onOpenChange,
  preview,
  previewLoading,
  previewError,
  onConfirm,
  confirmLoading,
}: PaymentReviewDialogProps) {
  const rows = Array.isArray(preview?.data) ? preview.data : []
  const total =
    preview?.total_amount != null ? Number(preview.total_amount) : null
  const count = preview?.count != null ? Number(preview.count) : null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Review payment batch</DialogTitle>
          <DialogDescription>
            Confirm totals and included worklogs before marking them paid.
          </DialogDescription>
        </DialogHeader>
        {previewLoading ? (
          <p className="text-sm text-muted-foreground">Loading preview…</p>
        ) : null}
        {previewError ? (
          <p className="text-sm text-destructive">{previewError}</p>
        ) : null}
        {!previewLoading && !previewError && preview ? (
          <div className="space-y-4">
            <div className="rounded-md border p-3 text-sm">
              <div className="font-medium">Summary</div>
              <div className="mt-1 text-muted-foreground">
                Worklogs: {count ?? "—"} · Total:{" "}
                {total != null && !Number.isNaN(total) ? total.toFixed(2) : "—"}
              </div>
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Task</TableHead>
                  <TableHead>Freelancer</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.length ? (
                  rows.map((r: any) => (
                    <TableRow key={String(r.id)}>
                      <TableCell>{String(r.task_title)}</TableCell>
                      <TableCell>{String(r.freelancer_email)}</TableCell>
                      <TableCell>{Number(r.period_hours).toFixed(2)}</TableCell>
                      <TableCell>
                        {Number(r.period_earned).toFixed(2)}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={4}
                      className="text-center text-muted-foreground"
                    >
                      Nothing to pay after exclusions.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        ) : null}
        <DialogFooter className="gap-3 sm:gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Back
          </Button>
          <Button
            type="button"
            onClick={onConfirm}
            disabled={
              confirmLoading ||
              previewLoading ||
              Boolean(previewError) ||
              !rows.length
            }
          >
            {confirmLoading ? "Confirming…" : "Confirm payment"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
