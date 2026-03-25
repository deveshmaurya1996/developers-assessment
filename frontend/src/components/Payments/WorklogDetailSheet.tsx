import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type WorklogDetailSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  detail: any | null
  isLoading: boolean
  error: string | null
}

export function WorklogDetailSheet({
  open,
  onOpenChange,
  detail,
  isLoading,
  error,
}: WorklogDetailSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="flex w-full flex-col gap-4 overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>Time entries</SheetTitle>
          <SheetDescription>
            {detail?.task_title != null ? String(detail.task_title) : ""}
          </SheetDescription>
        </SheetHeader>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : null}
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {!isLoading && !error && detail ? (
          <div className="space-y-3 text-sm">
            <div className="grid gap-1 rounded-md border p-3">
              <div className="text-muted-foreground">Freelancer</div>
              <div>{String(detail.freelancer_email)}</div>
              <div className="mt-2 text-muted-foreground">Period totals</div>
              <div>
                {Number(detail.period_hours).toFixed(2)} h ·{" "}
                {Number(detail.period_earned).toFixed(2)} earned
              </div>
              <div className="mt-2 text-muted-foreground">Status</div>
              <div>{String(detail.status)}</div>
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Worked at (UTC)</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Notes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.isArray(detail.entries) && detail.entries.length ? (
                  detail.entries.map((e: any) => (
                    <TableRow key={String(e.id)}>
                      <TableCell className="font-mono text-xs">
                        {String(e.worked_at)}
                      </TableCell>
                      <TableCell>{Number(e.hours).toFixed(2)}</TableCell>
                      <TableCell>
                        {e.notes != null ? String(e.notes) : "—"}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={3}
                      className="text-center text-muted-foreground"
                    >
                      No entries in this range.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}
