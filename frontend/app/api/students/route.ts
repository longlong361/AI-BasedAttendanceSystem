import { NextResponse } from 'next/server';
import { supabaseClient } from '@/lib/supabase';

export async function GET() {
  try {
    const { data, error } = await supabaseClient
      .from('students')
      .select('id, student_code, name, class_name, school, status');

    if (error) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: 400 }
      );
    }

    if (!data) {
      return NextResponse.json(
        { success: true, data: [] },
        { status: 200 }
      );
    }

    return NextResponse.json(
      { success: true, data },
      { status: 200 }
    );
  } catch (err) {
    console.error("Supabase error:", err);
    return NextResponse.json(
      { success: false, error: err instanceof Error ? err.message : String(err) },
      { status: 500 }
    );
  }
}
