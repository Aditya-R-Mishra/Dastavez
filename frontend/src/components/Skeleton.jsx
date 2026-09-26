/**
 * Skeleton — reusable pulsing placeholder for loading states.
 *
 * Usage:
 *   <Skeleton className="h-6 w-40 rounded-md" />          // text line
 *   <Skeleton className="h-32 w-full rounded-xl" />        // card
 *   <Skeleton className="h-10 w-10 rounded-full" />        // avatar
 *
 * Example — Documents page loading state (uncomment when wiring API):
 *
 *   import Skeleton from '../components/Skeleton'
 *
 *   const DocumentsSkeleton = () => (
 *     <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
 *       {Array.from({ length: 4 }).map((_, i) => (
 *         <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-3">
 *           <div className="flex items-start justify-between">
 *             <Skeleton className="h-10 w-10 rounded-lg" />
 *             <Skeleton className="h-5 w-20 rounded-full" />
 *           </div>
 *           <div className="flex flex-col gap-1.5">
 *             <Skeleton className="h-4 w-3/4 rounded-md" />
 *             <Skeleton className="h-3 w-1/3 rounded-md" />
 *           </div>
 *           <div className="pt-1 border-t border-gray-800">
 *             <Skeleton className="h-5 w-12 rounded-md" />
 *           </div>
 *         </div>
 *       ))}
 *     </div>
 *   )
 */

const Skeleton = ({ className = '' }) => (
  <div
    className={`animate-pulse bg-gray-800 ${className}`}
    aria-hidden="true"
  />
)

export default Skeleton
