import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import React from "react";

/**
 * PricingLoadingSkeleton component
 * Renders a loading skeleton for the pricing models grid.
 * No props.
 */

export default function PricingLoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex justify-between items-start">
              <Skeleton className="h-6 w-24" />
              <div className="flex gap-1">
                <Skeleton className="h-8 w-8 rounded-md" />
                <Skeleton className="h-8 w-8 rounded-md" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Skeleton className="h-10 w-10 rounded-full" />
              <Skeleton className="h-6 w-40" />
            </div>
            <Skeleton className="h-4 w-full mt-2" />
          </CardHeader>
          <CardContent className="pb-4">
            <Skeleton className="h-[200px] w-full rounded-lg" />
          </CardContent>
          <CardFooter className="flex justify-between border-t pt-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-8 w-24" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
