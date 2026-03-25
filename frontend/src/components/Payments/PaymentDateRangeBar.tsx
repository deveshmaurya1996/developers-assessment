import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Range = { from: string; to: string }

type PaymentDateRangeBarProps = {
  value: Range
  onChange: (next: Range) => void
  onApply: () => void
  isLoading: boolean
}

export function PaymentDateRangeBar({
  value,
  onChange,
  onApply,
  isLoading,
}: PaymentDateRangeBarProps) {
  return (
    <div className="flex flex-col gap-4 rounded-lg border bg-card p-4 md:flex-row md:items-end">
      <div className="grid flex-1 gap-2">
        <Label htmlFor="pay-date-from">Date from (UTC)</Label>
        <Input
          id="pay-date-from"
          type="date"
          value={value.from}
          onChange={(e) => onChange({ ...value, from: e.target.value })}
        />
      </div>
      <div className="grid flex-1 gap-2">
        <Label htmlFor="pay-date-to">Date to (UTC)</Label>
        <Input
          id="pay-date-to"
          type="date"
          value={value.to}
          onChange={(e) => onChange({ ...value, to: e.target.value })}
        />
      </div>
      <Button
        type="button"
        onClick={onApply}
        disabled={isLoading}
        className="md:mb-0.5"
      >
        Apply range
      </Button>
    </div>
  )
}
