import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const POKEMON_TYPE_BASE_STYLE = "rounded-full border-2 border-black shadow-[inset_0_0_0_2px_white] blur-[0.4px]"

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        grass:
          `${POKEMON_TYPE_BASE_STYLE} bg-green-500 text-white`,
        poison:
          `${POKEMON_TYPE_BASE_STYLE} bg-purple-600 text-white`,
        fire:
          `${POKEMON_TYPE_BASE_STYLE} bg-red-500 text-white`,
        flying:
          `${POKEMON_TYPE_BASE_STYLE} bg-indigo-400 text-white`,
        water:
          `${POKEMON_TYPE_BASE_STYLE} bg-blue-500 text-white`,
        bug:
          `${POKEMON_TYPE_BASE_STYLE} bg-lime-500 text-white`,
        normal:
          `${POKEMON_TYPE_BASE_STYLE} bg-gray-400 text-white`,
        electric:
          `${POKEMON_TYPE_BASE_STYLE} bg-yellow-400 text-black`,
        ground:
          `${POKEMON_TYPE_BASE_STYLE} bg-amber-600 text-white`,
        fairy:
          `${POKEMON_TYPE_BASE_STYLE} bg-pink-300 text-black`,
        fighting:
          `${POKEMON_TYPE_BASE_STYLE} bg-red-700 text-white`,
        psychic:
          `${POKEMON_TYPE_BASE_STYLE} bg-pink-500 text-white`,
        rock:
          `${POKEMON_TYPE_BASE_STYLE} bg-amber-800 text-white`,
        steel:
          `${POKEMON_TYPE_BASE_STYLE} bg-slate-500 text-white`,
        ice:
          `${POKEMON_TYPE_BASE_STYLE} bg-cyan-300 text-black`,
        ghost:
          `${POKEMON_TYPE_BASE_STYLE} bg-indigo-800 text-white`,
        dragon:
          `${POKEMON_TYPE_BASE_STYLE} bg-violet-600 text-white`,
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span"

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
