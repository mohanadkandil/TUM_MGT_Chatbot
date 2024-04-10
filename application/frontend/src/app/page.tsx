"use client";

import { DisclaimerDialog } from "@/components/disclaimer-dialog";
import { Button } from "@/components/ui/button";
import { useDisclaimerChoice } from "@/lib/stores/useDisclaimerChoice";
import { signIn } from "next-auth/react";

export default function HomePage() {
  const selectedDisclaimerState = useDisclaimerChoice(
    (state) => state.hasAccepted
  );

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    await signIn("tumidp", {
      redirect: false,
      callbackUrl: "/chat",
    });
  };
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2 w-full">
      <div className="mt-8 flex flex-col justify-center">
        <Button
          className="rounded-md bg-[#3070B3] hover:bg-[#3070B3]/90 text-white"
          onClick={handleSubmit}
          disabled={!selectedDisclaimerState}
        >
          TUM MGT Chatbot Signin
        </Button>
        <div className="flex items-center justify-center space-x-2 mt-4">
          <DisclaimerDialog />
        </div>
      </div>
    </div>
  );
}
