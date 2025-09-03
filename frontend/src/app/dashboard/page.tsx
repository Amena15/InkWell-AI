'use client';

import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { ThemeProvider } from 'next-themes';

export default function DashboardPage() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <DashboardLayout />
    </ThemeProvider>
  );
}
