import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#08090D] px-4">
      <Card className="w-full max-w-md bg-white/5">
        <CardContent className="space-y-6 p-8">
          <div>
            <h1 className="text-2xl font-semibold text-white">Welcome back</h1>
            <p className="text-sm text-white/60">
              Sign in to access your clipping workspace.
            </p>
          </div>
          <div className="space-y-3">
            <Input placeholder="Email" className="bg-black/30" />
            <Input placeholder="Password" type="password" className="bg-black/30" />
          </div>
          <Button className="w-full rounded-full">Sign in</Button>
          <div className="text-center text-xs text-white/60">
            New to ClipNeuron?{" "}
            <Link href="/" className="text-white">
              Create an account
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
