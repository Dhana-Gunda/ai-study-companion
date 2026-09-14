import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FolderPlus, Layers, ArrowRight } from "lucide-react";

export default function SpacesPage() {
  const spaces = [
    {
      id: "space-1",
      name: "AI & Machine Learning",
      description: "Exploration of deep learning architectures, transformer attention, and RAG pipelines.",
      projectsCount: 3,
      materialsCount: 12
    },
    {
      id: "space-2",
      name: "Distributed Systems",
      description: "Cloud-native consensus, CAP theorem, streaming architectures, and message queues.",
      projectsCount: 2,
      materialsCount: 8
    }
  ];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Learning Spaces</h1>
          <p className="text-sm text-zinc-400">Broad areas of study containing focused learning projects</p>
        </div>
        <Button className="gap-2">
          <FolderPlus className="w-4 h-4" /> Create Space
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {spaces.map((space) => (
          <Card key={space.id} className="hover:border-zinc-700 transition-colors">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Layers className="w-5 h-5 text-indigo-400" />
                  {space.name}
                </CardTitle>
                <Badge variant="secondary">{space.projectsCount} Projects</Badge>
              </div>
              <CardDescription>{space.description}</CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between border-t border-zinc-800/60 pt-4 text-sm">
              <span className="text-zinc-500">{space.materialsCount} Documents Indexed</span>
              <Link
                href={`/spaces/${space.id}/projects/project-ml`}
                className="text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
              >
                View Projects <ArrowRight className="w-4 h-4" />
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
