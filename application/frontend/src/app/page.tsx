"use client";

import { Button } from "@/components/ui/button";
import { signIn } from "next-auth/react";

export default function HomePage() {
  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    await signIn("tumidp", {
      redirect: false,
      callbackUrl: "/chat",
    });
  };
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <div className="mt-8">
        <div className="mb-4">
          <Button className="px-4 py-2 rounded-md" onClick={handleSubmit}>
            TUMChat SSO
          </Button>
        </div>
      </div>
    </div>
  );
}
