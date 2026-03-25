import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"
import { useMemo } from "react"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export type WorklogRow = {
  id: string
  freelancer_id: string
  task_title: string
  freelancer_email: string
  period_hours: number
  period_earned: number
  status: string
  time_entry_count: number
}

type WorklogEarningsTableProps = {
  rows: WorklogRow[]
  excludedWorklogIds: Set<string>
  onToggleWorklog: (id: string, excluded: boolean) => void
  onRowOpen: (id: string) => void
}

export function WorklogEarningsTable({
  rows,
  excludedWorklogIds,
  onToggleWorklog,
  onRowOpen,
}: WorklogEarningsTableProps) {
  const columns = useMemo<ColumnDef<WorklogRow>[]>(
    () => [
      {
        id: "exclude",
        header: "Exclude",
        cell: ({ row }) => (
          <Checkbox
            checked={excludedWorklogIds.has(row.original.id)}
            onCheckedChange={(v) =>
              onToggleWorklog(row.original.id, v === true)
            }
            onClick={(e) => e.stopPropagation()}
            aria-label={`Exclude worklog ${row.original.id}`}
          />
        ),
      },
      {
        accessorKey: "task_title",
        header: "Task",
      },
      {
        accessorKey: "freelancer_email",
        header: "Freelancer",
      },
      {
        accessorKey: "period_hours",
        header: "Hours (period)",
      },
      {
        accessorKey: "period_earned",
        header: "Earned (period)",
        cell: ({ getValue }) => {
          const v = getValue() as number
          return v.toFixed(2)
        },
      },
      {
        accessorKey: "status",
        header: "Status",
      },
      {
        accessorKey: "time_entry_count",
        header: "Entries",
      },
    ],
    [excludedWorklogIds, onToggleWorklog],
  )

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 8 } },
  })

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((hg) => (
            <TableRow key={hg.id} className="hover:bg-transparent">
              {hg.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className="cursor-pointer"
                onClick={() => onRowOpen(row.original.id)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-24 text-center text-muted-foreground"
              >
                No worklogs for this range.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm text-muted-foreground">
          Page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount() || 1}
        </div>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="hidden size-8 lg:flex"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
            aria-label="First page"
          >
            <ChevronsLeft className="size-4" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            aria-label="Previous page"
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="size-8"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            aria-label="Next page"
          >
            <ChevronRight className="size-4" />
          </Button>
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="hidden size-8 lg:flex"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
            aria-label="Last page"
          >
            <ChevronsRight className="size-4" />
          </Button>
          <Select
            value={`${table.getState().pagination.pageSize}`}
            onValueChange={(v) => table.setPageSize(Number(v))}
          >
            <SelectTrigger className="w-[130px]" aria-label="Rows per page">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {[8, 12, 20].map((n) => (
                <SelectItem key={n} value={`${n}`}>
                  {n} / page
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )
}
