"use client"

import { useState, FormEvent, useEffect } from "react"
import Link from 'next/link'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"

// Interfaces
interface Recipe {
  title: string
  similarity: number
  ingredients: string[]
  ingredients_ner: string[]
  directions: string[]
}

interface ApiResponse {
  input: string
  entities: string[]
  predicted_cluster: number
  cluster_label: string
  similar_recipes: Recipe[]
}

export default function Home() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<ApiResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Drawer state
  const [selectedIngredient, setSelectedIngredient] = useState<string | null>(null)

  // Store in session storage so the recipe page can load it
  useEffect(() => {
    if (results) {
      sessionStorage.setItem("lastRecipes", JSON.stringify(results.similar_recipes))
    }
  }, [results])

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault()
    if (!query) return
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const res = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients: query, top_n: 12 }),
      })

      if (!res.ok) {
        throw new Error("Failed to fetch recipes.")
      }

      const data: ApiResponse = await res.json()
      setResults(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const navigateToRecipe = (recipeTitle: string) => {
    // We use standard link mapping, but pass full title into URL path parameter
    return `/recipe/${encodeURIComponent(recipeTitle)}`
  }

  return (
    <main className="min-h-screen bg-[#050505] text-[#E2E2E2] p-8 md:p-24 font-sans selection:bg-white/20">
      
      {/* Header */}
      <h1 className="text-5xl md:text-7xl font-light tracking-tighter text-white mb-12">
        Culinary Index.
      </h1>

      {/* Search Bar section */}
      <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 mb-16 w-full max-w-3xl">
        <Input 
          type="text" 
          placeholder="Enter ingredients e.g. chicken garlic soy sauce vinegar..." 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 bg-[#111] border-[#2A2A2A] text-white rounded-xl px-6 py-8 text-lg font-light focus-visible:ring-1 focus-visible:ring-white/20"
        />
        <Button 
          type="submit" 
          disabled={loading}
          className="md:w-32 bg-white text-black hover:bg-gray-200 rounded-xl px-0 py-8 text-lg font-medium transition-all duration-300"
        >
          {loading ? "Decoding..." : "Search"}
        </Button>
      </form>

      {/* Error state */}
      {error && (
        <div className="text-red-400 font-light tracking-wide">{error}</div>
      )}

      {/* Results grid */}
      {results && (
        <div className="animate-in fade-in slide-in-from-bottom-6 duration-1000">
          <div className="mb-8 inline-block px-4 py-1.5 rounded-lg bg-[#1A1A1A] border border-[#333] text-xs font-mono text-[#999] uppercase tracking-widest">
            Topology: {results.cluster_label}
          </div>

          <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
            {results.similar_recipes.map((recipe, idx) => (
              <Card key={idx} className="break-inside-avoid bg-white/5 backdrop-blur-xl border-white/10 overflow-hidden hover:scale-[1.02] hover:bg-white/10 transition-all duration-500 ease-out flex flex-col">
                <div className="h-48 w-full bg-gradient-to-br from-[#1a1a1a] to-[#0A0A0A] border-b border-white/5 flex items-center justify-center p-6">
                   <h2 className="text-2xl font-semibold tracking-tight text-white/90 text-center leading-tight">
                     {recipe.title}
                   </h2>
                </div>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono tracking-widest uppercase text-white/50">{recipe.directions.length} Steps</span>
                    <Badge variant="outline" className="bg-white/5 border-white/10 text-white/70 font-light rounded-sm">
                      {(recipe.similarity * 100).toFixed(1)}% Match
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 pb-4">
                  <div className="text-sm font-light text-white/60 mb-3 uppercase tracking-wider text-xs">Primary Entities</div>
                  <div className="flex flex-wrap gap-2">
                    {recipe.ingredients_ner.slice(0, 5).map((ing, i) => (
                      <Sheet key={i}>
                        <SheetTrigger asChild>
                          <Badge 
                            variant="secondary" 
                            className="bg-black/40 hover:bg-white/20 hover:text-white cursor-pointer text-white/70 border border-white/5 font-light"
                            onClick={() => setSelectedIngredient(ing)}
                          >
                            {ing}
                          </Badge>
                        </SheetTrigger>
                        <SheetContent className="bg-[#0A0A0A] border-l-[#222] text-[#E2E2E2] min-w-[400px]">
                          <SheetHeader className="mt-8">
                            <SheetTitle className="text-4xl font-light text-white tracking-tighter capitalize">{selectedIngredient}</SheetTitle>
                            <SheetDescription className="text-white/50 text-lg font-light leading-relaxed mt-4">
                              Core molecular entity extracted from vector embedding. Extremely common in {results.cluster_label} recipes.
                            </SheetDescription>
                          </SheetHeader>
                          
                          <div className="mt-12 space-y-6">
                             <div className="p-6 bg-white/5 rounded-2xl border border-white/5">
                                <h3 className="text-white font-medium mb-2 tracking-wide text-sm">Suggested Pairings</h3>
                                <div className="flex flex-wrap gap-2 mt-4">
                                  {results.entities.filter(e => e.toLowerCase() !== selectedIngredient?.toLowerCase()).slice(0,3).map((peer, i) => (
                                    <span key={i} className="px-3 py-1 bg-black/50 rounded-full text-xs font-mono text-white/60">{peer}</span>
                                  ))}
                                </div>
                             </div>
                          </div>
                        </SheetContent>
                      </Sheet>
                    ))}
                    {recipe.ingredients_ner.length > 5 && (
                      <Badge variant="outline" className="bg-transparent border-white/10 text-white/40 font-light">+{recipe.ingredients_ner.length - 5} more</Badge>
                    )}
                  </div>
                </CardContent>
                <CardFooter className="pt-4 border-t border-white/5 mt-auto">
                   <Link href={navigateToRecipe(recipe.title)} className="w-full">
                     <Button className="w-full bg-[#111] hover:bg-white hover:text-black border border-[#222] text-white font-light tracking-wide rounded-lg transition-all duration-300">
                       View Full Recipe
                     </Button>
                   </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      )}
    </main>
  )
}
