import type { Metadata } from "next";
import { AudioSettingsProvider } from "@/context/AudioSettingsContext";
import { SettingsButton } from "@/components/settings/SettingsButton";
import "./globals.css";

export const metadata: Metadata = {
  title: "peexh — Voice Communication Aid",
  description: "Personalized voice communication aid for people with dysarthria. Be understood.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased flex flex-col min-h-screen">
        <AudioSettingsProvider>
          <a href="#main-content" className="skip-link">
            Skip to main content
          </a>
          <header className="border-b border-surface-border bg-surface px-6 py-3.5">
            <div className="max-w-4xl mx-auto flex items-center justify-between">
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold tracking-tight text-foreground lowercase">
                  peexh
                </span>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-widest">
                  assistive voice
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-xs text-slate-500 hidden sm:inline" aria-label="System status">
                  Phase 7 Ready
                </span>
                <SettingsButton />
              </div>
            </div>
          </header>

          <main id="main-content" className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-8">
            {children}
          </main>

          <footer className="border-t border-surface-border bg-surface px-6 py-4 text-center text-xs text-slate-500">
            <div className="max-w-4xl mx-auto">
              peexh is a communication accessibility aid. LLM interprets, PEEXH decides, user controls.
            </div>
          </footer>
        </AudioSettingsProvider>
      </body>
    </html>
  );
}

