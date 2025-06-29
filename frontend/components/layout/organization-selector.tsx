"use client"

import { useState } from 'react'
import { Building2, Check, ChevronsUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useOrganization } from '@/contexts/OrganizationContext'
import { useSidebar } from '@/components/ui/custom-sidebar'

export function OrganizationSelector() {
  const { currentOrgId, setCurrentOrgId, organizations, loading } = useOrganization()
  const { expanded } = useSidebar()
  const [open, setOpen] = useState(false)

  const currentOrg = organizations.find(org => org.id === currentOrgId)

  if (loading) {
    return (
      <div className="px-2 py-2">
        <Skeleton className="h-8 w-full" />
      </div>
    )
  }

  if (!organizations.length) {
    return null
  }

  // Collapsed sidebar view - just show icon and tooltip
  if (!expanded) {
    return (
      <div className="group relative px-2 py-2">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-center p-2"
          onClick={() => setOpen(true)}
        >
          <Building2 className="h-4 w-4" />
        </Button>
        <div className="absolute left-full ml-2 hidden rounded-md bg-popover px-2 py-1 text-sm text-popover-foreground shadow-md group-hover:block z-50">
          {currentOrg?.name || 'Select Organization'}
        </div>
      </div>
    )
  }

  // Expanded sidebar view
  return (
    <div className="px-2 py-2">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="ghost"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between text-left h-auto p-2"
          >
            <div className="flex items-center gap-2 min-w-0">
              <Building2 className="h-4 w-4 flex-shrink-0" />
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-medium truncate">
                  {currentOrg?.name || 'Select Organization'}
                </span>
                {currentOrg && (
                  <Badge 
                    variant={currentOrg.status === 'active' ? 'default' : 'secondary'} 
                    className="text-xs w-fit mt-1"
                  >
                    {currentOrg.status}
                  </Badge>
                )}
              </div>
            </div>
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[280px] p-0" align="start">
          <Command>
            <CommandInput placeholder="Search organizations..." />
            <CommandEmpty>No organizations found.</CommandEmpty>
            <CommandList>
              <CommandGroup>
                {organizations.map((org) => (
                  <CommandItem
                    key={org.id}
                    value={org.name}
                    onSelect={() => {
                      setCurrentOrgId(org.id)
                      setOpen(false)
                    }}
                  >
                    <div className="flex items-center gap-2 w-full">
                      <Check
                        className={cn(
                          "h-4 w-4",
                          currentOrgId === org.id ? "opacity-100" : "opacity-0"
                        )}
                      />
                      <div className="flex flex-col gap-1 min-w-0 flex-1">
                        <span className="font-medium truncate">{org.name}</span>
                        {org.description && (
                          <span className="text-xs text-muted-foreground truncate">
                            {org.description}
                          </span>
                        )}
                      </div>
                      <Badge 
                        variant={org.status === 'active' ? 'default' : 'secondary'} 
                        className="text-xs"
                      >
                        {org.status}
                      </Badge>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
}
