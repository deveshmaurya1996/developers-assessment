import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export type FreelancerOption = {
  id: string
  email: string
}

type FreelancerExcludePanelProps = {
  freelancers: FreelancerOption[]
  excludedFreelancerIds: Set<string>
  onToggleFreelancer: (id: string, excluded: boolean) => void
  worklogTabHint: string
}

export function FreelancerExcludePanel({
  freelancers,
  excludedFreelancerIds,
  onToggleFreelancer,
  worklogTabHint,
}: FreelancerExcludePanelProps) {
  return (
    <Tabs defaultValue="worklog" className="w-full">
      <TabsList className="grid w-full max-w-md grid-cols-2">
        <TabsTrigger value="worklog">Worklog rows</TabsTrigger>
        <TabsTrigger value="freelancer">Freelancers</TabsTrigger>
      </TabsList>
      <TabsContent
        value="worklog"
        className="mt-3 text-sm text-muted-foreground"
      >
        {worklogTabHint}
      </TabsContent>
      <TabsContent value="freelancer" className="mt-3 space-y-3">
        {freelancers.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No freelancers in view.
          </p>
        ) : (
          freelancers.map((f) => (
            <div key={f.id} className="flex items-center gap-2">
              <Checkbox
                id={`fl-ex-${f.id}`}
                checked={excludedFreelancerIds.has(f.id)}
                onCheckedChange={(v) => onToggleFreelancer(f.id, v === true)}
                aria-label={`Exclude all worklogs for ${f.email}`}
              />
              <Label htmlFor={`fl-ex-${f.id}`} className="font-normal">
                Exclude all for {f.email}
              </Label>
            </div>
          ))
        )}
      </TabsContent>
    </Tabs>
  )
}
