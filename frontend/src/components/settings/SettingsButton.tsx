"use client";

import React, { useState } from "react";
import { Settings as SettingsIcon } from "lucide-react";
import { SettingsPanel } from "@/components/settings/SettingsPanel";

interface SettingsButtonProps {
  activeProvider?: string | null;
}

export function SettingsButton({ activeProvider }: SettingsButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="rounded-full p-2.5 text-slate-500 hover:text-foreground hover:bg-surface-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary min-w-[48px] min-h-[48px] flex items-center justify-center border border-transparent hover:border-surface-border"
        aria-label="Open Audio & Runtime Settings"
        title="Audio & Runtime Settings"
      >
        <SettingsIcon className="w-5 h-5" aria-hidden="true" />
      </button>

      <SettingsPanel
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        activeProvider={activeProvider}
      />
    </>
  );
}
