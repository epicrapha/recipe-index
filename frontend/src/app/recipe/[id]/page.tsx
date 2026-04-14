"use client"

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'

interface Recipe {
  title: string
  similarity: number
  ingredients: string[]
  ingredients_ner: string[]
  directions: string[]
}

export default function RecipeDetail() {
  const params = useParams()
  const recipeId = decodeURIComponent(params.id as string)

  const [recipe, setRecipe] = useState<Recipe | null>(null)
  const [loading, setLoading] = useState(true)
  const [checkedSteps, setCheckedSteps] = useState<Set<number>>(new Set())

  useEffect(() => {
    // Pull the recipe out of our search session memory instead of hitting the REST endpoint again
    const stored = sessionStorage.getItem("lastRecipes")
    if (stored) {
      const recipes: Recipe[] = JSON.parse(stored)
      const found = recipes.find(r => r.title === recipeId)
      if (found) setRecipe(found)
    }
    setLoading(false)
  }, [recipeId])

  const toggleStep = (idx: number) => {
    const next = new Set(checkedSteps)
    if (next.has(idx)) {
      next.delete(idx)
    } else {
      next.add(idx)
    }
    setCheckedSteps(next)
  }

  if (loading) return null

  if (!recipe) {
    return (
      <main className="min-h-screen bg-[#050505] flex items-center justify-center text-white">
        <div className="text-center">
          <h1 className="text-3xl font-light mb-4">Recipe lost in matrix.</h1>
          <Link href="/">
            <Button variant="outline" className="border-white/10 text-white hover:bg-white/10">Return to Base</Button>
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#050505] text-[#E2E2E2] font-sans selection:bg-white/20 pb-24">
      
      {/* Hero Image / Placeholder */}
      <div className="relative w-full h-[40vh] md:h-[50vh] bg-gradient-to-br from-[#1a1a1a] via-[#0A0A0A] to-[#000] border-b border-white/5 flex flex-col justify-end p-8 md:p-24">
        
        {/* Navigation */}
        <div className="absolute top-8 left-8 md:top-12 md:left-24">
            <Link href="/">
              <Button variant="ghost" className="text-white/60 hover:text-white hover:bg-white/10 tracking-widest text-xs font-mono uppercase">
                ← Back to Discovery
              </Button>
            </Link>
        </div>

        <div className="max-w-4xl animate-in slide-in-from-bottom-8 duration-700">
           <div className="flex gap-4 items-center mb-6">
              <Badge variant="outline" className="bg-transparent border-white/20 text-white/70 font-light px-4 py-1">
                 {(recipe.similarity * 100).toFixed(1)}% Match Confidence
              </Badge>
              <span className="text-white/30 text-sm font-mono">{recipe.directions.length} Prep Steps</span>
           </div>
           <h1 className="text-5xl md:text-8xl font-light tracking-tighter text-white leading-none">
             {recipe.title}
           </h1>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-16 grid grid-cols-1 md:grid-cols-12 gap-16">
        
        {/* Sidebar: Ingredients */}
        <div className="md:col-span-4 space-y-8 animate-in slide-in-from-left-8 duration-1000 delay-150 fill-mode-both">
          
          <div>
             <h3 className="text-sm font-mono tracking-widest uppercase text-white/50 border-b border-white/10 pb-4 mb-6">Raw Materials</h3>
             <ul className="space-y-4">
                {recipe.ingredients.map((ing, idx) => (
                   <li key={idx} className="font-light text-white/80 leading-relaxed text-lg border-l-2 border-white/10 pl-4">
                      {ing}
                   </li>
                ))}
             </ul>
          </div>

          <div className="pt-8">
             <h3 className="text-sm font-mono tracking-widest uppercase text-white/50 border-b border-white/10 pb-4 mb-6">Semantic Entities</h3>
             <div className="flex flex-wrap gap-2">
                {recipe.ingredients_ner.map((tag, idx) => (
                  <Badge key={idx} variant="secondary" className="bg-white/5 text-white/60 font-light hover:bg-white/10 transition-colors">
                    {tag}
                  </Badge>
                ))}
             </div>
          </div>
        </div>

        {/* Main Content: Preparation Protocol */}
        <div className="md:col-span-8 animate-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
           <h3 className="text-sm font-mono tracking-widest uppercase text-white/50 border-b border-white/10 pb-4 mb-8">Preparation Protocol</h3>
           
           <div className="space-y-6">
              {recipe.directions.map((step, idx) => {
                 const isCompleted = checkedSteps.has(idx)
                 return (
                   <div 
                     key={idx} 
                     className={`group p-6 rounded-2xl bg-white/5 border border-white/5 transition-all duration-300 cursor-pointer flex gap-6 ${isCompleted ? 'opacity-40 grayscale data-[state=checked]:bg-white' : 'hover:bg-white/10 hover:border-white/20'}`}
                     onClick={() => toggleStep(idx)}
                   >
                     <div className="pt-1">
                        <Checkbox 
                           checked={isCompleted} 
                           className="w-6 h-6 rounded-full border-white/20 data-[state=checked]:bg-white data-[state=checked]:text-black"
                        />
                     </div>
                     <div className="flex-1">
                        <span className={`block text-xs font-mono uppercase tracking-widest mb-2 ${isCompleted ? 'text-white/30' : 'text-white/50'}`}>Step 0{idx + 1}</span>
                        <p className={`text-xl font-light leading-relaxed ${isCompleted ? 'line-through text-white/50' : 'text-white'}`}>
                          {step}
                        </p>
                     </div>
                   </div>
                 )
              })}
           </div>

           <div className="mt-16 p-8 rounded-3xl bg-[#111] border border-[#222] text-center">
              <h4 className="text-2xl font-light text-white mb-4">Cooking Completed?</h4>
              <Button className="w-full md:w-auto bg-white text-black hover:bg-gray-200 px-12 py-6 text-lg font-medium rounded-xl">
                 Mark as Finalized
              </Button>
           </div>
        </div>

      </div>
    </main>
  )
}
