import { createFileRoute } from "@tanstack/react-router"

import PaymentDashboard from "@/components/Payments/PaymentDashboard"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/payments")({
  component: PaymentsPage,
  head: () => ({
    meta: [{ title: "Payments - FastAPI Cloud" }],
  }),
})

function PaymentsPage() {
  const { user: currentUser } = useAuth()

  if (!currentUser?.is_superuser) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6 text-sm">
        You need administrator access to open the payment dashboard.
      </div>
    )
  }

  return <PaymentDashboard />
}
