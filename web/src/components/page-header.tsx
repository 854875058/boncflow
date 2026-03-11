import { PropsWithChildren } from 'react';

export function PageHeader({ children }: PropsWithChildren) {
  return (
    <header className="flex justify-between items-center bg-bg-base border-b border-border-button px-5 py-4 text-text-primary">
      {children}
    </header>
  );
}
