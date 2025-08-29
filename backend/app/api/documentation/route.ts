import { NextResponse } from 'next/server';
import { DocumentationAnalyzer } from '@/services/documentation/analyzer';

export async function POST(request: Request) {
  try {
    const { directoryPath } = await request.json();
    
    if (!directoryPath) {
      return NextResponse.json(
        { error: 'Directory path is required' },
        { status: 400 }
      );
    }

    const analyzer = new DocumentationAnalyzer();
    const issues = await analyzer.analyzeCodebase(directoryPath);
    
    // Generate a report
    const reportPath = join(process.cwd(), 'reports', `doc-report-${Date.now()}.json`);
    analyzer.generateReport(reportPath);

    return NextResponse.json({
      success: true,
      issues,
      reportPath
    });

  } catch (error) {
    console.error('Error analyzing documentation:', error);
    return NextResponse.json(
      { error: 'Failed to analyze documentation' },
      { status: 500 }
    );
  }
}
